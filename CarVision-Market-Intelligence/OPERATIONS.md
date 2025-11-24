# Operations Runbook - CarVision

This document outlines the procedures for maintaining, monitoring, and troubleshooting the CarVision Market Intelligence system.

## 1. Deployment

### 1.1 Container Deployment
The standard deployment method is via Docker.

**Build & Run:**
```bash
docker build -t carvision:latest .
docker run -d -p 8000:8000 --name carvision-api carvision:latest
```

**Health Check:**
Verify the service is up:
```bash
curl -f http://localhost:8000/health
# Expected output: {"status": "ok"}
```

### 1.2 Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_PATH` | `artifacts/model.joblib` | Path to the serialized model artifact. |
| `ARTIFACTS_DIR` | `artifacts` | Directory containing metadata (feature columns). |

## 2. Model Retraining

Retraining should be triggered when data drift is detected or new data becomes available.

**Procedure:**
1.  **Update Data:** Place the new `vehicles_us.csv` in `data/raw/`.
2.  **Run Pipeline:**
    ```bash
    make train
    ```
3.  **Evaluate:**
    ```bash
    make eval
    ```
    *Check `artifacts/metrics.json`. Ensure RMSE < Threshold (e.g., 8000).*
4.  **Commit Artifacts:**
    If performance improves, commit the new artifacts (or push to DVC remote).
    ```bash
    git add artifacts/
    git commit -m "Model update: RMSE improved to X"
    ```
5.  **Redeploy:**
    Restart the container to load the new model.

## 3. Monitoring

### 3.1 Key Metrics to Watch
- **API Latency:** 99th percentile response time should be < 200ms.
- **Error Rate:** 5xx responses should be 0%.
- **Prediction Distribution:** Monitor the mean predicted price. Significant shifts indicate concept drift.

### 3.2 Logs
Access logs via Docker:
```bash
docker logs -f carvision-api
```
Look for:
- `ERROR` level logs (Tracebacks).
- `WARNING` logs regarding missing features during inference.

## 4. Troubleshooting

### Issue: "Model not loaded" error in API
**Cause:** The `artifacts/model.joblib` file is missing or corrupted.
**Resolution:**
1.  Check if file exists in container: `docker exec carvision-api ls -l artifacts/`
2.  If missing, rerun `make train` and rebuild image.

### Issue: "Column mismatch" during prediction
**Cause:** The input JSON payload contains fields not expected by the model, or is missing required fields.
**Resolution:**
1.  Check `artifacts/feature_columns.json` to see expected schema.
2.  Ensure `fastapi_app.py` logic matches `training.py` preprocessing.

### Issue: Performance degradation (High RMSE)
**Cause:** Outliers in new data or change in data distribution (e.g., inflation).
**Resolution:**
1.  Run `src/carvision/analysis.py` on new data.
2.  Adjust filtering thresholds in `src/carvision/data.py`.
3.  Retrain.

## 5. Rollback
If a bad model is deployed:
1.  Revert the git commit containing the new artifacts.
    ```bash
    git checkout HEAD~1 artifacts/
    ```
2.  Rebuild and redeploy container.
