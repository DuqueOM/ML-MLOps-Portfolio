"""
Prediction logic.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np
import pandas as pd


def predict_price(payload: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, float]:
    """Predict car price from payload."""
    paths = config["paths"]

    # Load model
    model = joblib.load(paths["model_path"])

    # Load feature columns
    feat_path = Path(paths["artifacts_dir"]) / "feature_columns.json"
    if feat_path.exists():
        feature_columns = json.loads(Path(feat_path).read_text())
    else:
        # fallback
        pre = model.named_steps["pre"]
        feature_columns = list(pre.transformers_[0][2]) + list(pre.transformers_[1][2])

    df_in = pd.DataFrame([payload])

    # Feature engineering is now handled by the pipeline (FeatureEngineer step)
    # We just ensure raw columns are present if possible, or let alignment handle it.

    # Align columns
    # Note: feature_columns contains the columns expected by the Preprocessor (step 2).
    # Since the pipeline starts with FeatureEngineer (step 1), we should ideally
    # ensure RAW columns are present.
    # However, the current logic aligns to 'feature_columns' which includes derived features.
    # We fill them with NaN, and FeatureEngineer will populate them correctly
    # (assuming raw columns like 'model_year' and 'model' are in feature_columns or payload).

    for col in feature_columns:
        if col not in df_in.columns:
            df_in[col] = np.nan

    df_in = df_in[feature_columns]

    pred = model.predict(df_in)

    return {"prediction": float(pred[0])}
