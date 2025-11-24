# 🛠 Operations Runbook - Global Portfolio

This document outlines the operational procedures for managing, deploying, and troubleshooting the applications in the ML-MLOps Portfolio.

## 1. Deployment Management

### 1.1 Prerequisites
- **Docker Engine** 20.10+
- **Docker Compose** v2.0+
- **Make** utility
- **Python** 3.11+ (for local management)

### 1.2 Deploying the Full Stack (Local/Staging)
To spin up all services including the MLflow tracking server:

```bash
# From root directory
make docker-demo
```

This command:
1. Builds fresh images for BankChurn, CarVision, and TelecomAI.
2. Starts the MLflow server and SQLite backend.
3. Launches all 3 APIs and the CarVision Dashboard.
4. Connects them via a shared Docker network `ml-mlops-network`.

### 1.3 Verifying Deployment
Check the status of all containers:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

Expected output:
| Names | Status | Ports |
|-------|--------|-------|
| mlflow-server | Up (healthy) | 0.0.0.0:5000->5000/tcp |
| bankchurn-api | Up (healthy) | 0.0.0.0:8001->8000/tcp |
| carvision-api | Up (healthy) | 0.0.0.0:8002->8000/tcp, 0.0.0.0:8501->8501/tcp |
| telecom-api | Up (healthy) | 0.0.0.0:8003->8000/tcp |

## 2. Monitoring & Health Checks

### 2.1 Health Endpoints
Each service exposes a standard health check endpoint:

- **BankChurn**: `curl http://localhost:8001/health`
- **CarVision**: `curl http://localhost:8002/health`
- **TelecomAI**: `curl http://localhost:8003/health`

Response:
```json
{"status": "healthy", "version": "1.0.0", "model_loaded": true}
```

### 2.2 Logging
Logs are streamed to stdout/stderr and captured by the Docker daemon.

**View logs for a specific service:**
```bash
# Follow logs for BankChurn
docker logs -f bankchurn-api

# View logs for all services
docker-compose -f docker-compose.demo.yml logs -f
```

## 3. Routine Maintenance

### 3.1 Retraining Models
When data drifts or new data arrives, models need retraining. This is currently a manual trigger or CI/CD scheduled event.

**Example: Retraining BankChurn**
```bash
# Enter the container (or run locally)
docker exec -it bankchurn-api bash

# Run the training pipeline
python -m src.bankchurn.training --data-path data/raw/churn.csv --register-model
```

### 3.2 Database Migrations
MLflow uses SQLite for this demo stack. The database is persisted in `mlruns/mlflow.db`.
To reset the database (CAUTION: deletes all experiments):
```bash
rm mlruns/mlflow.db
make docker-demo  # Recreates the DB on startup
```

## 4. Troubleshooting & Incident Response

### 4.1 Incident: Service Returns 500 Error
1. **Check Logs**: `docker logs bankchurn-api --tail 100`
2. **Verify Model**: Ensure the model artifact exists in `models/`.
3. **Restart Service**: `docker restart bankchurn-api`

### 4.2 Incident: MLflow Connection Failed
If services cannot log metrics:
1. Verify MLflow container is healthy: `docker inspect --format='{{json .State.Health}}' mlflow-server`
2. Check network connectivity: Ensure `MLFLOW_TRACKING_URI` is set to `http://mlflow:5000` inside containers.

### 4.3 Incident: Port Conflicts
If `make docker-demo` fails with "Bind for 0.0.0.0:8001 failed: port is already allocated":
1. Find the process: `sudo lsof -i :8001`
2. Kill it: `kill -9 <PID>`
3. Or modify `docker-compose.demo.yml` to use a different host port.

## 5. Security Procedures

- **Secrets Management**: Never commit `.env` files. Use GitHub Secrets for CI/CD.
- **Image Scanning**: All images are scanned by Trivy in the CI pipeline.
- **Updates**: Regularly run `make upgrade-deps` (if configured) or manually update `requirements.in` and re-compile to patch vulnerabilities.

## 6. Disaster Recovery
- **Artifacts**: In production, use S3/GCS for MLflow artifacts.
- **Code**: Git is the single source of truth.
- **Recovery Time Objective (RTO)**: < 5 minutes (Container restart time).
