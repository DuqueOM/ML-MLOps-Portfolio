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

    data_csv_abs = project_root / cfg.paths["data_csv"]
    artifacts_dir = tmp_path / "artifacts"
    models_dir = tmp_path / "models"

    cfg.paths = {
        **cfg.paths,
        "data_csv": str(data_csv_abs),
        "artifacts_dir": str(artifacts_dir),
        "model_path": str(artifacts_dir / "model.joblib"),
        "metrics_path": str(artifacts_dir / "metrics.json"),
        "confusion_matrix_path": str(artifacts_dir / "confusion_matrix.png"),
        "roc_curve_path": str(artifacts_dir / "roc_curve.png"),
        "model_export_path": str(models_dir / "model_v1.0.0.pkl"),
    }
    cfg.mlflow = None
    return cfg


def test_train_and_evaluate_end_to_end(tmp_path: Path) -> None:
    cfg = make_isolated_config(tmp_path)

    metrics = train_model(cfg)
    assert "accuracy" in metrics

    paths = cfg.paths
    assert Path(paths["model_path"]).exists()
    # preprocessor is now inside the model pipeline

    metrics_eval = evaluate_model(cfg)
    assert "accuracy" in metrics_eval
    assert Path(paths["metrics_path"]).exists()


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
    predict_batch(str(input_csv), str(output_csv), cfg.paths["model_path"], cfg.features)

    assert output_csv.exists()
    out_df = pd.read_csv(output_csv)
    assert "pred_is_ultra" in out_df.columns
    assert "proba_is_ultra" in out_df.columns


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
            cfg.paths["model_path"],
            cfg.features,
        )
