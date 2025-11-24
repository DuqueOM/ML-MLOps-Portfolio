# Operations Runbook

**Service:** BankChurn-Predictor  
**Severity:** Tier 2 (Internal Critical)

---

## 1. Deployment Guide

### 1.1 Local Deployment (Docker Compose)
To deploy the full stack (API + MLflow + Postgres if configured):

```bash
make docker-compose-up
```

Verify health:
```bash
curl localhost:8000/health
```

### 1.2 Kubernetes Deployment
Apply manifests located in `k8s/`:
```bash
kubectl apply -f k8s/
```

---

## 2. Maintenance Tasks

### 2.1 Model Retraining
When performance drops (drift detected) or new data arrives:

1.  Place new data in `data/raw/Churn.csv`.
2.  Run training pipeline:
    ```bash
    make train
    ```
3.  Verify metrics in MLflow (locally `mlruns` or remote server).
4.  Commit updated artifacts (`models/best_model.pkl`) or push to registry.
5.  Rebuild and deploy container.

### 2.2 Rollback
If the new model behaves unexpectedly:
1.  Revert to previous docker image tag:
    ```bash
    # Docker
    docker run -d bankchurn-predictor:v1.0.0
    
    # K8s
    kubectl rollout undo deployment/bankchurn-predictor
    ```

---

## 3. Monitoring & Alerting

### 3.1 Key Metrics
| Metric | Threshold | Action |
|--------|-----------|--------|
| **Latency (p95)** | > 200ms | Scale replicas / Check resource limits |
| **Error Rate** | > 1% | Check logs for 500 errors / Data validation failures |
| **Drift (PSI)** | > 0.2 | Trigger retraining |

### 3.2 Checking Logs
```bash
# Docker
docker logs -f bankchurn-container

# System logs (local)
cat bankchurn.log
```

---

## 4. Troubleshooting

### 4.1 Common Issues

**Scenario: API returns 503 Model not available**
-   **Cause**: Model file missing or failed to load.
-   **Fix**: Check if `models/best_model.pkl` exists. Run `make train` to regenerate.

**Scenario: Training fails with OOM**
-   **Cause**: Large dataset with SMOTE.
-   **Fix**: Increase RAM or switch to `undersample` strategy in `configs/config.yaml`.

**Scenario: MLflow connection error**
-   **Cause**: MLflow server down or bad URI.
-   **Fix**: Check `MLFLOW_TRACKING_URI` env var. For local run, set `mlflow.enabled: false` in config.

---

## 5. Disaster Recovery
-   **Data Backup**: Raw data backed up in S3/GCS (via DVC remote).
-   **Model Artifacts**: Stored in MLflow Artifact Store.
-   **Code**: Git repository.

To restore from scratch:
1.  Clone repo.
2.  `dvc pull` (to get data).
3.  `make train` (to rebuild model).
4.  `make api-start`.
