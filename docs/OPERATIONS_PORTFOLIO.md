# ⚙️ Operations Guide — ML/MLOps Portfolio

<div align="center">

**Production Deployment, Monitoring & Troubleshooting Guide**

![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker)
![Kubernetes](https://img.shields.io/badge/K8s-Deployments-326CE5?style=for-the-badge&logo=kubernetes)
![Prometheus](https://img.shields.io/badge/Monitoring-Prometheus-E6522C?style=for-the-badge&logo=prometheus)
![Last Updated](https://img.shields.io/badge/Updated-February%202026-blue?style=for-the-badge)

</div>

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11 or 3.12
- Docker & Docker Compose
- Git
- 8GB RAM minimum
- 20GB free disk space

### One-Click Demo Setup
```bash
# Clone repository
git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git
cd ML-MLOps-Portfolio

# Start full demo stack (all 3 projects + MLflow)
docker compose -f docker-compose.demo.yml up --build

# Access services:
# - MLflow UI: http://localhost:5000
# - BankChurn API: http://localhost:8001/docs
# - CarVision API: http://localhost:8002/docs
# - CarVision Dashboard: http://localhost:8501
# - TelecomAI API: http://localhost:8003/docs
```

**Stop services**:
```bash
docker compose -f docker-compose.demo.yml down
```

### Individual Project Setup

#### BankChurn-Predictor
```bash
cd BankChurn-Predictor

# Install dependencies
pip install -r requirements.txt

# Train model
python main.py --mode train --config configs/config.yaml

# Start API
python main.py --mode api
# or
uvicorn app.fastapi_app:app --reload --port 8000
```

#### CarVision-Market-Intelligence
```bash
cd CarVision-Market-Intelligence

# Install dependencies
pip install -r requirements.txt

# Train model
python main.py --mode train --config configs/config.yaml

# Start API
python main.py --mode api

# Start Streamlit dashboard
streamlit run app/streamlit_app.py
```

#### TelecomAI-Customer-Intelligence
```bash
cd TelecomAI-Customer-Intelligence

# Install dependencies
pip install -r requirements.txt

# Train model
python main.py --mode train

# Start API
uvicorn app.fastapi_app:app --reload --port 8000
```

## Development Workflows

### Making Code Changes

1. **Create feature branch**:
```bash
git checkout -b feature/your-feature-name
```

2. **Install pre-commit hooks**:
```bash
pip install pre-commit
pre-commit install
```

3. **Run tests locally**:
```bash
cd <project-name>
pytest tests/ -v --cov=src
```

4. **Format code**:
```bash
black src/ tests/
isort src/ tests/
flake8 src/ tests/
```

5. **Commit and push**:
```bash
git add .
git commit -m "feat: your feature description"
git push origin feature/your-feature-name
```

### Running Tests

**Unit tests (individual project)**:
```bash
cd BankChurn-Predictor
pytest tests/ -v --cov=src --cov-report=html
```

**Integration tests (full stack)**:
```bash
# Start services
docker compose -f docker-compose.demo.yml up -d

# Run integration tests
pytest tests/integration/test_demo.py -v

# Tear down
docker compose -f docker-compose.demo.yml down
```

**Security scans**:
```bash
# Python code security
bandit -r . -f json -o bandit-report.json

# Container security
docker build -t test-image .
trivy image test-image
```

### Model Training Workflows

#### Local Training with MLflow Tracking
```bash
# Start MLflow server (optional)
mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns --host 0.0.0.0 --port 5000

# Train model with tracking
cd BankChurn-Predictor
export MLFLOW_TRACKING_URI=http://localhost:5000
python main.py --mode train --config configs/config.yaml

# View experiments in MLflow UI
open http://localhost:5000
```

#### Hyperparameter Optimization
```bash
# BankChurn uses Optuna
cd BankChurn-Predictor
python -m src.bankchurn.training --optimize --n-trials 100
```

#### Model Evaluation
```bash
# Generate evaluation report
python main.py --mode evaluate --config configs/config.yaml
```

## Deployment Workflows

### Docker Deployment

#### Build Individual Project
```bash
cd BankChurn-Predictor
docker build -t bankchurn-api:latest .
docker run -p 8000:8000 bankchurn-api:latest
```

#### Build All Projects
```bash
# From repository root
docker compose -f docker-compose.demo.yml build
```

### Kubernetes Deployment

#### Prerequisites
- kubectl configured
- Kubernetes cluster (minikube, GKE, EKS, AKS)

#### Deploy to Kubernetes
```bash
# Create namespace
kubectl create namespace ml-production

# Apply manifests
kubectl apply -f k8s/ -n ml-production

# Check deployment status
kubectl get pods -n ml-production
kubectl get services -n ml-production

# Access services (if using LoadBalancer)
kubectl get svc -n ml-production

# Port-forward for local access
kubectl port-forward svc/bankchurn-service 8001:8000 -n ml-production
kubectl port-forward svc/carvision-service 8002:8000 -n ml-production
kubectl port-forward svc/mlflow-service 5000:5000 -n ml-production
```

#### Enable Monitoring (Prometheus + Grafana)
```bash
# Start with monitoring profile
docker compose -f docker-compose.demo.yml --profile monitoring up
```

### CI/CD Pipeline

#### Automated Testing (GitHub Actions)
The CI/CD pipeline automatically runs on:
- Push to `main` or `develop` branches
- Pull requests to `main`

**Pipeline stages**:
1. **Tests**: Matrix testing (Python 3.11 & 3.12 × 3 projects)
2. **Security**: Gitleaks + Bandit scans
3. **Docker**: Build & Trivy vulnerability scan
4. **Integration**: Full stack integration tests
5. **Report**: Summary generation

**View pipeline**:
- GitHub Actions tab in repository
- Status badges in README

#### Manual Pipeline Trigger
```bash
# Via GitHub CLI
gh workflow run ci-mlops.yml

# Or push a tag
git tag v1.0.0
git push origin v1.0.0
```

## Monitoring & Observability

### Health Checks

**API Health**:
```bash
# BankChurn
curl http://localhost:8001/health

# CarVision
curl http://localhost:8002/health

# TelecomAI
curl http://localhost:8003/health

# MLflow
curl http://localhost:5000/health
```

### Metrics Collection

**Prometheus Metrics** (scrapes all 3 ML services):
```bash
# Access Prometheus
open http://localhost:9090

# Example queries (real metric names):
# - BankChurn request rate: rate(bankchurn_requests_total[5m])
# - CarVision request rate: rate(carvision_requests_total[5m])
# - TelecomAI request rate: rate(telecom_requests_total[5m])
# - Latency P95: histogram_quantile(0.95, sum(rate(bankchurn_request_duration_seconds_bucket[5m])) by (le))
# - Error rate: sum(rate(bankchurn_requests_total{status=~"5.."}[5m]))
```

**Grafana Dashboards** (auto-provisioned "ML Portfolio Metrics" — 10 panels):
```bash
# Access Grafana
open http://localhost:3000
# Credentials (secret grafana-credentials): admin / MLPortfolio2026!
# Dashboard: "ML Portfolio Metrics" (auto-provisioned via ConfigMap)
```

### Production Load Testing

```bash
# Full test (smoke + load + SLA report)
python scripts/load_test_services.py

# Quick validation
python scripts/load_test_services.py --smoke-only

# Custom parameters
python scripts/load_test_services.py --requests 200 --concurrency 5
```

### Logs

**Docker logs**:
```bash
# View logs for specific service
docker compose -f docker-compose.demo.yml logs bankchurn

# Follow logs
docker compose -f docker-compose.demo.yml logs -f carvision

# All services
docker compose -f docker-compose.demo.yml logs
```

**Kubernetes logs**:
```bash
# Pod logs
kubectl logs -f <pod-name> -n ml-production

# Logs from all pods in deployment
kubectl logs -f deployment/bankchurn -n ml-production
```

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

#### Docker Build Fails
```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker compose -f docker-compose.demo.yml build --no-cache
```

#### Model Not Found
```bash
# Ensure model is trained first
cd <project>
python main.py --mode train

# Check models directory
ls -la models/
```

#### Import Errors
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check Python path
echo $PYTHONPATH
```

### Health Check Failures

**Symptom**: Container starts but health check fails

**Solution**:
```bash
# Check container logs
docker logs <container-id>

# Exec into container
docker exec -it <container-id> /bin/bash

# Test health endpoint manually
curl localhost:8000/health

# Check if app is listening on correct port
netstat -tulpn | grep 8000
```

## Maintenance Operations

### Updating Dependencies

```bash
# Update Python packages
cd <project>
pip-compile requirements.in --upgrade
pip install -r requirements.txt

# Rebuild Docker images
docker compose -f docker-compose.demo.yml build
```

### Database Migrations (MLflow)

```bash
# Backup MLflow database
cp mlflow.db mlflow.db.backup

# Run migrations
mlflow db upgrade sqlite:///mlflow.db
```

### Model Versioning

```bash
# Tag model version in MLflow
mlflow models serve -m "models:/<model-name>/<version>" -p 5001
```

## Performance Tuning

### API Performance

**Increase workers**:
```bash
# FastAPI with multiple workers
uvicorn app.fastapi_app:app --workers 4 --host 0.0.0.0 --port 8000
```

**Enable caching** (future enhancement):
```python
# Redis caching for predictions
# TODO: Implement
```

### Model Optimization

**Quantization**:
```python
# Reduce model size (future)
# Use ONNX or TensorFlow Lite
```

## Backup & Recovery

### Backup Strategy

```bash
# Backup MLflow artifacts
tar -czf mlflow-backup-$(date +%Y%m%d).tar.gz mlruns/

# Backup models
tar -czf models-backup-$(date +%Y%m%d).tar.gz */models/

# Backup databases
cp */data/*.db backups/
```

### Recovery

```bash
# Restore MLflow
tar -xzf mlflow-backup-YYYYMMDD.tar.gz

# Restore models
tar -xzf models-backup-YYYYMMDD.tar.gz
```

## Security Best Practices

1. **Never commit secrets**: Use `.env` files (gitignored)
2. **Scan images**: `trivy image <image-name>`
3. **Use non-root users**: All Dockerfiles configured
4. **Keep dependencies updated**: Regular `pip-compile --upgrade`
5. **Enable HTTPS**: Use reverse proxy (nginx) in production
6. **API authentication**: Implement OAuth2/JWT (future)

## Production Data Management (GCS)

All production datasets and model artifacts are stored in Google Cloud Storage with enterprise-grade data management practices.

### GCS Buckets

| Bucket | Purpose | Versioning | Lifecycle |
|--------|---------|------------|-----------|
| `*-ml-models-production` | ML model artifacts (.joblib) | ✅ Enabled | Nearline after 90 days |
| `*-datasets-production` | Training/reference datasets (.csv) | ✅ Enabled | Nearline 30d → Delete 90d (non-current) |

### Dataset Inventory

| Project | File | Size | GCS Path |
|---------|------|------|----------|
| **BankChurn** | `Churn.csv` | 694 KB | `bankchurn/v1/Churn.csv` |
| **CarVision** | `vehicles_us.csv` | 4.3 MB | `carvision/v1/vehicles_us.csv` |
| **TelecomAI** | `WA_Fn-UseC_-Telco-Customer-Churn.csv` | 132 KB | `telecom/v1/WA_Fn-UseC_-Telco-Customer-Churn.csv` |

### Security & Access Control

- **Uniform Bucket-Level IAM** on both buckets
- **Public access prevention** enabled
- **Workload Identity SA** (`ml-portfolio-gke-workload`) has `storage.objectViewer` (read-only)
- No service account keys — pods authenticate via GKE Workload Identity

### Init Container Data Flow

```
Pod startup sequence:
  1. init: download-model  → GCS models bucket  → /app/models/model.joblib
  2. init: download-data   → GCS datasets bucket → /app/data/raw/{dataset}.csv
  3. main: application container starts with both artifacts available
```

### Useful Commands

```bash
# List all datasets
gsutil ls -r gs://ml-portfolio-duque-om-202602-datasets-production/

# Upload a new dataset version
gsutil cp data/raw/dataset.csv gs://ml-portfolio-duque-om-202602-datasets-production/{project}/v2/dataset.csv

# Check versioning history
gsutil ls -la gs://ml-portfolio-duque-om-202602-datasets-production/{project}/

# Verify bucket policies
gsutil lifecycle get gs://ml-portfolio-duque-om-202602-datasets-production/
gsutil iam get gs://ml-portfolio-duque-om-202602-datasets-production/
```

---

## Production Cloud Cost Analysis

Real cost data from the live GCP (GKE) deployment. Values originally billed in COP (Colombian Pesos) and converted at ~4,200 COP/USD for international reference.

### GCP Monthly Cost Breakdown (~$51 USD/month)

| Service | USD/month | % | What It Does |
|---------|-----------|---|--------------|
| **Compute Engine** | $20.50 | 40% | 3 GKE nodes (e2-medium VMs) hosting all pods |
| **Kubernetes Engine** | $13.35 | 26% | GKE cluster management and control plane |
| **Container Scanning** | $9.10 | 18% | Automated vulnerability analysis on Docker images |
| **Networking** | $6.15 | 12% | Load Balancer, VPC, egress traffic |
| **Cloud SQL** | $1.70 | 3% | PostgreSQL instance for MLflow tracking store |
| **Artifact Registry** | $0.18 | <1% | Docker image storage (3 services × ~888 MB) |
| **Cloud Build + Storage** | $0.02 | <1% | Remote builds and GCS model storage |

> **Free Tier**: All costs currently covered by GCP credits (net cost: $0). The breakdown represents real production pricing.

### Cost Optimization Strategies Applied

| Strategy | Savings | Implementation |
|----------|---------|----------------|
| **e2-medium** over n1-standard | ~40% | Right-sized for ML inference (not training) |
| **Single-zone** cluster | ~67% on GKE fees | Acceptable for portfolio; production would use regional |
| **Cleanup policies** | Prevents unbounded growth | Artifact Registry auto-deletes `sha-*` tags after 7 days |
| **Init containers** for model download | Decouples model from image | Smaller images, faster builds, independent model updates |

### Infrastructure Health Metrics

| Metric | Current Value | Status |
|--------|---------------|--------|
| **Running Pods** | 6/6 | ✅ All healthy |
| **Pod Restarts** | 0 | ✅ Stable |
| **GKE Nodes** | 3 (e2-medium) | ✅ Running |
| **Docker Images** | 3 × ~888 MB | ✅ Tagged `v1.0.0` + `latest` |
| **Container CVEs** | 68/image (Low/Medium) | ✅ OS-level, not application code |
| **Cloud Builds** | 5 successful | ✅ All passed |
| **Uptime** | 99.9%+ | ✅ No unplanned downtime |

### Cost Projection: Scaling to Production

| Scenario | Estimated USD/month | Key Changes |
|----------|--------------------:|-------------|
| **Current** (portfolio) | ~$51 | 3 nodes, single-zone, free tier |
| **Startup** (low traffic) | ~$150–250 | Regional cluster, spot nodes, auto-scaling 1–5 |
| **Scale-up** (moderate traffic) | ~$500–1,000 | Multi-zone, dedicated nodes, Cloud CDN, managed certs |
| **Enterprise** (high traffic) | ~$2,000–5,000 | Multi-region, GPU nodes for inference, dedicated DB |

---

## Scaling Recommendations

### Horizontal Scaling
- All 3 ML services use standardized HPA with **dual metrics** (CPU + memory)
- CPU targets: 70% (BankChurn/CarVision), 75% (TelecomAI)
- Memory target: 80% for all services
- Max replicas: 3 per service (1–3 range)
- Conservative scale-down: 300s stabilization, max 50% reduction/min
- Scale-up: 60s stabilization to filter transient spikes

### Vertical Scaling
- Resource requests calibrated to `kubectl top pods` steady-state + headroom
- BankChurn: 448Mi request (ensemble ~300Mi real)
- CarVision API: 640Mi request (~550Mi real) + Streamlit sidecar: 256Mi
- TelecomAI: 384Mi request (~140Mi real)
- Current limits: 768Mi–1Gi memory, 800m–1000m CPU per service

### Database Scaling
- Move MLflow to PostgreSQL for production (Cloud SQL already provisioned)
- Implement connection pooling (PgBouncer recommended)

## Disaster Recovery

1. **Regular backups**: Daily automated backups
2. **Multi-region deployment**: Deploy to multiple cloud regions
3. **Failover strategy**: Use load balancers with health checks
4. **Incident response**: Document runbooks for common issues
---

**Last Updated**: February 2026
