"""
NLPInsight Analyzer API

Features:
- Real-time sentiment analysis with transformer models
- Batch prediction support (up to 500 texts)
- Prometheus-compatible metrics endpoint
- Health checks for Kubernetes readiness/liveness
"""

from __future__ import annotations

import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, List, Optional

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
        "nlpinsight_requests_total",
        "Total HTTP requests",
        ["method", "endpoint", "status"],
    )
    REQUEST_LATENCY = Histogram(
        "nlpinsight_request_duration_seconds",
        "Request latency in seconds",
        ["endpoint"],
        buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
    )
    PREDICTION_COUNT = Counter(
        "nlpinsight_predictions_total",
        "Total predictions made",
        ["sentiment"],
    )
except ImportError:
    PROMETHEUS_AVAILABLE = False

BASE_DIR = Path(__file__).resolve().parent.parent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "models"))
start_time = time.time()

# Global state
predictor = None


def load_model_logic() -> bool:
    """Load the sentiment analysis model."""
    global predictor
    try:
        from src.nlpinsight.inference import SentimentPredictor

        model_path = Path(MODEL_PATH)
        if not model_path.exists():
            logger.warning(f"Model directory not found: {model_path}")
            return False

        predictor = SentimentPredictor(model_path=model_path)
        logger.info(f"Model loaded from {model_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return False


@asynccontextmanager
async def lifespan(application: FastAPI):
    # Initialize OpenTelemetry tracing
    if init_telemetry is not None:
        init_telemetry(service_name="nlpinsight-analyzer")
    if instrument_fastapi is not None:
        instrument_fastapi(application)
    success = load_model_logic()
    if not success:
        logger.warning("Application started without model loaded.")
    yield


app = FastAPI(
    title="NLPInsight Analyzer API",
    description="Financial sentiment analysis — dual-backend (TF-IDF + DistilBERT)",
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


# --- Pydantic Models ---


class TextInput(BaseModel):
    """Single text for sentiment analysis."""

    text: str = Field(..., min_length=1, max_length=5000, description="Text to analyze")

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v.strip()


class BatchInput(BaseModel):
    """Batch of texts for sentiment analysis."""

    texts: List[TextInput] = Field(..., min_length=1, max_length=500)


class SentimentResult(BaseModel):
    """Prediction result for a single text."""

    label: str
    confidence: float
    all_scores: Optional[Dict[str, float]] = None


def _model_name() -> str:
    """Return the active model backend name."""
    if predictor is None:
        return "not-loaded"
    return "tfidf-logreg" if predictor.backend == "sklearn" else "distilbert-base-uncased"


class PredictResponse(BaseModel):
    """Single prediction response."""

    prediction: SentimentResult
    model: str = "tfidf-logreg"
    inference_time_ms: float


class BatchResponse(BaseModel):
    """Batch prediction response."""

    predictions: List[SentimentResult]
    count: int
    model: str = "tfidf-logreg"
    inference_time_ms: float


# --- Endpoints ---


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health():
    """Health check for Kubernetes probes."""
    return {
        "status": "healthy" if predictor is not None else "degraded",
        "model_loaded": predictor is not None,
        "uptime_seconds": round(time.time() - start_time, 1),
        "version": "1.0.0",
    }


@app.post("/predict", response_model=PredictResponse)
async def predict(input_data: TextInput):
    """Analyze sentiment of a single text."""
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    t0 = time.perf_counter()
    try:
        result = predictor.predict(input_data.text, return_all_scores=True)
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
    elapsed_ms = (time.perf_counter() - t0) * 1000

    if PROMETHEUS_AVAILABLE:
        REQUEST_COUNT.labels(method="POST", endpoint="/predict", status="200").inc()
        REQUEST_LATENCY.labels(endpoint="/predict").observe(elapsed_ms / 1000)
        PREDICTION_COUNT.labels(sentiment=result["label"]).inc()

    return PredictResponse(
        prediction=SentimentResult(**result),
        model=_model_name(),
        inference_time_ms=round(elapsed_ms, 2),
    )


@app.post("/predict_batch", response_model=BatchResponse)
async def predict_batch(input_data: BatchInput):
    """Analyze sentiment of a batch of texts."""
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    texts = [item.text for item in input_data.texts]
    t0 = time.perf_counter()
    try:
        results = predictor.predict_batch(texts, return_all_scores=True)
    except Exception as e:
        logger.error(f"Batch prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
    elapsed_ms = (time.perf_counter() - t0) * 1000

    if PROMETHEUS_AVAILABLE:
        REQUEST_COUNT.labels(method="POST", endpoint="/predict_batch", status="200").inc()
        REQUEST_LATENCY.labels(endpoint="/predict_batch").observe(elapsed_ms / 1000)
        for r in results:
            PREDICTION_COUNT.labels(sentiment=r["label"]).inc()

    return BatchResponse(
        predictions=[SentimentResult(**r) for r in results],
        count=len(results),
        model=_model_name(),
        inference_time_ms=round(elapsed_ms, 2),
    )


@app.get("/model_info")
async def model_info():
    """Return model metadata and label mapping."""
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    info = {
        "model_path": str(predictor.model_path),
        "backend": predictor.backend,
        "labels": predictor.id2label,
        "num_labels": len(predictor.id2label),
    }
    if hasattr(predictor, "device"):
        info["device"] = predictor.device
    return info


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    if not PROMETHEUS_AVAILABLE:
        return Response(content="prometheus_client not installed", media_type="text/plain")
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
