"""
Training pipeline logic.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline

from src.carvision.data import (
    build_preprocessor,
    clean_data,
    infer_feature_types,
    load_data,
    save_split_indices,
    split_data,
)
from src.carvision.evaluation import rmse

logger = logging.getLogger(__name__)


def train_model(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Run training pipeline."""
    paths = cfg["paths"]
    tr = cfg["training"]
    prep = cfg["preprocessing"]

    Path(paths["artifacts_dir"]).mkdir(parents=True, exist_ok=True)

    # Load & clean data
    df = clean_data(load_data(paths["data_path"]))

    # Infer features
    num_cols, cat_cols = infer_feature_types(
        df,
        target=tr["target"],
        numeric_features=prep.get("numeric_features"),
        categorical_features=prep.get("categorical_features"),
        drop_columns=prep.get("drop_columns"),
    )

    # Split
    X_train, X_val, X_test, y_train, y_val, y_test, split_indices = split_data(
        df,
        target=tr["target"],
        test_size=tr["test_size"],
        val_size=tr["val_size"],
        seed=cfg["seed"],
        shuffle=tr["shuffle"],
    )
    save_split_indices(split_indices, paths["split_indices_path"])

    # Preprocessor
    pre = build_preprocessor(
        num_cols,
        cat_cols,
        numeric_imputer=prep.get("numeric_imputer", "median"),
        categorical_imputer=prep.get("categorical_imputer", "most_frequent"),
        scale_numeric=prep.get("scale_numeric", True),
        handle_unknown=prep.get("handle_unknown_category", "ignore"),
    )

    # Model
    if tr.get("model") == "random_forest":
        rf_params = tr.get("random_forest_params", {})
        # ensure reproducibility
        if "random_state" not in rf_params:
            rf_params["random_state"] = cfg["seed"]
        model = RandomForestRegressor(**rf_params)
    else:
        raise NotImplementedError(f"Modelo no soportado: {tr.get('model')}")

    pipe = Pipeline(steps=[("pre", pre), ("model", model)])
    logger.info("Entrenando modelo...")
    pipe.fit(X_train, y_train)

    # Validation metrics
    yv = pipe.predict(X_val)
    val_metrics = {
        "rmse": rmse(y_val, yv),
        "mae": float(mean_absolute_error(y_val, yv)),
        "mape": float(np.mean(np.abs((np.array(y_val) - yv) / (np.array(y_val) + 1e-8))) * 100),
        "r2": float(r2_score(y_val, yv)),
    }
    logger.info(f"Métricas de validación: {val_metrics}")

    # Persist artifacts
    joblib.dump(pipe, paths["model_path"])

    # Export a copy for demo loading (legacy support)
    Path("models").mkdir(exist_ok=True)
    joblib.dump(pipe, "models/model_v1.0.0.pkl")

    feature_columns = sorted(num_cols + cat_cols)
    with open(Path(paths["artifacts_dir"]) / "feature_columns.json", "w") as f:
        json.dump(feature_columns, f, indent=2)
    with open(Path(paths["artifacts_dir"]) / "metrics_val.json", "w") as f:
        json.dump(val_metrics, f, indent=2)

    return {
        "val_metrics": val_metrics,
        "model_path": paths["model_path"],
        "feature_columns": feature_columns,
    }
