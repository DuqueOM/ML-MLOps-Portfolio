"""Fairness and bias audit module for NLPInsight Analyzer.

Computes group-level classification metrics across sentiment classes
and text-length groups to detect disparate performance. Produces a
structured report for CI/CD integration.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

logger = logging.getLogger(__name__)

# Per-class metric floor: no class should have F1 below this fraction of the best class
CLASS_PARITY_THRESHOLD = 0.70


def compute_group_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[List[str]] = None,
) -> Dict[str, float]:
    """Compute classification metrics for a single group.

    Parameters
    ----------
    y_true : array-like
        True labels.
    y_pred : array-like
        Predicted labels.
    labels : list, optional
        All possible label values for consistent averaging.

    Returns
    -------
    Dict with n_samples, accuracy, precision, recall, f1.
    """
    n = len(y_true)
    if n == 0:
        return {}

    metrics: Dict[str, float] = {
        "n_samples": n,
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(precision_score(y_true, y_pred, average="macro", zero_division=0, labels=labels)),
        "recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0, labels=labels)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0, labels=labels)),
    }

    return metrics


def compute_per_class_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    labels: Optional[List[str]] = None,
) -> Dict[str, Dict[str, float]]:
    """Compute per-class precision, recall, F1.

    Parameters
    ----------
    y_true : array-like
        True labels.
    y_pred : array-like
        Predicted labels.
    labels : list, optional
        All possible label values.

    Returns
    -------
    Dict mapping class name to its metrics.
    """
    if labels is None:
        labels = sorted(set(y_true) | set(y_pred), key=str)

    result: Dict[str, Dict[str, float]] = {}
    for label in labels:
        mask_true = y_true == label
        mask_pred = y_pred == label
        tp = int(np.sum(mask_true & mask_pred))
        fp = int(np.sum(~mask_true & mask_pred))
        fn = int(np.sum(mask_true & ~mask_pred))

        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        f1 = 2 * precision * recall / max(precision + recall, 1e-9)

        result[str(label)] = {
            "n_samples": int(mask_true.sum()),
            "precision": round(float(precision), 4),
            "recall": round(float(recall), 4),
            "f1": round(float(f1), 4),
        }

    return result


def compute_fairness_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive_features: Optional[pd.DataFrame] = None,
    labels: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Compute fairness metrics for NLP classification.

    Analyzes:
    1. Per-class performance parity (F1 ratio between best and worst class)
    2. Group-level metrics across optional sensitive features (e.g., text_length_bin)

    Parameters
    ----------
    y_true : array-like
        True labels.
    y_pred : array-like
        Predicted labels.
    sensitive_features : DataFrame, optional
        Columns are grouping attributes (e.g., text_length_bin).
    labels : list, optional
        All possible label values.

    Returns
    -------
    Dict with per-class and per-group fairness analysis.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    if labels is None:
        labels = sorted(set(y_true) | set(y_pred), key=str)

    report: Dict[str, Any] = {}

    # 1. Per-class parity
    per_class = compute_per_class_metrics(y_true, y_pred, labels)
    f1_values = [m["f1"] for m in per_class.values() if m["n_samples"] > 0]

    class_parity: Dict[str, Any] = {"per_class": per_class}
    if len(f1_values) >= 2 and max(f1_values) > 0:
        f1_ratio = min(f1_values) / max(f1_values)
        class_parity["f1_parity_ratio"] = round(f1_ratio, 4)
        class_parity["f1_parity_pass"] = f1_ratio >= CLASS_PARITY_THRESHOLD

    report["class_parity"] = class_parity

    # 2. Group-level metrics (if sensitive features provided)
    if sensitive_features is not None:
        for attr in sensitive_features.columns:
            groups = sensitive_features[attr].unique()
            group_metrics: Dict[str, Any] = {}

            for group in sorted(groups, key=str):
                mask = sensitive_features[attr].values == group
                gm = compute_group_metrics(y_true[mask], y_pred[mask], labels)
                group_metrics[str(group)] = gm

            # Cross-group parity
            f1_vals = [gm["f1_macro"] for gm in group_metrics.values() if gm.get("f1_macro")]
            fairness_indicators: Dict[str, Any] = {}
            if f1_vals and max(f1_vals) > 0:
                ratio = min(f1_vals) / max(f1_vals)
                fairness_indicators["f1_parity_ratio"] = round(ratio, 4)
                fairness_indicators["f1_parity_pass"] = ratio >= CLASS_PARITY_THRESHOLD

            report[attr] = {
                "groups": group_metrics,
                "fairness": fairness_indicators,
            }

    return report


def run_fairness_audit(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive_features: Optional[pd.DataFrame] = None,
    labels: Optional[List[str]] = None,
    output_path: Optional[str | Path] = None,
) -> Dict[str, Any]:
    """Run a complete fairness audit and optionally save results.

    Parameters
    ----------
    y_true : array-like
        True labels.
    y_pred : array-like
        Predicted labels.
    sensitive_features : DataFrame, optional
        Protected attribute columns.
    labels : list, optional
        All possible label values.
    output_path : str or Path, optional
        Path to save JSON report.

    Returns
    -------
    Complete fairness audit report.
    """
    report = compute_fairness_metrics(y_true, y_pred, sensitive_features, labels)

    # Summary
    all_pass = True
    summary: List[str] = []

    cp = report.get("class_parity", {})
    if not cp.get("f1_parity_pass", True):
        all_pass = False
        summary.append(f"class_parity: FAIL F1 ratio ({cp['f1_parity_ratio']:.3f} < {CLASS_PARITY_THRESHOLD})")

    for attr, data in report.items():
        if attr.startswith("_") or attr == "class_parity":
            continue
        fi = data.get("fairness", {})
        if not fi.get("f1_parity_pass", True):
            all_pass = False
            summary.append(f"{attr}: FAIL F1 parity ({fi['f1_parity_ratio']:.3f} < {CLASS_PARITY_THRESHOLD})")

    report["_summary"] = {
        "overall_pass": all_pass,
        "issues": summary if summary else ["No fairness violations detected"],
        "thresholds": {
            "class_parity": CLASS_PARITY_THRESHOLD,
        },
    }

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f"Fairness report saved to {output_path}")

    return report
