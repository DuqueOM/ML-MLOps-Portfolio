from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.telecom.data import build_preprocessor, get_features_target, load_dataset
from src.telecom.evaluation import compute_classification_metrics


def test_load_dataset_raises_for_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.csv"
    with pytest.raises(FileNotFoundError):
        load_dataset(missing)


def test_get_features_target_success_and_missing_columns() -> None:
    df = pd.DataFrame(
        {
            "calls": [10, 20],
            "minutes": [100.0, 200.0],
            "messages": [5, 1],
            "mb_used": [1.0, 2.0],
            "is_ultra": [0, 1],
        }
    )
    features = ["calls", "minutes", "messages", "mb_used"]
    target = "is_ultra"

    X, y = get_features_target(df, features, target)
    assert list(X.columns) == features
    assert y.name == target
    assert len(X) == len(y) == 2

    df_missing = df.drop(columns=["messages"])
    with pytest.raises(ValueError):
        get_features_target(df_missing, features, target)


def test_build_preprocessor_transforms_numeric_features() -> None:
    df = pd.DataFrame(
        {
            "calls": [10, 20, np.nan],
            "minutes": [100.0, 200.0, 50.0],
        }
    )
    features = ["calls", "minutes"]
    preprocessor = build_preprocessor(features)

    transformed = preprocessor.fit_transform(df)
    assert transformed.shape[1] == len(features)
    assert not np.isnan(transformed).any()


def test_compute_classification_metrics_with_and_without_proba() -> None:
    y_true = np.array([0, 0, 1, 1])
    y_pred = np.array([0, 1, 1, 1])
    y_proba = np.array([0.1, 0.6, 0.4, 0.9])

    metrics_no_proba = compute_classification_metrics(y_true, y_pred)
    assert "accuracy" in metrics_no_proba
    assert "roc_auc" not in metrics_no_proba

    metrics_with_proba = compute_classification_metrics(y_true, y_pred, y_proba)
    assert "roc_auc" in metrics_with_proba
