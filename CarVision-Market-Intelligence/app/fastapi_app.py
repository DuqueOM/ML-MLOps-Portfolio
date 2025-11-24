from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

# Use shared logic

app = FastAPI(title="CarVision Inference API", version="1.0.0")

MODEL_PATH = os.getenv("MODEL_PATH", "artifacts/model.joblib")
ARTIFACTS_DIR = Path(os.getenv("ARTIFACTS_DIR", "artifacts"))


class ModelWrapper:
    def __init__(self):
        self.model = None
        self.feature_columns = None

    def load(self):
        if not Path(MODEL_PATH).exists():
            return  # Handle gracefully or fail
        self.model = joblib.load(MODEL_PATH)
        feat_path = ARTIFACTS_DIR / "feature_columns.json"
        if feat_path.exists():
            self.feature_columns = json.loads(feat_path.read_text())
        else:
            # Fallback introspection
            try:
                pre = self.model.named_steps["pre"]
                self.feature_columns = list(pre.transformers_[0][2]) + list(pre.transformers_[1][2])
            except Exception:
                pass

    def predict(self, data: Dict[str, Any]) -> float:
        if not self.model:
            raise HTTPException(status_code=503, detail="Model not loaded")

        df = pd.DataFrame([data])

        # Feature engineering (consistent with training)
        # We can use clean_data but it filters out rows, which we don't want in inference necessarily.
        # Instead we replicate the feature creation logic or extract it.
        # For now, we replicate the critical transformations:
        if "model_year" in df.columns:
            current_year = pd.Timestamp.now().year
            df["vehicle_age"] = current_year - df["model_year"]

        if "model" in df.columns:
            df["brand"] = df["model"].astype(str).str.split().str[0]

        # Align columns
        if self.feature_columns:
            for col in self.feature_columns:
                if col not in df.columns:
                    df[col] = 0  # Neutral value for missing numeric/encoded
            df = df[self.feature_columns]

        return float(self.model.predict(df)[0])


wrapper = ModelWrapper()


class VehicleFeatures(BaseModel):
    model_year: int
    model: str
    condition: Optional[str] = "good"
    cylinders: Optional[float] = 4
    fuel: Optional[str] = "gas"
    odometer: Optional[float] = 0
    transmission: Optional[str] = "automatic"
    drive: Optional[str] = "fwd"
    type: Optional[str] = "sedan"
    paint_color: Optional[str] = "white"


@app.on_event("startup")
def load_model():
    wrapper.load()


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health():
    if not wrapper.model:
        return {"status": "unhealthy", "reason": "model_not_loaded"}
    return {"status": "ok"}


@app.post("/predict")
async def predict(features: VehicleFeatures):
    try:
        pred = wrapper.predict(features.dict())
        return {"prediction": pred}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
