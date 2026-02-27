"""
TelecomAI Customer Intelligence API

Features:
- Plan recommendation prediction (Standard vs Ultra)
- Batch prediction support (up to 500 customers)
- Feature importance explainability
- Prometheus-compatible metrics endpoint
- Health checks for Kubernetes readiness/liveness
"""

from __future__ import annotations

import logging
import os
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, Response
from pydantic import BaseModel, Field, field_validator

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
    PREDICTION_COUNT = Counter(
        "telecom_predictions_total",
        "Total predictions made",
        ["plan"],
    )
except ImportError:
    PROMETHEUS_AVAILABLE = False

# Add repo root to path for common_utils imports
BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from common_utils.model_persistence import load_model
except ImportError:
    import joblib

    def load_model(path, **kwargs):
        return joblib.load(path)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "models" / "model.joblib"))
FEATURE_NAMES = ["calls", "minutes", "messages", "mb_used"]
start_time = time.time()

# Global state
pipeline = None


def _get_feature_importance() -> Dict[str, float]:
    """Extract feature importance from the trained pipeline."""
    if pipeline is None:
        return {}
    try:
        clf = pipeline.named_steps.get("clf") or pipeline[-1]
        if hasattr(clf, "feature_importances_"):
            importances = clf.feature_importances_
        elif hasattr(clf, "coef_"):
            importances = np.abs(clf.coef_[0]) if clf.coef_.ndim > 1 else np.abs(clf.coef_)
        else:
            return {}
        return {name: round(float(imp), 4) for name, imp in zip(FEATURE_NAMES, importances)}
    except Exception:
        return {}


def load_model_logic() -> bool:
    """Load model pipeline."""
    global pipeline
    model_path = Path(MODEL_PATH)
    if not model_path.exists():
        logger.error(f"Model not found: {model_path}")
        return False
    try:
        pipeline = load_model(model_path)
        logger.info(f"Model loaded from {model_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to load model from {model_path}: {e}")
        return False


@asynccontextmanager
async def lifespan(application: FastAPI):
    success = load_model_logic()
    if not success:
        logger.warning("Application started without model loaded.")
    yield


app = FastAPI(title="TelecomAI Inference API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TelecomFeatures(BaseModel):
    calls: float = Field(..., ge=0, description="Number of calls")
    minutes: float = Field(..., ge=0, description="Total minutes")
    messages: float = Field(..., ge=0, description="Number of messages")
    mb_used: float = Field(..., ge=0, description="Mobile data used (MB)")


class BatchTelecomData(BaseModel):
    """Schema for batch prediction."""

    customers: List[TelecomFeatures]

    @field_validator("customers")
    @classmethod
    def validate_batch_size(cls, v: list) -> list:
        if len(v) > 500:
            raise ValueError("Max 500 customers per batch")
        if len(v) == 0:
            raise ValueError("Must include at least one customer")
        return v


class PredictionResponse(BaseModel):
    prediction: int
    plan: str
    probability_is_ultra: Optional[float] = None
    feature_importance: Dict[str, float] = Field(default_factory=dict)
    prediction_timestamp: str


class BatchPredictionResponse(BaseModel):
    predictions: List[PredictionResponse]
    batch_id: str
    total_customers: int
    processing_time_seconds: float


def _predict_one(data_dict: Dict[str, Any]) -> PredictionResponse:
    """Run prediction for a single customer."""
    df = pd.DataFrame([data_dict])
    pred = int(pipeline.predict(df)[0])
    proba = None
    if hasattr(pipeline, "predict_proba"):
        proba = round(float(pipeline.predict_proba(df)[0, 1]), 4)
    plan = "Ultra" if pred == 1 else "Standard"
    return PredictionResponse(
        prediction=pred,
        plan=plan,
        probability_is_ultra=proba,
        feature_importance=_get_feature_importance(),
        prediction_timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
    )


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health() -> dict:
    uptime = time.time() - start_time
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


@app.post("/predict", response_model=PredictionResponse)
async def predict(features: TelecomFeatures):
    pred_start = time.time()
    if pipeline is None:
        if PROMETHEUS_AVAILABLE:
            REQUEST_COUNT.labels(method="POST", endpoint="/predict", status="503").inc()
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        result = _predict_one(features.model_dump())
        latency = time.time() - pred_start

        if PROMETHEUS_AVAILABLE:
            REQUEST_COUNT.labels(method="POST", endpoint="/predict", status="200").inc()
            REQUEST_LATENCY.labels(endpoint="/predict").observe(latency)
            PREDICTION_COUNT.labels(plan=result.plan).inc()

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        if PROMETHEUS_AVAILABLE:
            REQUEST_COUNT.labels(method="POST", endpoint="/predict", status="500").inc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict_batch", response_model=BatchPredictionResponse)
async def predict_batch(batch_data: BatchTelecomData):
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    start_batch = time.time()
    batch_id = f"batch_{int(start_batch)}"

    try:
        customers_list = [c.model_dump() for c in batch_data.customers]
        df = pd.DataFrame(customers_list)
        preds = pipeline.predict(df)
        probas = None
        if hasattr(pipeline, "predict_proba"):
            probas = pipeline.predict_proba(df)[:, 1]

        importance = _get_feature_importance()
        predictions = []
        for i in range(len(preds)):
            pred = int(preds[i])
            plan = "Ultra" if pred == 1 else "Standard"
            predictions.append(
                PredictionResponse(
                    prediction=pred,
                    plan=plan,
                    probability_is_ultra=round(float(probas[i]), 4) if probas is not None else None,
                    feature_importance=importance,
                    prediction_timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                )
            )

        processing_time = time.time() - start_batch

        if PROMETHEUS_AVAILABLE:
            REQUEST_COUNT.labels(method="POST", endpoint="/predict_batch", status="200").inc()
            REQUEST_LATENCY.labels(endpoint="/predict_batch").observe(processing_time)

        return BatchPredictionResponse(
            predictions=predictions,
            batch_id=batch_id,
            total_customers=len(batch_data.customers),
            processing_time_seconds=processing_time,
        )
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
