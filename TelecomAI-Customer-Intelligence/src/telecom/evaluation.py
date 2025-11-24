"""
Evaluation logic.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import joblib
import numpy as np
import yaml
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split

from src.telecom.data import get_features_target, load_dataset

logger = logging.getLogger(__name__)


def compute_classification_metrics(
    y_true: np.ndarray, y_pred: np.ndarray, y_proba: Optional[np.ndarray] = None
) -> Dict[str, float]:
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }
    if y_proba is not None:
        try:
            metrics["roc_auc"] = float(roc_auc_score(y_true, y_proba))
        except ValueError:
            metrics["roc_auc"] = 0.0
    return metrics


def evaluate_model(cfg: Any) -> Dict[str, float]:
    logger.info("Starting evaluation...")

    df = load_dataset(cfg.paths["data_csv"])
    X, y = get_features_target(df, cfg.features, cfg.target)

    _, X_test, _, y_test = train_test_split(
        X,
        y,
        test_size=float(cfg.split.get("test_size", 0.2)),
        stratify=y if cfg.split.get("stratify", True) else None,
        random_state=int(cfg.random_seed),
    )

    # Load pipeline
    pipeline = joblib.load(cfg.paths["model_path"])

    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1] if hasattr(pipeline, "predict_proba") else None

    metrics = compute_classification_metrics(y_test.to_numpy(), y_pred, y_proba)
    logger.info("Evaluation done. Metrics: %s", metrics)

    # Save metrics
    with open(cfg.paths["metrics_path"], "w") as f:
        yaml.dump(metrics, f)

    return metrics
