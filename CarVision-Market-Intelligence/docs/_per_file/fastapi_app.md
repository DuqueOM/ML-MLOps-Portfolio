# Inference API (`app/fastapi_app.py`)

## Purpose
This module provides the REST API interface for the model. It is built using FastAPI and uses Pydantic for strict input validation.
Critically, it implements a `ModelWrapper` class that ensures feature engineering logic (e.g., calculating `vehicle_age` from `model_year`) matches the training logic exactly, preventing training-serving skew.

## Validation
To validate the API locally:
1.  Start the server:
    ```bash
    uvicorn app.fastapi_app:app --reload
    ```
2.  Send a test request:
    ```bash
    curl -X POST "http://localhost:8000/predict" \
         -H "Content-Type: application/json" \
         -d '{"model_year": 2019, "model": "toyota corolla", "odometer": 30000}'
    ```
**Success Criteria:**
- Server starts without errors.
- Returns a JSON with `"prediction": float_value`.
