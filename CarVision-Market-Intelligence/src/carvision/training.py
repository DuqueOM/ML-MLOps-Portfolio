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
from src.carvision.features import FeatureEngineer

logger = logging.getLogger(__name__)


def train_model(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Run training pipeline."""
    paths = cfg["paths"]
    tr = cfg["training"]
    prep = cfg["preprocessing"]

    Path(paths["artifacts_dir"]).mkdir(parents=True, exist_ok=True)

    # Load & clean data
    df = clean_data(load_data(paths["data_path"]), filters=prep.get("filters"))

    # Feature engineering for inferring types (since FeatureEngineer is part of pipeline,
    # we need to know what features WILL be produced if we want to be strict, but
    # infer_feature_types usually runs on raw dataframe.
    # However, FeatureEngineer produces 'vehicle_age' etc.
    # So we should probably run FeatureEngineer on the df temporarily to infer types
    # OR we assume FeatureEngineer is part of the pipeline and we infer on raw data + added cols?
    #
    # The previous code ran clean_data which ADDED columns. Now clean_data does NOT add columns.
    # So infer_feature_types will miss 'vehicle_age', 'brand', 'price_per_mile'.
    # We must manually add these or run a temporary transform.

    # Let's create the engineer and transform df temporarily for type inference and splitting.
    # Wait, if we transform for splitting, we should pass transformed data to the pipeline?
    # NO, the pipeline expects raw data.

    # BUT, if we split on raw data, we are fine.
    # The issue is infer_feature_types needs to know about 'vehicle_age' etc if they are to be used.
    # And build_preprocessor needs to know about them.

    # If we put FeatureEngineer in the pipeline, the pipeline input is raw data.
    # The FeatureEngineer output is data with new columns.
    # The ColumnTransformer (pre) comes AFTER FeatureEngineer.
    # So ColumnTransformer MUST be configured with the columns that exist AFTER FeatureEngineer.

    # So we MUST run FeatureEngineer once to get the column names/types.

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

    # Split on RAW data (or transformed? Pipeline expects raw usually).
    # If we want the pipeline to be end-to-end callable with raw data, we should split on RAW data.
    # But then we need to be careful that 'pre' (ColumnTransformer) is applied to output of 'features'.

    X_train, X_val, X_test, y_train, y_val, y_test, split_indices = split_data(
        df,  # Split raw df
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

    # Model
    if tr.get("model") == "random_forest":
        rf_params = tr.get("random_forest_params", {})
        # ensure reproducibility
        if "random_state" not in rf_params:
            rf_params["random_state"] = cfg["seed"]
        model = RandomForestRegressor(**rf_params)
    else:
        raise NotImplementedError(f"Modelo no soportado: {tr.get('model')}")

    # Pipeline: features -> pre -> model
    # Note: FeatureEngineer returns a DF, so 'pre' (ColumnTransformer) can take it.
    pipe = Pipeline(steps=[("features", fe), ("pre", pre), ("model", model)])

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
