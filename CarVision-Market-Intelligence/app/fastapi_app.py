"""
CarVision Market Intelligence API

Features:
- Vehicle price prediction using RandomForest/XGBoost pipeline
- Batch prediction support (up to 500 vehicles)
- Prometheus-compatible metrics endpoint
- Health checks for Kubernetes readiness/liveness
"""

from __future__ import annotations

import json
import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, Response
from pydantic import BaseModel, Field, field_validator

# OpenTelemetry (optional — no-op if not installed)
try:
    import sys as _sys

    _sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent))
    from common_utils.telemetry import init_telemetry, instrument_fastapi
except ImportError:
    init_telemetry = None  # type: ignore[assignment]
    instrument_fastapi = None  # type: ignore[assignment]

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
    PREDICTION_COUNT = Counter(
        "carvision_predictions_total",
        "Total predictions made",
    )
except ImportError:
    PROMETHEUS_AVAILABLE = False

BASE_DIR = Path(__file__).resolve().parent.parent

try:
    from common_utils.model_persistence import load_model
except ImportError:
    import joblib

    def load_model(path, **kwargs):
        return joblib.load(path)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "models" / "model.joblib"))
ARTIFACTS_DIR = Path(os.getenv("ARTIFACTS_DIR", str(BASE_DIR / "artifacts")))

# Global state
pipeline = None
feature_columns: Optional[List[str]] = None
start_time = time.time()


def load_model_logic() -> bool:
    """Load model pipeline and feature metadata."""
    global pipeline, feature_columns
    model_path = Path(MODEL_PATH)
    if not model_path.exists():
        logger.error(f"Model not found: {model_path}")
        return False
    try:
        pipeline = load_model(model_path)
        logger.info(f"Model loaded from {model_path}")
    except Exception as e:
        logger.error(f"Failed to load model from {model_path}: {e}")
        return False

    feat_path = ARTIFACTS_DIR / "feature_columns.json"
    if feat_path.exists():
        feature_columns = json.loads(feat_path.read_text())
        logger.info(f"Loaded {len(feature_columns)} feature columns from {feat_path}")
    return True


@asynccontextmanager
async def lifespan(application: FastAPI):
    # Initialize OpenTelemetry tracing
    if init_telemetry is not None:
        init_telemetry(service_name="carvision-market-intelligence")
    if instrument_fastapi is not None:
        instrument_fastapi(application)
    success = load_model_logic()
    if not success:
        logger.warning("Application started without model loaded.")
    yield


app = FastAPI(
    title="CarVision Inference API",
    version="1.0.0",
    root_path=os.getenv("API_ROOT_PATH", ""),
    lifespan=lifespan,
)

# CORS — origins from env for security (no wildcard + credentials)
_cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8501").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _cors_origins],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


class VehicleFeatures(BaseModel):
    model_year: int = Field(..., ge=1990, le=2030)
    model: str = Field(...)
    condition: Optional[str] = "good"
    cylinders: Optional[float] = 4
    fuel: Optional[str] = "gas"
    odometer: Optional[float] = Field(default=0, ge=0)
    transmission: Optional[str] = "automatic"
    drive: Optional[str] = "fwd"
    type: Optional[str] = "sedan"
    paint_color: Optional[str] = "white"


class BatchVehicleData(BaseModel):
    """Schema for batch prediction."""

    vehicles: List[VehicleFeatures]

    @field_validator("vehicles")
    @classmethod
    def validate_batch_size(cls, v: list) -> list:
        if len(v) > 500:
            raise ValueError("Max 500 vehicles per batch")
        if len(v) == 0:
            raise ValueError("Must include at least one vehicle")
        return v


class PredictionResponse(BaseModel):
    predicted_price: float
    prediction_timestamp: str


class BatchPredictionResponse(BaseModel):
    predictions: List[PredictionResponse]
    batch_id: str
    total_vehicles: int
    processing_time_seconds: float


def _prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Add training-time columns not exposed in the API schema.

    The pipeline was trained with raw columns (date_posted, days_listed,
    is_4wd) that are not meaningful at inference time.  We derive or
    default them so sklearn's ColumnTransformer does not raise.
    """
    if "is_4wd" not in df.columns:
        df["is_4wd"] = df["drive"].apply(lambda x: 1.0 if x == "4wd" else 0.0) if "drive" in df.columns else 0.0
    if "date_posted" not in df.columns:
        df["date_posted"] = pd.Timestamp.now().strftime("%Y-%m-%d")
    if "days_listed" not in df.columns:
        df["days_listed"] = 0
    # Safety net: fill any remaining columns the pipeline expects
    if feature_columns:
        for col in feature_columns:
            if col not in df.columns:
                df[col] = 0
    return df


def _predict_single(data: Dict[str, Any]) -> float:
    """Run prediction for a single vehicle through the pipeline."""
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    df = _prepare_dataframe(pd.DataFrame([data]))
    return float(pipeline.predict(df)[0])


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health():
    uptime = time.time() - start_time
    if pipeline is None:
        return {"status": "degraded", "model_loaded": False, "uptime_seconds": uptime}
    return {"status": "ok", "model_loaded": True, "uptime_seconds": uptime}


@app.get("/metrics")
async def metrics():
    """Prometheus-compatible metrics endpoint."""
    if PROMETHEUS_AVAILABLE:
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
    return {"error": "prometheus_client not installed"}


@app.post("/predict", response_model=PredictionResponse)
async def predict(features: VehicleFeatures):
    pred_start = time.time()
    try:
        pred = _predict_single(features.model_dump())
        latency = time.time() - pred_start

        if PROMETHEUS_AVAILABLE:
            REQUEST_COUNT.labels(method="POST", endpoint="/predict", status="200").inc()
            REQUEST_LATENCY.labels(endpoint="/predict").observe(latency)
            PREDICTION_COUNT.inc()

        return PredictionResponse(
            predicted_price=pred,
            prediction_timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        if PROMETHEUS_AVAILABLE:
            REQUEST_COUNT.labels(method="POST", endpoint="/predict", status="500").inc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict_batch", response_model=BatchPredictionResponse)
async def predict_batch(batch_data: BatchVehicleData):
    if pipeline is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    start_batch = time.time()
    batch_id = f"batch_{int(start_batch)}"

    try:
        vehicles_list = [v.model_dump() for v in batch_data.vehicles]
        df = _prepare_dataframe(pd.DataFrame(vehicles_list))
        preds = pipeline.predict(df)

        predictions = [
            PredictionResponse(
                predicted_price=float(preds[i]),
                prediction_timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            )
            for i in range(len(preds))
        ]

        processing_time = time.time() - start_batch

        if PROMETHEUS_AVAILABLE:
            REQUEST_COUNT.labels(method="POST", endpoint="/predict_batch", status="200").inc()
            REQUEST_LATENCY.labels(endpoint="/predict_batch").observe(processing_time)
            PREDICTION_COUNT.inc(len(preds))

        return BatchPredictionResponse(
            predictions=predictions,
            batch_id=batch_id,
            total_vehicles=len(batch_data.vehicles),
            processing_time_seconds=processing_time,
        )
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
