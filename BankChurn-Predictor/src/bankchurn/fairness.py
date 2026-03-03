"""Fairness and bias audit module for BankChurn Predictor.

Computes group-level fairness metrics across protected attributes
(Gender, Geography) to detect disparate impact and equal opportunity
violations. Produces a structured report for CI/CD integration.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score

logger = logging.getLogger(__name__)

# Thresholds per the 4/5 (80%) rule for disparate impact
DISPARATE_IMPACT_THRESHOLD = 0.80
EQUAL_OPPORTUNITY_THRESHOLD = 0.80


def compute_group_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: Optional[np.ndarray] = None,
) -> Dict[str, float]:
    """Compute classification metrics for a single group.

    Parameters
    ----------
    y_true : array-like
        True binary labels.
    y_pred : array-like
        Predicted binary labels.
    y_prob : array-like, optional
        Predicted probabilities for the positive class.

    Returns
    -------
    Dict with accuracy, precision, recall, f1, positive_rate, and optionally auc.
    """
    n = len(y_true)
    if n == 0:
        return {}

    metrics: Dict[str, float] = {
        "n_samples": n,
        "positive_rate": float(y_pred.mean()),
        "base_rate": float(y_true.mean()),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "true_positive_rate": float(recall_score(y_true, y_pred, zero_division=0)),
        "false_positive_rate": float(np.sum((y_pred == 1) & (y_true == 0)) / max(np.sum(y_true == 0), 1)),
    }

    if y_prob is not None and len(np.unique(y_true)) > 1:
        metrics["auc"] = float(roc_auc_score(y_true, y_prob))

    return metrics


def compute_fairness_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive_features: pd.DataFrame,
    y_prob: Optional[np.ndarray] = None,
) -> Dict[str, Any]:
    """Compute fairness metrics across protected groups.

    For each sensitive attribute, computes:
    - Per-group classification metrics
    - Disparate Impact Ratio (positive_rate_min / positive_rate_max)
    - Equal Opportunity Difference (TPR gap between groups)
    - Demographic Parity Difference (positive_rate gap)

    Parameters
    ----------
    y_true : array-like
        True binary labels.
    y_pred : array-like
        Predicted binary labels.
    sensitive_features : DataFrame
        Columns are protected attributes (e.g., Gender, Geography).
    y_prob : array-like, optional
        Predicted probabilities for the positive class.

    Returns
    -------
    Dict with per-attribute fairness analysis.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    if y_prob is not None:
        y_prob = np.asarray(y_prob)

    report: Dict[str, Any] = {}

    for attr in sensitive_features.columns:
        groups = sensitive_features[attr].unique()
        group_metrics: Dict[str, Any] = {}

        for group in sorted(groups):
            mask = sensitive_features[attr].values == group
            gm = compute_group_metrics(
                y_true[mask],
                y_pred[mask],
                y_prob[mask] if y_prob is not None else None,
            )
            group_metrics[str(group)] = gm

        # Compute cross-group fairness indicators
        positive_rates = [gm["positive_rate"] for gm in group_metrics.values() if gm.get("positive_rate") is not None]
        tpr_values = [
            gm["true_positive_rate"] for gm in group_metrics.values() if gm.get("true_positive_rate") is not None
        ]
        fpr_values = [
            gm["false_positive_rate"] for gm in group_metrics.values() if gm.get("false_positive_rate") is not None
        ]

        fairness_indicators: Dict[str, Any] = {}

        if positive_rates and max(positive_rates) > 0:
            di_ratio = min(positive_rates) / max(positive_rates)
            fairness_indicators["disparate_impact_ratio"] = round(di_ratio, 4)
            fairness_indicators["disparate_impact_pass"] = di_ratio >= DISPARATE_IMPACT_THRESHOLD

        if tpr_values:
            eo_diff = max(tpr_values) - min(tpr_values)
            fairness_indicators["equal_opportunity_difference"] = round(eo_diff, 4)
            fairness_indicators["equal_opportunity_pass"] = 1.0 - eo_diff >= EQUAL_OPPORTUNITY_THRESHOLD

        if positive_rates:
            dp_diff = max(positive_rates) - min(positive_rates)
            fairness_indicators["demographic_parity_difference"] = round(dp_diff, 4)

        if fpr_values:
            fairness_indicators["equalized_odds_fpr_gap"] = round(max(fpr_values) - min(fpr_values), 4)

        report[attr] = {
            "groups": group_metrics,
            "fairness": fairness_indicators,
        }

    return report


def run_fairness_audit(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive_features: pd.DataFrame,
    y_prob: Optional[np.ndarray] = None,
    output_path: Optional[str | Path] = None,
) -> Dict[str, Any]:
    """Run a complete fairness audit and optionally save results.

    Parameters
    ----------
    y_true : array-like
        True binary labels.
    y_pred : array-like
        Predicted binary labels.
    sensitive_features : DataFrame
        Protected attribute columns.
    y_prob : array-like, optional
        Predicted probabilities.
    output_path : str or Path, optional
        Path to save JSON report.

    Returns
    -------
    Complete fairness audit report.
    """
    report = compute_fairness_metrics(y_true, y_pred, sensitive_features, y_prob)

    # Summary
    all_pass = True
    summary: List[str] = []
    for attr, data in report.items():
        fi = data.get("fairness", {})
        di_pass = fi.get("disparate_impact_pass", True)
        eo_pass = fi.get("equal_opportunity_pass", True)

        if not di_pass:
            all_pass = False
            summary.append(
                f"{attr}: FAIL disparate impact ({fi['disparate_impact_ratio']:.3f} < {DISPARATE_IMPACT_THRESHOLD})"
            )
        if not eo_pass:
            all_pass = False
            summary.append(f"{attr}: FAIL equal opportunity (gap={fi['equal_opportunity_difference']:.3f})")

    report["_summary"] = {
        "overall_pass": all_pass,
        "issues": summary if summary else ["No fairness violations detected"],
        "thresholds": {
            "disparate_impact": DISPARATE_IMPACT_THRESHOLD,
            "equal_opportunity": EQUAL_OPPORTUNITY_THRESHOLD,
        },
    }

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f"Fairness report saved to {output_path}")

    return report
