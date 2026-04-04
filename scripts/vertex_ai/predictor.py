"""
Vertex AI Custom Prediction Routine for BankChurn model.

Vertex AI invokes the Predictor class automatically:
  __init__()     -> called once at container startup
  predict()      -> called for each prediction request
  postprocess()  -> optional, serialize response

This is the GCP equivalent of SageMaker's inference.py (4 functions).

References:
  https://cloud.google.com/vertex-ai/docs/predictions/custom-prediction-routines
"""

import json
import os
from typing import Any, Dict, List

import joblib
import pandas as pd


class BankChurnPredictor:
    """Vertex AI Custom Prediction Routine for BankChurn."""

    def __init__(self):
        """Load model from the Vertex AI model directory."""
        model_dir = os.environ.get("AIP_STORAGE_URI", "/tmp/model")  # nosec B108
        model_path = os.path.join(model_dir, "model.joblib")
        self._model = joblib.load(model_path)

    def predict(self, instances: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run prediction on a batch of instances.

        Args:
            instances: List of dicts, each with 10 BankChurn features.

        Returns:
            List of prediction dicts with churn_probability and prediction.
        """
        df = pd.DataFrame(instances)
        proba = self._model.predict_proba(df)

        results = []
        for i in range(len(df)):
            p = float(proba[i][1])
            results.append(
                {
                    "churn_probability": round(p, 4),
                    "prediction": int(p > 0.5),
                    "model_framework": "vertex-ai-sklearn",
                }
            )
        return results

    def postprocess(self, prediction: Dict[str, Any]) -> str:
        """Serialize prediction to JSON string."""
        return json.dumps(prediction)
