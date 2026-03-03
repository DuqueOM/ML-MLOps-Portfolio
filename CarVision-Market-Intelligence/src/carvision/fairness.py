"""Fairness and bias audit module for CarVision Market Intelligence.

Computes group-level regression error metrics across protected attributes
(fuel type, manufacturer) to detect disparate error rates.
Produces a structured report for CI/CD integration.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Error ratio threshold: worst group MAE should not exceed 1.25× the best group
ERROR_RATIO_THRESHOLD = 1.25


def compute_group_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> Dict[str, float]:
    """Compute regression error metrics for a single group.

    Parameters
    ----------
    y_true : array-like
        True target values.
    y_pred : array-like
        Predicted target values.

    Returns
    -------
    Dict with n_samples, mae, rmse, mape, mean_error (signed).
    """
    n = len(y_true)
    if n == 0:
        return {}

    errors = y_true - y_pred
    abs_errors = np.abs(errors)

    metrics: Dict[str, float] = {
        "n_samples": n,
        "mae": float(np.mean(abs_errors)),
        "rmse": float(np.sqrt(np.mean(errors**2))),
        "mean_error": float(np.mean(errors)),
        "median_absolute_error": float(np.median(abs_errors)),
    }

    # MAPE — only where y_true != 0
    nonzero_mask = y_true != 0
    if nonzero_mask.any():
        metrics["mape"] = float(np.mean(np.abs(errors[nonzero_mask] / y_true[nonzero_mask])))
    else:
        metrics["mape"] = float("nan")

    return metrics


def compute_fairness_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive_features: pd.DataFrame,
) -> Dict[str, Any]:
    """Compute fairness metrics across protected groups for regression.

    For each sensitive attribute, computes:
    - Per-group regression error metrics (MAE, RMSE, MAPE)
    - Error Ratio (worst_group_MAE / best_group_MAE)
    - Mean Error Spread (max signed error gap between groups)

    Parameters
    ----------
    y_true : array-like
        True target values.
    y_pred : array-like
        Predicted target values.
    sensitive_features : DataFrame
        Columns are protected attributes (e.g., fuel, manufacturer).

    Returns
    -------
    Dict with per-attribute fairness analysis.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    report: Dict[str, Any] = {}

    for attr in sensitive_features.columns:
        groups = sensitive_features[attr].unique()
        group_metrics: Dict[str, Any] = {}

        for group in sorted(groups, key=str):
            mask = sensitive_features[attr].values == group
            gm = compute_group_metrics(y_true[mask], y_pred[mask])
            group_metrics[str(group)] = gm

        # Cross-group fairness indicators
        mae_values = [gm["mae"] for gm in group_metrics.values() if gm.get("mae") is not None]
        mean_errors = [gm["mean_error"] for gm in group_metrics.values() if gm.get("mean_error") is not None]

        fairness_indicators: Dict[str, Any] = {}

        if mae_values:
            best_mae = min(mae_values)
            worst_mae = max(mae_values)
            if best_mae > 0:
                error_ratio = worst_mae / best_mae
            else:
                # One group has perfect predictions → ratio is infinite if worst > 0
                error_ratio = float("inf") if worst_mae > 0 else 1.0
            fairness_indicators["error_ratio"] = round(error_ratio, 4) if np.isfinite(error_ratio) else 999.0
            fairness_indicators["error_ratio_pass"] = error_ratio <= ERROR_RATIO_THRESHOLD
            fairness_indicators["best_group_mae"] = round(best_mae, 2)
            fairness_indicators["worst_group_mae"] = round(worst_mae, 2)

        if mean_errors:
            spread = max(mean_errors) - min(mean_errors)
            fairness_indicators["mean_error_spread"] = round(spread, 2)

        report[attr] = {
            "groups": group_metrics,
            "fairness": fairness_indicators,
        }

    return report


def run_fairness_audit(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sensitive_features: pd.DataFrame,
    output_path: Optional[str | Path] = None,
) -> Dict[str, Any]:
    """Run a complete fairness audit and optionally save results.

    Parameters
    ----------
    y_true : array-like
        True target values.
    y_pred : array-like
        Predicted target values.
    sensitive_features : DataFrame
        Protected attribute columns.
    output_path : str or Path, optional
        Path to save JSON report.

    Returns
    -------
    Complete fairness audit report.
    """
    report = compute_fairness_metrics(y_true, y_pred, sensitive_features)

    # Summary
    all_pass = True
    summary: List[str] = []
    for attr, data in report.items():
        fi = data.get("fairness", {})
        er_pass = fi.get("error_ratio_pass", True)

        if not er_pass:
            all_pass = False
            summary.append(f"{attr}: FAIL error ratio ({fi['error_ratio']:.3f} > {ERROR_RATIO_THRESHOLD})")

    report["_summary"] = {
        "overall_pass": all_pass,
        "issues": summary if summary else ["No fairness violations detected"],
        "thresholds": {
            "error_ratio": ERROR_RATIO_THRESHOLD,
        },
    }

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f"Fairness report saved to {output_path}")

    return report
