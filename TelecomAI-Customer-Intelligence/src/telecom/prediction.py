"""
Prediction logic.
"""

from __future__ import annotations

import joblib
import pandas as pd


def predict_batch(input_csv: str, output_path: str, model_path: str, features: list) -> None:
    """Run batch prediction from CSV."""
    df = pd.read_csv(input_csv)

    # Load pipeline
    pipeline = joblib.load(model_path)

    # Validate columns
    missing = [c for c in features if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    preds = pipeline.predict(df[features])
    probas = pipeline.predict_proba(df[features])[:, 1] if hasattr(pipeline, "predict_proba") else None

    df["pred_is_ultra"] = preds
    if probas is not None:
        df["proba_is_ultra"] = probas

    df.to_csv(output_path, index=False)
