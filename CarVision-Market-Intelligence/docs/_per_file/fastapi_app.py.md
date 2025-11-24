# FastAPI Service (`app/fastapi_app.py`)

**Location:** `app/fastapi_app.py`

## Purpose
Provides a high-performance REST API for model inference. It loads the trained model artifacts on startup and exposes endpoints for prediction.

## Endpoints
-   `GET /health`: Health check probe for Kubernetes/Docker. Checks if model is loaded.
-   `POST /predict`: Single item prediction. Accepts JSON payload matching the vehicle schema.
-   `POST /predict_batch`: Batch prediction for multiple items.

## Architecture
-   **Lifespan Manager**: Uses FastAPI's `lifespan` context manager to load the model once during startup, preventing reload latency on every request.
-   **Pydantic Models**: Enforces strict type validation on inputs.

## Validation
Start the server locally and check the docs:
```bash
uvicorn app.fastapi_app:app --reload
```
Visit `http://localhost:8000/docs` to test endpoints interactively.
