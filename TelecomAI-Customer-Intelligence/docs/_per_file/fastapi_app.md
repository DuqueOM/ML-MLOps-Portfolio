# app/fastapi_app.py

## Purpose
Defines the REST API interface for the model using FastAPI. It handles request validation (via Pydantic), model lifecycle management (loading once at startup), and prediction logic.

## Key Features
- **Lifespan Context Manager:** Ensures the model is loaded securely into memory only once when the app starts.
- **Pydantic Validation:** Enforces strict types on inputs (`calls`, `minutes`, etc.) to prevent garbage data from reaching the model.
- **Health Check:** `/health` endpoint for container orchestration probes.

## Validation
Run the server locally and check the health endpoint:
```bash
uvicorn app.fastapi_app:app --port 8000
curl http://localhost:8000/health
```
