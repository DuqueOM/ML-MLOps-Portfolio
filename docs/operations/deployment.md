# Deployment Guide

This guide covers deploying the ML-MLOps Portfolio services in various environments.

## Deployment Options

| Environment | Method | Best For |
|-------------|--------|----------|
| **Local Demo** | Docker Compose | Quick evaluation, development |
| **Staging** | Docker Compose + MLflow | Testing before production |
| **Production** | Kubernetes | Scalable production workloads |

---

## Local Deployment (Docker Compose)

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ RAM available

### Start All Services

```bash
# Generate demo models (first time only)
bash scripts/setup_demo_models.sh

# Start the stack
docker-compose -f docker-compose.demo.yml up -d --build

# Verify services
docker-compose -f docker-compose.demo.yml ps
```

### Service Endpoints

| Service | Port | Health Check |
|---------|------|--------------|
| MLflow | 5000 | `curl http://localhost:5000/health` |
| BankChurn API | 8001 | `curl http://localhost:8001/health` |
| CarVision API | 8002 | `curl http://localhost:8002/health` |
| TelecomAI API | 8003 | `curl http://localhost:8003/health` |
| CarVision Dashboard | 8501 | `curl http://localhost:8501` |

### Enable Monitoring (Optional)

```bash
# Start with Prometheus + Grafana
docker-compose -f docker-compose.demo.yml --profile monitoring up -d
```

Access monitoring:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

### Stop Services

```bash
docker-compose -f docker-compose.demo.yml down

# Remove volumes too
docker-compose -f docker-compose.demo.yml down -v
```

---

## Production Deployment (Kubernetes)

### Prerequisites

- Kubernetes cluster (EKS, GKE, or local)
- kubectl configured
- Helm 3.x (optional, for ingress)

### Deploy Services

```bash
# Apply all manifests
kubectl apply -f k8s/

# Verify pods
kubectl get pods -n ml-portfolio

# Check services
kubectl get svc -n ml-portfolio
```

### Kubernetes Resources

| Resource | File | Purpose |
|----------|------|---------|
| Deployments | `k8s/*-deployment.yaml` | Service pods |
| Services | `k8s/*-deployment.yaml` | Internal networking |
| HPA | `k8s/hpa.yaml` | Auto-scaling |
| Ingress | `k8s/ingress.yaml` | External access |

### Scaling

```bash
# Manual scaling
kubectl scale deployment bankchurn-api --replicas=3

# View HPA status
kubectl get hpa
```

### Rolling Updates

```bash
# Update image
kubectl set image deployment/bankchurn-api \
  bankchurn-api=ghcr.io/duqueom/bankchurn:v1.2.0

# Check rollout status
kubectl rollout status deployment/bankchurn-api

# Rollback if needed
kubectl rollout undo deployment/bankchurn-api
```

---

## MLflow Setup

### Local MLflow Server

```bash
# Using Docker Compose (recommended)
docker-compose -f docker-compose.mlflow.yml up -d

# Or standalone
mlflow server \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlruns \
  --host 0.0.0.0 \
  --port 5000
```

### Configure Tracking URI

Set in environment or code:

```bash
export MLFLOW_TRACKING_URI=http://localhost:5000
```

```python
import mlflow
mlflow.set_tracking_uri("http://localhost:5000")
```

### Model Registration

```python
# Log model during training
mlflow.sklearn.log_model(model, "model", registered_model_name="BankChurnModel")

# Load registered model
model = mlflow.sklearn.load_model("models:/BankChurnModel/Production")
```

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MLFLOW_TRACKING_URI` | MLflow server URL | `http://mlflow:5000` |
| `LOG_LEVEL` | Logging verbosity | `INFO`, `DEBUG` |
| `PYTHONUNBUFFERED` | Disable output buffering | `1` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MODEL_PATH` | Path to model artifact | `models/model.pkl` |
| `DATA_PATH` | Path to data directory | `data/` |
| `PORT` | API server port | `8000` |

---

## Health Checks

All APIs expose health endpoints:

```bash
# Check individual service
curl http://localhost:8001/health

# Expected response
{"status": "healthy", "version": "1.0.0"}
```

### Kubernetes Probes

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

---

## Troubleshooting

### Common Issues

!!! warning "Container Won't Start"
    ```bash
    # Check logs
    docker-compose logs <service-name>
    
    # Common causes:
    # - Missing model files → Run setup_demo_models.sh
    # - Port already in use → Change port mapping
    # - Out of memory → Increase Docker memory limit
    ```

!!! warning "API Returns 500 Error"
    ```bash
    # Check application logs
    docker-compose logs --tail 100 bankchurn-api
    
    # Common causes:
    # - Model file missing or corrupted
    # - Invalid input data format
    # - Memory issues during inference
    ```

!!! warning "MLflow Connection Refused"
    ```bash
    # Ensure MLflow is running
    docker-compose ps mlflow
    
    # Check network connectivity
    docker-compose exec bankchurn-api curl http://mlflow:5000/health
    ```

### Useful Commands

```bash
# View all container logs
docker-compose logs -f

# Enter container for debugging
docker-compose exec bankchurn-api /bin/bash

# Check resource usage
docker stats

# Rebuild single service
docker-compose up -d --build bankchurn-api
```

---

## Production Checklist

- [ ] All health checks passing
- [ ] Resource limits configured (CPU, memory)
- [ ] Secrets stored securely (not in code)
- [ ] Logging configured and accessible
- [ ] Monitoring dashboards set up
- [ ] Alerting rules defined
- [ ] Backup strategy in place
- [ ] Rollback procedure tested
- [ ] Load testing completed
- [ ] Security scanning passed
