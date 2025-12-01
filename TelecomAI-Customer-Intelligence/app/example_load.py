"""Example model loading and prediction script for TelecomAI.

This script demonstrates how to load the trained model and make predictions
outside of the FastAPI context.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

CANDIDATE_PATHS = [
    Path("models/model_v1.0.0.pkl"),
    Path("artifacts/model.joblib"),
]


def load_model():
    """Load model from the first available path."""
    for p in CANDIDATE_PATHS:
        if p.exists():
            return joblib.load(p)
    raise FileNotFoundError(f"No model found. Tried: {[str(p) for p in CANDIDATE_PATHS]}")


def demo_predict():
    """Run a demo prediction with sample data."""
    model = load_model()
    # Sample payload matching the expected features
    sample = pd.DataFrame(
        [
            {
                "calls": 40.0,
                "minutes": 311.9,
                "messages": 83.0,
                "mb_used": 19915.42,
            }
        ]
    )
    pred = int(model.predict(sample)[0])
    proba = model.predict_proba(sample)[0]
    print(
        {
            "prediction": pred,
            "plan": "ultra" if pred == 1 else "smart",
            "probability_ultra": float(proba[1]),
        }
    )


if __name__ == "__main__":
    demo_predict()
