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
from src.carvision.features import FeatureEngineer
from src.carvision.models_advanced import build_model, get_available_models

logger = logging.getLogger(__name__)


def train_model(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Run training pipeline."""
    paths = cfg["paths"]
    tr = cfg["training"]
    prep = cfg["preprocessing"]

    Path(paths["artifacts_dir"]).mkdir(parents=True, exist_ok=True)

    # Load & clean data
    df = clean_data(load_data(paths["data_path"]), filters=prep.get("filters"))

    # Run FeatureEngineer once to infer column types for the ColumnTransformer,
    # which operates on FeatureEngineer output inside the pipeline.
    dataset_year = cfg.get("dataset_year", 2024)
    fe = FeatureEngineer(current_year=dataset_year)
    df_transformed = fe.transform(df)

    # Infer features on transformed data
    num_cols, cat_cols = infer_feature_types(
        df_transformed,
        target=tr["target"],
        numeric_features=prep.get("numeric_features"),
        categorical_features=prep.get("categorical_features"),
        drop_columns=prep.get("drop_columns"),
    )

    # Split raw data — pipeline handles FeatureEngineer → ColumnTransformer internally
    X_train, X_val, X_test, y_train, y_val, y_test, split_indices = split_data(
        df,
        target=tr["target"],
        test_size=tr["test_size"],
        val_size=tr["val_size"],
        seed=cfg["seed"],
        shuffle=tr["shuffle"],
    )
    save_split_indices(split_indices, paths["split_indices_path"])

    # Preprocessor (configured with inferred columns from transformed data)
    pre = build_preprocessor(
        num_cols,
        cat_cols,
        numeric_imputer=prep.get("numeric_imputer", "median"),
        categorical_imputer=prep.get("categorical_imputer", "most_frequent"),
        scale_numeric=prep.get("scale_numeric", True),
        handle_unknown=prep.get("handle_unknown_category", "ignore"),
    )

    # Build model via factory
    model_name = tr.get("model", "random_forest")
    model_params = tr.get(f"{model_name}_params", tr.get("random_forest_params", {}))
    if "random_state" not in model_params:
        model_params["random_state"] = cfg["seed"]
    model = build_model(model_name, params=model_params, seed=cfg["seed"])

    # Pipeline: features -> pre -> model
    pipe = Pipeline(steps=[("features", fe), ("pre", pre), ("model", model)])

    logger.info(f"Training model: {model_name}")
    pipe.fit(X_train, y_train)

    # Validation metrics
    yv = pipe.predict(X_val)
    y_val_arr = np.asarray(y_val)
    val_metrics = {
        "model": model_name,
        "rmse": rmse(y_val, yv),
        "mae": float(mean_absolute_error(y_val, yv)),
        "mape": float(np.mean(np.abs((y_val_arr - yv) / np.maximum(y_val_arr, 1e-8))) * 100),
        "r2": float(r2_score(y_val, yv)),
    }
    logger.info(f"Validation metrics ({model_name}): {val_metrics}")

    # Model comparison if configured
    compare_list = tr.get("compare_models", [])
    comparison_results = {}
    if compare_list:
        available = get_available_models()
        for cmp_name in compare_list:
            if not available.get(cmp_name, False):
                logger.warning(f"Model '{cmp_name}' not available, skipping")
                continue
            try:
                cmp_params = tr.get(f"{cmp_name}_params", {})
                if "random_state" not in cmp_params:
                    cmp_params["random_state"] = cfg["seed"]
                cmp_model = build_model(cmp_name, params=cmp_params, seed=cfg["seed"])
                cmp_pipe = Pipeline(
                    steps=[("features", FeatureEngineer(current_year=dataset_year)), ("pre", pre), ("model", cmp_model)]
                )
                cmp_pipe.fit(X_train, y_train)
                cmp_preds = cmp_pipe.predict(X_val)
                cmp_metrics = {
                    "rmse": rmse(y_val, cmp_preds),
                    "mae": float(mean_absolute_error(y_val, cmp_preds)),
                    "r2": float(r2_score(y_val, cmp_preds)),
                }
                comparison_results[cmp_name] = cmp_metrics
                logger.info(f"  {cmp_name}: RMSE={cmp_metrics['rmse']:.2f}, R2={cmp_metrics['r2']:.4f}")
            except Exception as e:
                logger.error(f"  {cmp_name} failed: {e}")
                comparison_results[cmp_name] = {"error": str(e)}

    # Persist artifacts
    model_path = Path(paths["model_path"])
    joblib.dump(pipe, model_path, compress=3)
    size_mb = model_path.stat().st_size / (1024 * 1024)
    logger.info(f"Model saved to {model_path} ({size_mb:.2f} MB)")

    legacy_path = Path("models/model_v1.0.0.pkl")
    if legacy_path.resolve() != model_path.resolve():
        legacy_path.parent.mkdir(exist_ok=True)
        joblib.dump(pipe, legacy_path, compress=3)

    feature_columns = sorted(num_cols + cat_cols)
    artifacts_dir = Path(paths["artifacts_dir"])
    with open(artifacts_dir / "feature_columns.json", "w") as f:
        json.dump(feature_columns, f, indent=2)
    with open(artifacts_dir / "metrics_val.json", "w") as f:
        json.dump(val_metrics, f, indent=2)
    if comparison_results:
        with open(artifacts_dir / "model_comparison.json", "w") as f:
            json.dump(comparison_results, f, indent=2)

    return {
        "val_metrics": val_metrics,
        "model_path": paths["model_path"],
        "feature_columns": feature_columns,
        "comparison": comparison_results,
    }
