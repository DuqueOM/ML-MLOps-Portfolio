# Inference API (`app/fastapi_app.py`)

## Purpose
Exposes the model via REST API.
It defines the input schema using Pydantic (`TelecomFeatures`), loads the model pipeline on startup, and delegates prediction to the pipeline.

## Validation
1. Start server: `make serve`
2. Test prediction:
   ```bash
   curl -X POST "http://localhost:8000/predict" \
        -H "Content-Type: application/json" \
        -d '{"calls": 10, "minutes": 100, "messages": 5, "mb_used": 500}'
   ```
**Success Criteria:**
- Response contains `"prediction": 0` (or 1) and `"probability_is_ultra"`.
