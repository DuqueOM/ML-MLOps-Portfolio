# Operations Runbook

**Service:** BankChurn-Predictor  
**Severity:** Tier 2 (Internal Critical)  
**Maintainer:** MLOps Team  

---

## 1. Prerequisites & Environment

### 1.1 Environment Variables
The service relies on the following environment variables. Ensure they are set in your deployment manifest or `.env` file.

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LOG_LEVEL` | Logging verbosity (DEBUG, INFO, WARN) | `INFO` | No |
| `MLFLOW_TRACKING_URI` | URI for MLflow server | `http://localhost:5000` | No (if disabled in config) |
| `WORKERS` | Number of Uvicorn workers | `1` | No |

---

## 2. Deployment Guide

### 2.1 Local Deployment (Docker Compose)
To deploy the full stack (API + MLflow):

```bash
make docker-demo
```

**Verification**:
```bash
curl localhost:8000/health
# Expected: {"status": "healthy", "model_loaded": true}
```

### 2.2 Kubernetes Deployment (Manual)
Apply manifests located in `k8s/`:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

---

## 3. Maintenance Tasks

### 3.1 Model Retraining (Drift Response)
When performance metrics (F1/AUC) drop or data drift is detected:

1.  **Ingest New Data**: Place the new dataset in `data/raw/Churn.csv` (or update DVC pointer).
2.  **Run Pipeline**:
    ```bash
    make train
    ```
3.  **Validate**: Check the output in `models/metrics.json`. Ensure F1 > 0.80.
4.  **Release**:
    -   Commit the new `dvc.lock` and `models/metrics.json`.
    -   Push to git to trigger CI/CD.
    -   The pipeline will build a new Docker image with the updated model.

### 3.2 Manual Rollback
If the new model behaves unexpectedly in production:

**Docker:**
```bash
# Stop current
docker stop bankchurn-demo
# Run previous tag (e.g., v1.0.0)
docker run -d --name bankchurn-demo -p 8000:8000 ghcr.io/duqueom/bankchurn:v1.0.0
```

**Kubernetes:**
```bash
kubectl rollout undo deployment/bankchurn-api
```

---

## 4. Monitoring & Alerting

### 4.1 Key Metrics (Prometheus)
The API exposes metrics at `/metrics`. Key indicators to watch:

| Metric | Threshold | Action |
|--------|-----------|--------|
| `http_request_duration_seconds_bucket` (P95) | > 200ms | Scale replicas / Check CPU usage |
| `http_requests_total` (status=5xx) | > 1% rate | Check logs for application errors |
| `model_prediction_drift` (Evidently) | > 0.2 PSI | Trigger retraining |

### 4.2 Logs
Logs are structured in JSON (if configured) or standard text.

```bash
# Docker
docker logs -f bankchurn-demo

# Search for errors
docker logs bankchurn-demo 2>&1 | grep "ERROR"
```

---

## 5. Troubleshooting

### 5.1 Common Scenarios

**Scenario: API returns 503 "Model not available"**
-   **Cause**: The `best_model.pkl` artifact was not found during startup.
-   **Fix**:
    1.  Verify `models/best_model.pkl` exists in the container.
    2.  If using volumes, check the mount path.
    3.  Run `make train` locally and rebuild image.

**Scenario: "ModuleNotFoundError: src"**
-   **Cause**: Python path misconfiguration.
-   **Fix**: Always execute via `python -m src.bankchurn.cli ...` or use the provided `Makefile` targets which set `PYTHONPATH`.

**Scenario: OOM (Out of Memory) during Training**
-   **Cause**: SMOTE oversampling creating too many synthetic samples.
-   **Fix**: Update `configs/config.yaml` to use `undersample` strategy or increase container memory limit.

---

## 6. Disaster Recovery

-   **Code**: Recover from GitHub `main` branch.
-   **Data**: Pull from DVC remote storage (S3/GCS).
-   **Model**: Pull previous known good model from MLflow or Git history (if committed).

**Recovery Sequence:**
1.  `git clone [repo]`
2.  `dvc pull`
3.  `make install`
4.  `make train`
5.  `make api-start`
