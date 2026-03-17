"""
FastAPI application for BankChurn Predictor

Features:
- Real-time churn prediction with probability and risk level
- Batch prediction support (up to 1000 customers)
- Prometheus-compatible metrics endpoint
- Health checks for Kubernetes readiness/liveness
"""

import contextlib
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field, field_validator

# OpenTelemetry (optional — no-op if not installed)
try:
    from common_utils.logging import get_logger as _get_logger
    from common_utils.telemetry import init_telemetry, instrument_fastapi
except ImportError:
    init_telemetry = None  # type: ignore[assignment]
    instrument_fastapi = None  # type: ignore[assignment]
    _get_logger = None  # type: ignore[assignment]

# Prometheus metrics
try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

    PROMETHEUS_AVAILABLE = True
    REQUEST_COUNT = Counter(
        "bankchurn_requests_total",
        "Total HTTP requests",
        ["method", "endpoint", "status"],
    )
    REQUEST_LATENCY = Histogram(
        "bankchurn_request_duration_seconds",
        "Request latency in seconds",
        ["endpoint"],
        buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
    )
    PREDICTION_COUNT = Counter(
        "bankchurn_predictions_total",
        "Total predictions made",
        ["risk_level"],
    )
except ImportError:
    PROMETHEUS_AVAILABLE = False

from src.bankchurn.explainability import ModelExplainer
from src.bankchurn.prediction import ChurnPredictor

BASE_DIR = Path(__file__).resolve().parent.parent

# Configure logging (structured JSON in production via LOG_FORMAT=json)
if _get_logger is not None:
    logger = _get_logger(__name__, service="bankchurn")
else:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

# Global state
predictor: Optional[ChurnPredictor] = None
model_explainer: Optional[ModelExplainer] = None
model_metadata: Dict[str, Any] = {}
start_time = time.time()


FEATURE_COLUMNS = [
    "CreditScore",
    "Geography",
    "Gender",
    "Age",
    "Tenure",
    "Balance",
    "NumOfProducts",
    "HasCrCard",
    "IsActiveMember",
    "EstimatedSalary",
]


def _load_background_data(max_samples: int = 100) -> Optional[pd.DataFrame]:
    """Load a small background sample for SHAP explainer initialization.

    Searches data directories populated by the init container (production)
    or available locally (development).

    Returns only the 10 feature columns (excludes RowNumber, CustomerId, Surname, Exited).
    """
    data_dirs = [
        BASE_DIR / "data" / "raw",  # Local dev
        Path("/app/data/raw"),  # Production (init container mount)
        BASE_DIR / "data",
    ]
    for data_dir in data_dirs:
        if not data_dir.is_dir():
            continue
        for csv_file in sorted(data_dir.glob("*.csv")):
            try:
                df = pd.read_csv(csv_file, nrows=max_samples)
                # Filter to only the 10 feature columns (exclude metadata and target)
                available = [c for c in FEATURE_COLUMNS if c in df.columns]
                if len(available) >= 8:  # Need most features to be useful
                    clean = df[available].dropna()
                    logger.info(f"Loaded {len(clean)} background samples from {csv_file} ({len(available)} features)")
                    return clean
            except Exception as e:
                logger.debug(f"Could not load {csv_file}: {e}")
    logger.warning("No background data found for SHAP initialization")
    return None


