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
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field, validator

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

# Add project root to path to allow imports from src
# app/ is one level deep, so parent is root
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.bankchurn.prediction import ChurnPredictor  # noqa: E402

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
predictor: Optional[ChurnPredictor] = None
model_metadata: Dict[str, Any] = {}
request_count: int = 0
total_prediction_time: float = 0.0
start_time = time.time()


def load_model_logic() -> bool:
    """Internal logic to load model."""
    global predictor, model_metadata
    try:
        model_path = BASE_DIR / "models" / "best_model.pkl"
        preprocessor_path = BASE_DIR / "models" / "preprocessor.pkl"

        if not model_path.exists():
            logger.error(f"Model not found: {model_path}")
            return False

        # Pass preprocessor path only if it exists, otherwise None
        # The ChurnPredictor handles Pipeline models without separate preprocessor
        prep_arg = preprocessor_path if preprocessor_path.exists() else None

        predictor = ChurnPredictor.from_files(model_path, prep_arg)

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
    success = load_model_logic()
    if not success:
        logger.warning("Application started without model loaded.")
    yield


app = FastAPI(
    title="BankChurn Predictor API",
    description="API for bank customer churn prediction",
    version="1.0.0",
    lifespan=lifespan,
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

    @validator("Geography")
    def validate_geography(cls, v):
        valid = ["France", "Spain", "Germany"]
        if v not in valid:
            raise ValueError(f"Geography must be one of: {valid}")
        return v

    @validator("Gender")
    def validate_gender(cls, v):
        valid = ["Male", "Female"]
        if v not in valid:
            raise ValueError(f"Gender must be one of: {valid}")
        return v


class BatchCustomerData(BaseModel):
    """Schema for batch prediction."""

    customers: List[CustomerData]

    @validator("customers")
    def validate_batch_size(cls, v):
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
    Calcula contribuciones aproximadas de features usando valores promedio.
    En producción, se usaría SHAP o LIME para explicaciones precisas.
    """
    # Contribuciones simuladas basadas en importancia conocida
    base = {
        k: 0.0
        for k in customer_data.keys()
        if k
        in [
            "Age",
            "NumOfProducts",
            "IsActiveMember",
            "Geography",
            "Balance",
            "CreditScore",
            "EstimatedSalary",
        ]
    }

    # Lógica simplificada (legacy)
    if customer_data.get("Age", 0) > 50:
        base["Age"] = 0.15
    elif customer_data.get("Age", 0) < 30:
        base["Age"] = -0.05

    if customer_data.get("NumOfProducts", 1) == 1:
        base["NumOfProducts"] = 0.12

    if customer_data.get("IsActiveMember", 0) == 0:
        base["IsActiveMember"] = 0.18

    if customer_data.get("Geography") == "Germany":
        base["Geography"] = 0.14

    return base


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
    avg_time = (total_prediction_time / request_count * 1000) if request_count > 0 else 0
    return ModelMetrics(
        total_predictions=request_count,
        average_prediction_time_ms=avg_time,
        model_accuracy=model_metadata.get("test_accuracy"),
        model_f1_score=model_metadata.get("test_f1_score"),
        model_auc_roc=model_metadata.get("test_auc_roc"),
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict_churn(customer: CustomerData):
    global request_count, total_prediction_time

    if predictor is None:
        if PROMETHEUS_AVAILABLE:
            REQUEST_COUNT.labels(method="POST", endpoint="/predict", status="503").inc()
        raise HTTPException(status_code=503, detail="Model not available")

    start_pred = time.time()
    try:
        customer_dict = customer.dict()
        df = pd.DataFrame([customer_dict])

        # Use robust prediction from src
        results = predictor.predict(df, include_proba=True)

        prob = float(results.iloc[0]["probability"])
        pred = int(results.iloc[0]["prediction"])
        risk_level = determine_risk_level(prob)

        pred_time = time.time() - start_pred
        request_count += 1
        total_prediction_time += pred_time

        # Track Prometheus metrics
        if PROMETHEUS_AVAILABLE:
            REQUEST_COUNT.labels(method="POST", endpoint="/predict", status="200").inc()
            REQUEST_LATENCY.labels(endpoint="/predict").observe(pred_time)
            PREDICTION_COUNT.labels(risk_level=risk_level).inc()

        return PredictionResponse(
            churn_probability=prob,
            churn_prediction=pred,
            risk_level=risk_level,
            confidence=calculate_confidence(prob),
            feature_contributions=calculate_feature_contributions(customer_dict),
            model_version=model_metadata.get("version", "1.0.0"),
            prediction_timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        if PROMETHEUS_AVAILABLE:
            REQUEST_COUNT.labels(method="POST", endpoint="/predict", status="500").inc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict_batch", response_model=BatchPredictionResponse)
async def predict_batch(batch_data: BatchCustomerData, background_tasks: BackgroundTasks):
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not available")

    start_batch = time.time()
    batch_id = f"batch_{int(start_batch)}"

    try:
        customers_list = [c.dict() for c in batch_data.customers]
        df = pd.DataFrame(customers_list)

        results = predictor.predict(df, include_proba=True)

        predictions = []
        for i, row in results.iterrows():
            prob = float(row["probability"])
            pred = int(row["prediction"])
            predictions.append(
                PredictionResponse(
                    churn_probability=prob,
                    churn_prediction=pred,
                    risk_level=determine_risk_level(prob),
                    confidence=calculate_confidence(prob),
                    feature_contributions=calculate_feature_contributions(customers_list[i]),
                    model_version=model_metadata.get("version", "1.0.0"),
                    prediction_timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                )
            )

        processing_time = time.time() - start_batch

        global request_count, total_prediction_time
        request_count += len(batch_data.customers)
        total_prediction_time += processing_time

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
