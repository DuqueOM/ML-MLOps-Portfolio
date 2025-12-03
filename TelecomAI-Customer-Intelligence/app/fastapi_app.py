"""
TelecomAI Customer Intelligence API

Features:
- Plan recommendation prediction (Standard vs Ultra)
- Prometheus-compatible metrics endpoint
- Health checks for Kubernetes readiness/liveness
"""

from __future__ import annotations

import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, Response
from pydantic import BaseModel, Field

# Prometheus metrics (optional dependency)
try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

    PROMETHEUS_AVAILABLE = True
    REQUEST_COUNT = Counter(
        "telecom_requests_total",
        "Total HTTP requests",
        ["method", "endpoint", "status"],
    )
    REQUEST_LATENCY = Histogram(
        "telecom_request_duration_seconds",
        "Request latency in seconds",
        ["endpoint"],
        buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
    )
except ImportError:
    PROMETHEUS_AVAILABLE = False

APP_TITLE = "TelecomAI Inference API"
MODEL_PATH = os.getenv("MODEL_PATH", "artifacts/model.joblib")
start_time = time.time()

ml_models = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    if not Path(MODEL_PATH).exists():
        # Warn but don't crash, might be a build phase
        print(f"WARNING: Model not found at {MODEL_PATH}")
    else:
        ml_models["pipeline"] = joblib.load(MODEL_PATH)
    yield
    ml_models.clear()


app = FastAPI(title=APP_TITLE, lifespan=lifespan)


class TelecomFeatures(BaseModel):
    calls: float = Field(..., ge=0)
    minutes: float = Field(..., ge=0)
    messages: float = Field(..., ge=0)
    mb_used: float = Field(..., ge=0)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health() -> dict:
    uptime = time.time() - start_time
    pipeline = ml_models.get("pipeline")
    return {
        "status": "ok" if pipeline else "degraded",
        "model_loaded": pipeline is not None,
        "uptime_seconds": uptime,
    }


@app.get("/metrics")
async def metrics():
    """Prometheus-compatible metrics endpoint."""
    if PROMETHEUS_AVAILABLE:
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
    return {"error": "prometheus_client not installed"}


@app.post("/predict")
async def predict(features: TelecomFeatures) -> dict:
    pred_start = time.time()
    pipeline = ml_models.get("pipeline")
    if not pipeline:
        if PROMETHEUS_AVAILABLE:
            REQUEST_COUNT.labels(method="POST", endpoint="/predict", status="503").inc()
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # pydantic v2 compatibility
        data_dict = features.model_dump() if hasattr(features, "model_dump") else features.dict()
        df = pd.DataFrame([data_dict])
        proba = None
        if hasattr(pipeline, "predict_proba"):
            proba = float(pipeline.predict_proba(df)[0, 1])
        pred = int(pipeline.predict(df)[0])

        latency = time.time() - pred_start
        if PROMETHEUS_AVAILABLE:
            REQUEST_COUNT.labels(method="POST", endpoint="/predict", status="200").inc()
            REQUEST_LATENCY.labels(endpoint="/predict").observe(latency)

        return {
            "prediction": pred,
            "probability_is_ultra": proba,
        }
    except Exception as e:
        if PROMETHEUS_AVAILABLE:
            REQUEST_COUNT.labels(method="POST", endpoint="/predict", status="500").inc()
        raise HTTPException(status_code=500, detail=str(e))
