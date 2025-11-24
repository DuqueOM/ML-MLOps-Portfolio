from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

APP_TITLE = "TelecomAI Inference API"
MODEL_PATH = os.getenv("MODEL_PATH", "artifacts/model.joblib")

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
    return {"status": "ok"}


@app.post("/predict")
async def predict(features: TelecomFeatures) -> dict:
    pipeline = ml_models.get("pipeline")
    if not pipeline:
        raise HTTPException(status_code=503, detail="Model not loaded")

    # pydantic v2 compatibility
    data_dict = features.model_dump() if hasattr(features, "model_dump") else features.dict()
    df = pd.DataFrame([data_dict])
    proba = None
    if hasattr(pipeline, "predict_proba"):
        proba = float(pipeline.predict_proba(df)[0, 1])
    pred = int(pipeline.predict(df)[0])

    return {
        "prediction": pred,
        "probability_is_ultra": proba,
    }
