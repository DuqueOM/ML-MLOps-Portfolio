"""
SageMaker inference handler for BankChurn model.

SageMaker invokes these 4 functions automatically:
  model_fn()    -> load model from disk
  input_fn()    -> deserialize request body
  predict_fn()  -> run prediction
  output_fn()   -> serialize response

This script is packaged inside model.tar.gz alongside model.joblib.
"""

import json
import os

import joblib
import pandas as pd


def model_fn(model_dir: str):
    """Load the trained model from SageMaker model directory."""
    model_path = os.path.join(model_dir, "model.joblib")
    model = joblib.load(model_path)
    return model


def input_fn(request_body: str, request_content_type: str) -> pd.DataFrame:
    """Deserialize JSON request to DataFrame."""
    if request_content_type == "application/json":
        data = json.loads(request_body)
        if isinstance(data, list):
            return pd.DataFrame(data)
        return pd.DataFrame([data])
    raise ValueError(f"Unsupported content type: {request_content_type}")


def predict_fn(input_data: pd.DataFrame, model) -> dict:
    """Run prediction with probabilities."""
    proba = model.predict_proba(input_data)
    results = []
    for i in range(len(input_data)):
        p = float(proba[i][1])
        results.append(
            {
                "churn_probability": round(p, 4),
                "prediction": int(p > 0.5),
                "model_framework": "sagemaker-sklearn",
            }
        )
    if len(results) == 1:
        return results[0]
    return results


def output_fn(prediction, accept: str) -> tuple:
    """Serialize prediction to JSON."""
    return json.dumps(prediction), "application/json"
