# fastapi_app.py

**Location:** `app/fastapi_app.py`

## Purpose
Defines the REST API interface for the model. It uses FastAPI to provide high-performance, asynchronous serving with automatic Swagger/OpenAPI documentation.

Features:
1.  **Lifecycle Management**: Uses `@asynccontextmanager` (lifespan) to load the model once on startup, ensuring efficiency.
2.  **Input Validation**: Pydantic models (`CustomerData`) enforce data types and constraints (e.g., CreditScore between 300-850).
3.  **Endpoints**:
    -   `/predict`: For single real-time inference.
    -   `/predict_batch`: For processing multiple records.
    -   `/health`: Kubernetes-friendly health check.
    -   `/metrics`: Operational metrics.

## Validation
Start the server and ping health:
```bash
make api-start
# In another terminal
curl localhost:8000/health
```
