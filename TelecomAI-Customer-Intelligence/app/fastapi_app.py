from __future__ import annotations

import os
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sklearn.pipeline import Pipeline

APP_TITLE = "TelecomAI Inference API"
MODEL_PATH = os.getenv("MODEL_PATH", "artifacts/model.joblib")

app = FastAPI(title=APP_TITLE)


class TelecomFeatures(BaseModel):
    calls: float = Field(..., ge=0)
    minutes: float = Field(..., ge=0)
    messages: float = Field(..., ge=0)
    mb_used: float = Field(..., ge=0)


def _load_pipeline() -> Pipeline:
    if not Path(MODEL_PATH).exists():
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Train the model first.")
    return joblib.load(MODEL_PATH)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/predict")
async def predict(features: TelecomFeatures) -> dict:
    try:
        pipeline = _load_pipeline()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e

    df = pd.DataFrame([features.dict()])
    proba = None
    if hasattr(pipeline, "predict_proba"):
        proba = float(pipeline.predict_proba(df)[0, 1])
    pred = int(pipeline.predict(df)[0])

    return {
        "prediction": pred,
        "probability_is_ultra": proba,
    }
