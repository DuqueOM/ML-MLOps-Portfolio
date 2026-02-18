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

# Build images (first time or after changes)
docker build -t ml-portfolio-bankchurn:latest -f BankChurn-Predictor/Dockerfile BankChurn-Predictor
docker build -t ml-portfolio-carvision:latest -f CarVision-Market-Intelligence/Dockerfile CarVision-Market-Intelligence
docker build -t ml-portfolio-telecom:latest -f TelecomAI-Customer-Intelligence/Dockerfile TelecomAI-Customer-Intelligence

# Start the stack
docker compose -f docker-compose.demo.yml up -d

# Verify services
docker compose -f docker-compose.demo.yml ps
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
docker compose -f docker-compose.demo.yml --profile monitoring up -d
```

Access monitoring:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

### Stop Services

```bash
docker compose -f docker-compose.demo.yml down

# Remove volumes too
docker compose -f docker-compose.demo.yml down -v
```

---

## Production Deployment (GCP GKE) ✅

This portfolio is **deployed on Google Cloud Platform** with a GKE cluster running 6 services.

![GKE Workloads](../media/screenshots/gcp-console/05-gke-workloads-running.png)

### Prerequisites

- GCP account with billing enabled
- `gcloud` CLI configured (`gcloud auth login`)
- `kubectl` configured for GKE (`gcloud container clusters get-credentials`)
- Terraform 1.0+ installed

### Infrastructure Setup (Terraform)

```bash
# 1. Initialize Terraform
cd infra/terraform/gcp
terraform init

# 2. Review plan
terraform plan -var-file=terraform.tfvars

# 3. Apply infrastructure (creates GKE, GCS, Artifact Registry, VPC, Cloud SQL)
terraform apply -var-file=terraform.tfvars

# 4. Configure kubectl
gcloud container clusters get-credentials ml-portfolio-gke-production \
  --region us-central1 --project ml-portfolio-duque-om-202602
```

### Build & Push Docker Images

```bash
# Authenticate Docker with Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build and push each service
for svc in BankChurn-Predictor CarVision-Market-Intelligence TelecomAI-Customer-Intelligence; do
  docker build -t us-central1-docker.pkg.dev/PROJECT_ID/ml-portfolio/$(echo $svc | tr '[:upper:]' '[:lower:]'):latest -f $svc/Dockerfile $svc
  docker push us-central1-docker.pkg.dev/PROJECT_ID/ml-portfolio/$(echo $svc | tr '[:upper:]' '[:lower:]'):latest
done
```

### Deploy to GKE

```bash
# Apply namespace and storage
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/storage.yaml

# Deploy all services
kubectl apply -f k8s/

# Verify all 6 pods are running
kubectl get pods -n ml-portfolio
```

**Expected output:**
```
NAME                                    READY   STATUS    RESTARTS   AGE
bankchurn-predictor-xxx                 1/1     Running   0          5m
carvision-intelligence-xxx              1/1     Running   0          5m
telecom-intelligence-xxx                1/1     Running   0          5m
mlflow-server-xxx                       1/1     Running   0          5m
prometheus-xxx                          1/1     Running   0          5m
grafana-xxx                             1/1     Running   0          5m
```

### Kubernetes Resources

| Resource | File | Purpose |
|----------|------|---------|
| Namespace | `k8s/namespace.yaml` | `ml-portfolio` namespace with resource quotas |
| Deployments | `k8s/*-deployment.yaml` | Service pods (6 deployments) |
| Services | `k8s/*-deployment.yaml` | NodePort services for GCE ingress |
| Ingress | `k8s/ingress.yaml` | GCE load balancer with path-based routing |
| Storage | `k8s/storage.yaml` | PVCs for persistent data |
| Monitoring | `k8s/prometheus-deployment.yaml` | Prometheus + Grafana |

### Access Services (Port Forward)

```bash
# BankChurn API
kubectl port-forward svc/bankchurn-service 8001:80 -n ml-portfolio

# CarVision API
kubectl port-forward svc/carvision-service 8002:80 -n ml-portfolio

# TelecomAI API
kubectl port-forward svc/telecom-service 8003:80 -n ml-portfolio

# Grafana (admin/admin)
kubectl port-forward svc/grafana-service 3000:3000 -n ml-portfolio

# Prometheus
kubectl port-forward svc/prometheus-service 9090:9090 -n ml-portfolio

# MLflow
kubectl port-forward svc/mlflow-service 5000:5000 -n ml-portfolio
```

### Scaling

```bash
# Manual scaling
kubectl scale deployment bankchurn-predictor --replicas=3 -n ml-portfolio

# View HPA status
kubectl get hpa -n ml-portfolio
```

### Rolling Updates

```bash
# Update image from Artifact Registry
kubectl set image deployment/bankchurn-predictor \
  bankchurn-predictor=us-central1-docker.pkg.dev/PROJECT_ID/ml-portfolio/bankchurn-predictor:v1.1.0 \
  -n ml-portfolio

# Check rollout status
kubectl rollout status deployment/bankchurn-predictor -n ml-portfolio

# Rollback if needed
kubectl rollout undo deployment/bankchurn-predictor -n ml-portfolio
```

---

## MLflow Setup

### Local MLflow Server

```bash
# Using Docker Compose (recommended)
docker compose -f docker-compose.mlflow.yml up -d

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
    docker compose logs <service-name>
    
    # Common causes:
    # - Missing model files → Run setup_demo_models.sh
    # - Port already in use → Change port mapping
    # - Out of memory → Increase Docker memory limit
    ```

!!! warning "API Returns 500 Error"
    ```bash
    # Check application logs
    docker compose logs --tail 100 bankchurn-api
    
    # Common causes:
    # - Model file missing or corrupted
    # - Invalid input data format
    # - Memory issues during inference
    ```

!!! warning "MLflow Connection Refused"
    ```bash
    # Ensure MLflow is running
    docker compose ps mlflow
    
    # Check network connectivity
    docker compose exec bankchurn-api curl http://mlflow:5000/health
    ```

### Useful Commands

```bash
# View all container logs
docker compose logs -f

# Enter container for debugging
docker compose exec bankchurn-api /bin/bash

# Check resource usage
docker stats

# Rebuild single service
docker compose up -d --build bankchurn-api
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

---

**Last Updated**: February 2026
