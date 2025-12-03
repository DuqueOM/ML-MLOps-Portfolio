"""
CarVision Market Intelligence API

Features:
- Vehicle price prediction using RandomForest model
- Prometheus-compatible metrics endpoint
- Health checks for Kubernetes readiness/liveness
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, Response
from pydantic import BaseModel

# Prometheus metrics (optional dependency)
try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

    PROMETHEUS_AVAILABLE = True
    REQUEST_COUNT = Counter(
        "carvision_requests_total",
        "Total HTTP requests",
        ["method", "endpoint", "status"],
    )
    REQUEST_LATENCY = Histogram(
        "carvision_request_duration_seconds",
        "Request latency in seconds",
        ["endpoint"],
        buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
    )
except ImportError:
    PROMETHEUS_AVAILABLE = False

app = FastAPI(title="CarVision Inference API", version="1.0.0")
start_time = time.time()

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

        # Feature engineering is handled by the model pipeline.

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
    uptime = time.time() - start_time
    if not wrapper.model:
        return {"status": "unhealthy", "reason": "model_not_loaded", "uptime_seconds": uptime}
    return {"status": "ok", "uptime_seconds": uptime}


@app.get("/metrics")
async def metrics():
    """Prometheus-compatible metrics endpoint."""
    if PROMETHEUS_AVAILABLE:
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
    return {"error": "prometheus_client not installed"}


@app.post("/predict")
async def predict(features: VehicleFeatures):
    pred_start = time.time()
    try:
        pred = wrapper.predict(features.dict())
        latency = time.time() - pred_start

        if PROMETHEUS_AVAILABLE:
            REQUEST_COUNT.labels(method="POST", endpoint="/predict", status="200").inc()
            REQUEST_LATENCY.labels(endpoint="/predict").observe(latency)

        return {"prediction": pred}
    except Exception as e:
        if PROMETHEUS_AVAILABLE:
            REQUEST_COUNT.labels(method="POST", endpoint="/predict", status="500").inc()
        raise HTTPException(status_code=500, detail=str(e))