def load_model_logic() -> bool:
    """Internal logic to load model."""
    global predictor, model_explainer, model_metadata
    try:
        model_path = Path(os.environ.get("MODEL_PATH", str(BASE_DIR / "models" / "model.joblib")))
        preprocessor_path = Path(os.environ.get("PREPROCESSOR_PATH", str(BASE_DIR / "models" / "preprocessor.joblib")))

        if not model_path.exists():
            logger.error(f"Model not found: {model_path}")
            return False

        # Pass preprocessor path only if it exists, otherwise None
        # The ChurnPredictor handles Pipeline models without separate preprocessor
        prep_arg = preprocessor_path if preprocessor_path.exists() else None

        predictor = ChurnPredictor.from_files(model_path, prep_arg)

        # Initialize SHAP-based explainer for real feature contributions
        # Background data is needed for SHAP; loaded from data dir (init container in prod)
        try:
            X_background = _load_background_data()
            model_explainer = ModelExplainer(
                predictor.model,
                X_background=X_background,
                feature_names=(list(X_background.columns) if X_background is not None else None),
            )
            if X_background is not None:
                logger.info(f"ModelExplainer initialized with {len(X_background)} background samples")
            else:
                logger.warning("ModelExplainer initialized without background data (contributions may be zero)")
        except Exception as e:
            logger.warning(f"ModelExplainer init failed (contributions will be empty): {e}")
            model_explainer = None

        # Try to load metadata
        metadata_path = BASE_DIR / "models" / "best_model_metadata.json"
        if metadata_path.exists():
            import json

            with open(metadata_path, "r") as f:
                model_metadata = json.load(f)

        logger.info("Model loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return False


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Initialize OpenTelemetry tracing
    if init_telemetry is not None:
        init_telemetry(service_name="bankchurn-predictor")
    if instrument_fastapi is not None:
        instrument_fastapi(app)
    success = load_model_logic()
    if not success:
        logger.warning("Application started without model loaded.")
    yield


app = FastAPI(
    title="BankChurn Predictor API",
    description="API for bank customer churn prediction",
    version="1.0.0",
    root_path=os.getenv("API_ROOT_PATH", ""),
    lifespan=lifespan,
)

# Configurar CORS — origins from env for security (no wildcard + credentials)
_cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8501").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _cors_origins],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# --- Pydantic Models ---


class CustomerData(BaseModel):
    """Schema for individual customer data."""

    CreditScore: int = Field(..., ge=300, le=850)
    Geography: str = Field(...)
    Gender: str = Field(...)
    Age: int = Field(..., ge=18, le=100)
    Tenure: int = Field(..., ge=0, le=10)
    Balance: float = Field(..., ge=0)
    NumOfProducts: int = Field(..., ge=1, le=4)
    HasCrCard: int = Field(..., ge=0, le=1)
    IsActiveMember: int = Field(..., ge=0, le=1)
    EstimatedSalary: float = Field(..., ge=0)

    @field_validator("Geography")
    @classmethod
    def validate_geography(cls, v: str) -> str:
        valid = ["France", "Spain", "Germany"]
        if v not in valid:
            raise ValueError(f"Geography must be one of: {valid}")
        return v

    @field_validator("Gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        valid = ["Male", "Female"]
        if v not in valid:
            raise ValueError(f"Gender must be one of: {valid}")
        return v


class BatchCustomerData(BaseModel):
    """Schema for batch prediction."""

    customers: List[CustomerData]

    @field_validator("customers")
    @classmethod
    def validate_batch_size(cls, v: list) -> list:
        if len(v) > 1000:
            raise ValueError("Max 1000 customers per batch")
        if len(v) == 0:
            raise ValueError("Must include at least one customer")
        return v


class PredictionResponse(BaseModel):
    """Schema for prediction response."""

    churn_probability: float
    churn_prediction: int
    risk_level: str
    confidence: float
    feature_contributions: Dict[str, float]
    model_version: str
    prediction_timestamp: str


class BatchPredictionResponse(BaseModel):
    predictions: List[PredictionResponse]
    batch_id: str
    total_customers: int
    processing_time_seconds: float


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    uptime_seconds: float
    version: str


class ModelMetrics(BaseModel):
    total_predictions: int
    average_prediction_time_ms: float
    model_accuracy: Optional[float] = None
    model_f1_score: Optional[float] = None
    model_auc_roc: Optional[float] = None


# --- Helpers ---


def calculate_feature_contributions(customer_data: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate feature contributions using the ModelExplainer.

    Uses SHAP values when available, otherwise falls back to model-introspected
    feature importances (coefficients or tree importances).  Returns an empty
    dict only when no model is loaded.
    """
    if model_explainer is None:
        return {k: 0.0 for k in customer_data}

    try:
        explanation = model_explainer.explain_prediction(customer_data)
        contributions = explanation.get("feature_contributions", {})
        # Round for cleaner API responses
        return {k: round(float(v), 4) for k, v in contributions.items()}
    except Exception as e:
        logger.warning(f"Feature contribution calculation failed: {e}")
        return {k: 0.0 for k in customer_data}


def determine_risk_level(probability: float) -> str:
    if probability < 0.3:
        return "LOW"
    elif probability < 0.7:
        return "MEDIUM"
    else:
        return "HIGH"


def calculate_confidence(probability: float) -> float:
    return abs(probability - 0.5) * 2


# --- Endpoints ---


@app.get("/", response_model=Dict[str, str])
async def root():
    return {
        "message": "BankChurn Predictor API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    uptime = time.time() - start_time
    return HealthResponse(
        status="healthy" if predictor is not None else "degraded",
        model_loaded=predictor is not None,
        uptime_seconds=uptime,
        version="1.0.0",
    )


@app.get("/metrics")
async def get_metrics():
    """Prometheus-compatible metrics endpoint."""
    if PROMETHEUS_AVAILABLE:
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
    # Fallback to JSON metrics if prometheus_client not installed
    return ModelMetrics(
        total_predictions=0,
        average_prediction_time_ms=0.0,
        model_accuracy=model_metadata.get("test_accuracy"),
        model_f1_score=model_metadata.get("test_f1_score"),
        model_auc_roc=model_metadata.get("test_auc_roc"),
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict_churn(customer: CustomerData, explain: bool = False):
    if predictor is None:
        if PROMETHEUS_AVAILABLE:
            REQUEST_COUNT.labels(method="POST", endpoint="/predict", status="503").inc()
        raise HTTPException(status_code=503, detail="Model not available")

    start_pred = time.time()
    try:
        customer_dict = customer.model_dump()
        df = pd.DataFrame([customer_dict])

        # Use robust prediction from src
        results = predictor.predict(df, include_proba=True)

        prob = float(results.iloc[0]["probability"])
        pred = int(results.iloc[0]["prediction"])
        risk_level = determine_risk_level(prob)

        pred_time = time.time() - start_pred

        # Track Prometheus metrics
        if PROMETHEUS_AVAILABLE:
            REQUEST_COUNT.labels(method="POST", endpoint="/predict", status="200").inc()
            REQUEST_LATENCY.labels(endpoint="/predict").observe(pred_time)
            PREDICTION_COUNT.labels(risk_level=risk_level).inc()

        # SHAP is expensive (~700ms); only compute when explicitly requested
        contributions = calculate_feature_contributions(customer_dict) if explain else {k: 0.0 for k in customer_dict}

        return PredictionResponse(
            churn_probability=prob,
            churn_prediction=pred,
            risk_level=risk_level,
            confidence=calculate_confidence(prob),
            feature_contributions=contributions,
            model_version=model_metadata.get("version", "1.0.0"),
            prediction_timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        if PROMETHEUS_AVAILABLE:
            REQUEST_COUNT.labels(method="POST", endpoint="/predict", status="500").inc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict_batch", response_model=BatchPredictionResponse)
async def predict_batch(batch_data: BatchCustomerData, background_tasks: BackgroundTasks, explain: bool = False):
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not available")

    start_batch = time.time()
    batch_id = f"batch_{int(start_batch)}"

    try:
        customers_list = [c.model_dump() for c in batch_data.customers]
        df = pd.DataFrame(customers_list)

        results = predictor.predict(df, include_proba=True)

        # Vectorized operations instead of iterrows for better performance
        predictions = []
        for i in range(len(results)):
            contributions = (
                calculate_feature_contributions(customers_list[i]) if explain else {k: 0.0 for k in customers_list[i]}
            )

            predictions.append(
                PredictionResponse(
                    churn_probability=float(results.iloc[i]["probability"]),
                    churn_prediction=int(results.iloc[i]["prediction"]),
                    risk_level=determine_risk_level(float(results.iloc[i]["probability"])),
                    confidence=calculate_confidence(float(results.iloc[i]["probability"])),
                    feature_contributions=contributions,
                    model_version=model_metadata.get("version", "1.0.0"),
                    prediction_timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                )
            )

        processing_time = time.time() - start_batch

        return BatchPredictionResponse(
            predictions=predictions,
            batch_id=batch_id,
            total_customers=len(batch_data.customers),
            processing_time_seconds=processing_time,
        )
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
