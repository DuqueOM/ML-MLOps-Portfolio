# Operations Runbook

## 🚀 Deployment

### Docker Deployment
1. **Build Image:**
   ```bash
   docker build -t telecomai:latest .
   ```
2. **Run Container:**
   ```bash
   docker run -d -p 8000:8000 --name telecom-api \
     -v $(pwd)/artifacts:/app/artifacts \
     -e MODEL_PATH=artifacts/model.joblib \
     telecomai:latest
   ```
3. **Health Check:**
   ```bash
   curl http://localhost:8000/health
   # Expected: {"status": "ok"}
   ```

### Kubernetes (Manifests)
*Refer to `k8s/` directory if available in the broader portfolio for manifests.*

## 🔄 Retraining Pipeline

To retrain the model with new data:
1. Place new data in `users_behavior.csv` (or update DVC pointer).
2. Run training:
   ```bash
   python main.py --mode train --config configs/config.yaml
   ```
3. Verify metrics in `artifacts/metrics.json`.
4. Commit new artifacts (or push to DVC).
5. Redeploy API (Restart container to reload model).

## ⚠️ Troubleshooting

### Common Issues

**1. Model File Not Found**
* **Symptom:** API starts but errors on `/predict` or logs warning "Model not found".
* **Fix:** Ensure `artifacts/model.joblib` exists and is mounted correctly to `/app/artifacts`. Run training if missing.

**2. High Latency**
* **Check:** Ensure the model is not reloading on every request (fixed in v1.1 via `lifespan`).
* **Action:** Check container CPU/Memory usage.

**3. Docker Permissions**
* **Symptom:** `Permission denied` when saving artifacts.
* **Fix:** Ensure the host directory has write permissions for the Docker user (UID 1000 usually).

## 📊 Monitoring

**Key Metrics to Watch:**
- **API Latency:** P99 < 200ms.
- **Error Rate:** Should be < 1%.
- **Drift:** Monitor input feature distributions vs training data (e.g., `calls` mean shift).

## 🚨 Rollback

If a new model performs poorly:
1. Revert `artifacts/model.joblib` to previous version (via Git/DVC).
2. Restart the API service.
   ```bash
   docker restart telecom-api
   ```
