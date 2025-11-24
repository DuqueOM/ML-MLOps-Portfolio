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

    # Basic feature engineering required for inference
    if "model_year" in df_in.columns:
        current_year = pd.Timestamp.now().year
        df_in["vehicle_age"] = current_year - df_in["model_year"]

    if "model" in df_in.columns and "brand" in feature_columns:
        df_in["brand"] = df_in["model"].astype(str).str.split().str[0]

    # Align columns
    for col in feature_columns:
        if col not in df_in.columns:
            df_in[col] = np.nan

    df_in = df_in[feature_columns]

    pred = model.predict(df_in)

    return {"prediction": float(pred[0])}
