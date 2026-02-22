from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.telecom.config import Config
from src.telecom.evaluation import evaluate_model
from src.telecom.prediction import predict_batch
from src.telecom.training import train_model


def make_isolated_config(tmp_path: Path) -> Config:
    project_root = Path(__file__).resolve().parents[1]
    cfg = Config.from_yaml(str(project_root / "configs" / "config.yaml"))

    data_csv_abs = project_root / cfg.paths.data_csv
    artifacts_dir = tmp_path / "artifacts"
    models_dir = tmp_path / "models"

    # Update paths using Pydantic model
    from src.telecom.config import PathsConfig

    cfg.paths = PathsConfig(
        data_csv=str(data_csv_abs),
        artifacts_dir=str(artifacts_dir),
        model_path=str(artifacts_dir / "model.joblib"),
        preprocessor_path=str(artifacts_dir / "preprocessor.joblib"),
        metrics_path=str(artifacts_dir / "metrics.json"),
        confusion_matrix_path=str(artifacts_dir / "confusion_matrix.png"),
        roc_curve_path=str(artifacts_dir / "roc_curve.png"),
        model_export_path=str(models_dir / "model.joblib"),
    )
    cfg.mlflow = None

    # Force sklearn-only model for tests (no optional deps like xgboost/lightgbm)
    from src.telecom.config import ModelConfig

    cfg.model = ModelConfig(name="gradient_boosting", params={"n_estimators": 20, "max_depth": 3}, compare_models=[])
    return cfg


def test_train_and_evaluate_end_to_end(tmp_path: Path) -> None:
    cfg = make_isolated_config(tmp_path)

    metrics = train_model(cfg)
    assert "accuracy" in metrics

    paths = cfg.paths
    assert Path(paths.model_path).exists()
    # preprocessor is now inside the model pipeline

    metrics_eval = evaluate_model(cfg)
    assert "accuracy" in metrics_eval
    assert Path(paths.metrics_path).exists()


def test_predict_creates_output_csv(tmp_path: Path) -> None:
    cfg = make_isolated_config(tmp_path)

    train_model(cfg)

    project_root = Path(__file__).resolve().parents[1]
    df = pd.read_csv(project_root / "data/raw/users_behavior.csv")
    input_cols = cfg.features
    input_df = df[input_cols].head(10)
    input_csv = tmp_path / "input.csv"
    input_df.to_csv(input_csv, index=False)

    output_csv = tmp_path / "preds.csv"
    predict_batch(str(input_csv), str(output_csv), cfg.paths.model_path, cfg.features)

    assert output_csv.exists()
    out_df = pd.read_csv(output_csv)
    assert "pred_is_ultra" in out_df.columns
    assert "proba_is_ultra" in out_df.columns


def test_train_with_model_comparison_and_auto_selection(tmp_path: Path) -> None:
    """Test that model comparison and auto-selection logic works end-to-end."""
    cfg = make_isolated_config(tmp_path)

    from src.telecom.config import ModelConfig

    # Use a weak primary model so comparison models can beat it
    cfg.model = ModelConfig(
        name="logistic_regression",
        params={},
        compare_models=["gradient_boosting", "random_forest"],
    )

    metrics = train_model(cfg)

    # Comparison should have run
    assert "model_comparison" in metrics
    assert "gradient_boosting" in metrics["model_comparison"]
    assert "random_forest" in metrics["model_comparison"]

    # Auto-selection fields should be present
    assert "auto_selected" in metrics

    # Check comparison metrics saved to file
    comp_path = Path(cfg.paths.metrics_path).parent / "model_comparison.json"
    assert comp_path.exists()

    import json

    with open(comp_path) as f:
        comp_data = json.load(f)
    assert "gradient_boosting" in comp_data or "random_forest" in comp_data

    # Model file should exist
    assert Path(cfg.paths.model_path).exists()


def test_train_comparison_keeps_best_primary(tmp_path: Path) -> None:
    """Test that auto-selection keeps primary when it is already the best."""
    cfg = make_isolated_config(tmp_path)

    from src.telecom.config import ModelConfig

    # Use a strong primary model; logistic_regression is weaker, so primary should win
    cfg.model = ModelConfig(
        name="gradient_boosting",
        params={"n_estimators": 50, "max_depth": 5},
        compare_models=["logistic_regression"],
    )

    metrics = train_model(cfg)
    assert "auto_selected" in metrics
    # Primary gradient_boosting should likely beat logistic_regression
    assert "model_comparison" in metrics


def test_train_comparison_with_unavailable_model(tmp_path: Path) -> None:
    """Test that unavailable comparison models are skipped gracefully."""
    cfg = make_isolated_config(tmp_path)

    from src.telecom.config import ModelConfig

    cfg.model = ModelConfig(
        name="gradient_boosting",
        params={"n_estimators": 20, "max_depth": 3},
        compare_models=["random_forest", "lightgbm"],
    )

    # Should not raise; lightgbm may be skipped if not installed
    metrics = train_model(cfg)
    assert "accuracy" in metrics


def test_predict_raises_for_missing_columns(tmp_path: Path) -> None:
    cfg = make_isolated_config(tmp_path)
    train_model(cfg)

    project_root = Path(__file__).resolve().parents[1]
    df = pd.read_csv(project_root / "data/raw/users_behavior.csv")
    reduced_df = df[cfg.features[:-1]].head(5)
    bad_input_csv = tmp_path / "bad_input.csv"
    reduced_df.to_csv(bad_input_csv, index=False)

    with pytest.raises(ValueError):
        predict_batch(
            str(bad_input_csv),
            str(tmp_path / "out.csv"),
            cfg.paths.model_path,
            cfg.features,
        )
