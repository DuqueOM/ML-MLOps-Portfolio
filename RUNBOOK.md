# 📖 Operations Runbook — ML/MLOps Portfolio

<div align="center">

**Day-to-Day Operations & Troubleshooting Guide**

![Docker](https://img.shields.io/badge/Docker-20.10+-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![Kubernetes](https://img.shields.io/badge/K8s-Ready-326CE5)
![Last Updated](https://img.shields.io/badge/updated-March%202026-blue)

</div>

---

## 📋 Quick Reference

| Operation | Command | Duration |
|-----------|---------|----------|
| **Start Demo Stack** | `make docker-demo` | ~2 min |
| **Health Check** | `make health-check` | ~5 sec |
| **Run Tests** | `make test` | ~30 sec |
| **Stop Services** | `docker compose -f docker-compose.demo.yml down` | ~10 sec |
| **View Logs** | `docker compose logs -f <service>` | Real-time |

---

## 🛠️ Prerequisites

### System Requirements

| Component | Minimum | Recommended | Check Command |
|-----------|---------|-------------|---------------|
| **Python** | 3.11 | 3.11+ | `python --version` |
| **Docker** | 20.10 | 24.0+ | `docker --version` |
| **Docker Compose** | 2.0 | 2.20+ | `docker compose version` |
| **Make** | Any | Latest | `make --version` |
| **Git** | 2.30 | 2.40+ | `git --version` |
| **RAM** | 8GB | 16GB | `free -h` |
| **Disk** | 20GB | 50GB | `df -h` |

### First-Time Setup

```bash
# 1. Clone repository
git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git
cd ML-MLOps-Portfolio

# 2. Generate demo models (one-time)
bash scripts/setup_demo_models.sh

# 3. Verify installation
make --version
docker --version
python --version
```

---

## 🚀 Common Operations

### Start Full Demo Stack

```bash
# Method 1: Make command (recommended)
make docker-demo

# Method 2: Direct Docker Compose
docker compose -f docker-compose.demo.yml up -d --build

# Verify all services started
make health-check
```

**Expected Services** (5 containers):
- `bankchurn-api` (port 8001)
- `carvision-api` (port 8002)
- `carvision-dashboard` (port 8501)
- `telecomai-api` (port 8003)
- `mlflow` (port 5000)

### Health Monitoring

```bash
# Quick health check (all services)
make health-check

# Individual service checks
curl http://localhost:8001/health  # BankChurn
curl http://localhost:8002/health  # CarVision API
curl http://localhost:8003/health  # TelecomAI
curl http://localhost:8501          # CarVision Dashboard (returns HTML)
curl http://localhost:5000          # MLflow (returns HTML)
```

**Healthy Response**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "1.5.0"
}
```

### Stop Services

```bash
# Stop containers (keep volumes)
docker compose -f docker-compose.demo.yml down

# Stop + remove volumes (clean slate)
docker compose -f docker-compose.demo.yml down -v

# Nuclear option (remove images too)
docker compose -f docker-compose.demo.yml down -v --rmi all
```

---

## 🔬 Testing

### Unit Tests

```bash
# All projects
make test

# Individual project
cd BankChurn-Predictor
pytest tests/ -v --cov=src --cov-report=html

# Expected: >95% coverage, all tests pass
```

### Integration Tests

```bash
# 1. Start demo stack
docker compose -f docker-compose.demo.yml up -d

# 2. Wait for services to be ready (30s)
sleep 30

# 3. Run integration tests
pytest tests/integration/test_demo.py -v

# 4. Cleanup
docker compose -f docker-compose.demo.yml down
```

**Tests Included**:
- Health endpoint validation (5 services)
- Prediction endpoint validation (3 APIs)
- Response schema validation
- Performance benchmarks (latency <200ms)

### Performance Testing

```bash
# API latency test (BankChurn example)
ab -n 1000 -c 10 -p payload.json -T application/json \
   http://localhost:8001/predict

# Expected: Mean latency <50ms, P95 <100ms
```

---

## 📦 Per-Project Operations

### BankChurn-Predictor

```bash
cd BankChurn-Predictor

# Train model
python main.py --mode train --config configs/config.yaml

# Evaluate model
python main.py --mode eval

# Start API locally
uvicorn app.fastapi_app:app --host 0.0.0.0 --port 8000 --reload

# Test prediction
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d @examples/sample_customer.json
```

**Key Artifacts**:
- `artifacts/model.joblib` (trained pipeline)
- `artifacts/metrics.json` (evaluation results)

### CarVision-Market-Intelligence

```bash
cd CarVision-Market-Intelligence

# Train model
python main.py --mode train --config configs/config.yaml

# Start API
uvicorn app.fastapi_app:app --host 0.0.0.0 --port 8000

# Start Dashboard
streamlit run app/streamlit_app.py --server.port 8501

# Test prediction
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"model_year":2018,"odometer":45000,"model":"ford f-150","fuel":"gas","transmission":"automatic"}'
```

**Dashboard Features**:
- Portfolio Overview (KPIs, price distribution)
- Market Analysis (investment insights)
- Model Metrics (RMSE, R², bootstrap CI)
- Price Predictor (single-vehicle estimation)

### TelecomAI-Customer-Intelligence

```bash
cd TelecomAI-Customer-Intelligence

# Train model
python main.py --mode train

# Start API
uvicorn app.fastapi_app:app --host 0.0.0.0 --port 8000

# Test prediction
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"calls":40.0,"minutes":311.9,"messages":83.0,"mb_used":19915.42}'
```

**Response**:
```json
{
  "prediction": 0,
  "probability_is_ultra": 0.12,
  "confidence": "HIGH",
  "recommendation": "Smart plan ($40/mo) is optimal"
}
```

---

## 📊 MLflow Operations

### Start MLflow Server

```bash
# Option 1: Docker Compose (recommended)
docker compose -f docker-compose.mlflow.yml up -d

# Option 2: Local file-based
mlflow ui --backend-store-uri file:./mlruns --port 5000

# Access UI
open http://localhost:5000
```

### Log Experiments

```bash
# Set tracking URI
export MLFLOW_TRACKING_URI=http://localhost:5000

# Run experiments
cd BankChurn-Predictor && make mlflow-demo && cd ..
cd CarVision-Market-Intelligence && make mlflow-demo && cd ..
cd TelecomAI-Customer-Intelligence && make mlflow-demo && cd ..
```

### View Experiments (CLI)

```bash
# List experiments
mlflow experiments list

# List runs for experiment
mlflow runs list --experiment-id 0

# Get run details
mlflow runs describe --run-id <run_id>
```

---

## 🐳 Docker Operations

### Build Images

```bash
# Build all images
make docker-build

# Build individual images
docker build -t bankchurn:latest ./BankChurn-Predictor
docker build -t carvision:latest ./CarVision-Market-Intelligence
docker build -t telecomai:latest ./TelecomAI-Customer-Intelligence
```

### Push to Registry (GHCR)

```bash
# 1. Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u DuqueOM --password-stdin

# 2. Tag images
docker tag bankchurn:latest ghcr.io/duqueom/bankchurn-api:v1.5.0
docker tag carvision:latest ghcr.io/duqueom/carvision-api:v1.5.0
docker tag telecomai:latest ghcr.io/duqueom/telecomai:v1.5.0

# 3. Push to registry
docker push ghcr.io/duqueom/bankchurn-api:v1.5.0
docker push ghcr.io/duqueom/carvision-api:v1.5.0
docker push ghcr.io/duqueom/telecomai:v1.5.0
```

### Pull from Registry

```bash
# Pull pre-built images
docker pull ghcr.io/duqueom/bankchurn-api:latest
docker pull ghcr.io/duqueom/carvision-api:latest
docker pull ghcr.io/duqueom/telecomai:latest

# Run pulled image
docker run -d -p 8001:8000 ghcr.io/duqueom/bankchurn-api:latest
```

---

## 🔐 Security Operations

### Scan Docker Images

```bash
# Trivy scan (vulnerabilities)
docker run --rm aquasec/trivy image bankchurn:latest

# Expected: No HIGH/CRITICAL vulnerabilities
```

### Scan Python Dependencies

```bash
# Bandit (code security)
bandit -r . -f json -o bandit-report.json

# pip-audit (dependency vulnerabilities)
pip-audit --requirement requirements.txt

# Safety check (deprecated, use pip-audit)
safety check --json
```

### Secret Detection

```bash
# Gitleaks (secret scanning)
gitleaks detect --source . --report-path gitleaks-report.json

# Expected: No secrets found
```

---

## 🐛 Troubleshooting

### Common Issues

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **ModuleNotFoundError** | Import errors | Set PYTHONPATH: `export PYTHONPATH=$PWD` or use `python -m` |
| **Port already in use** | `Address already in use` | Find process: `lsof -i :8001`, kill: `kill -9 <PID>` |
| **Container won't start** | Exit code 1 | Check logs: `docker logs <container>` |
| **Model not found** | `FileNotFoundError: model.joblib` | Run `make train` or `bash scripts/setup_demo_models.sh` |
| **Out of memory** | Docker crash | Increase Docker memory limit (8GB min) |
| **Connection refused** | API unreachable | Wait 30s after startup, services need time to initialize |

### View Logs

```bash
# All services (real-time)
docker compose -f docker-compose.demo.yml logs -f

# Specific service
docker compose -f docker-compose.demo.yml logs -f bankchurn

# Last 100 lines
docker compose -f docker-compose.demo.yml logs --tail=100 carvision-api
```

### Restart Services

```bash
# Restart specific service
docker compose -f docker-compose.demo.yml restart bankchurn

# Restart all services
docker compose -f docker-compose.demo.yml restart
```

### Reset Everything

```bash
# 1. Stop and remove all containers, networks, volumes
docker compose -f docker-compose.demo.yml down -v --rmi all

# 2. Remove Python caches
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null

# 3. Clean Docker system
docker system prune -a --volumes -f

# 4. Re-install dependencies
make install

# 5. Regenerate demo models
bash scripts/setup_demo_models.sh

# 6. Start fresh
make docker-demo
```

---

## ⚙️ Environment Variables

### Configuration

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

**Key Variables**:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SEED` | Random seed for reproducibility | `42` | No |
| `MLFLOW_TRACKING_URI` | MLflow server URL | `file:./mlruns` | No |
| `API_HOST` | API bind address | `0.0.0.0` | No |
| `API_PORT` | API port | `8000` | No |
| `LOG_LEVEL` | Logging verbosity | `INFO` | No |
| `MODEL_PATH` | Path to model artifacts | `artifacts/model.joblib` | Yes |

### Production Overrides

```bash
# Production environment variables
export LOG_LEVEL=WARNING
export MLFLOW_TRACKING_URI=https://mlflow.example.com
export MODEL_PATH=/app/models/production/model.joblib
```

---

## 🚀 CI/CD Operations

### GitHub Actions Workflow

**File**: `.github/workflows/ci-mlops.yml`

**Pipeline Stages**:
1. **Tests** (unit, integration) — Matrix: 3 projects × 2 Python versions
2. **Quality Gates** (linting, formatting) — Black, Flake8, Mypy
3. **Security Scans** (Gitleaks, Bandit, pip-audit)
4. **Docker Build** (multi-stage builds)
5. **Container Scan** (Trivy for vulnerabilities)
6. **E2E Tests** (full stack integration)
7. **Publish** (Docker images to GHCR on main branch)

### Trigger CI Manually

```bash
# Push to trigger CI
git push origin main

# Or create tag for release
git tag -a v1.5.0 -m "Release v1.5.0"
git push origin v1.5.0
```

### Debug CI Failures

1. **Check workflow logs**: GitHub Actions → Workflow → Job logs
2. **Reproduce locally**: Run same commands from `.github/workflows/ci-mlops.yml`
3. **Common failures**:
   - Tests: Check `pytest` output, review test files
   - Linting: Run `make lint` locally, fix issues
   - Docker: Check Dockerfile, verify base image availability

---

## 🎯 Deployment

### Local Deployment (Development)

```bash
# Already covered in "Start Full Demo Stack"
make docker-demo
```

### Kubernetes Deployment (Production)

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Verify pods running
kubectl get pods -l app=ml-mlops-portfolio

# Check service status
kubectl get svc

# Expected: 3 Deployments (bankchurn, carvision, telecomai) + 3 Services + 1 HPA
```

**Key K8s Resources**:
- `k8s/bankchurn-deployment.yaml` (3 replicas, HPA 2-10)
- `k8s/carvision-deployment.yaml` (2 replicas, HPA 2-8)
- `k8s/telecomai-deployment.yaml` (2 replicas, HPA 2-10)

### Terraform Deployment (AWS)

```bash
cd infra/terraform/aws

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -out=tfplan

# Apply (creates EKS, RDS, S3, ECR)
terraform apply tfplan

# Destroy (cleanup)
terraform destroy
```

---

## 📚 Additional Resources

### Documentation

- **[README.md](README.md)** — Portfolio overview
- **[QUICK_START.md](QUICK_START.md)** — 5-minute setup guide
- **[SECURITY.md](SECURITY.md)** — Security policy
- **[docs/ARCHITECTURE_PORTFOLIO.md](docs/ARCHITECTURE_PORTFOLIO.md)** — System architecture
- **[docs/OPERATIONS_PORTFOLIO.md](docs/OPERATIONS_PORTFOLIO.md)** — Detailed operations

### Project READMEs

- [BankChurn-Predictor/README.md](BankChurn-Predictor/README.md)
- [CarVision-Market-Intelligence/README.md](CarVision-Market-Intelligence/README.md)
- [TelecomAI-Customer-Intelligence/README.md](TelecomAI-Customer-Intelligence/README.md)

### Model Cards

- [BankChurn-Predictor/models/model_card.md](BankChurn-Predictor/models/model_card.md)
- [CarVision-Market-Intelligence/models/model_card.md](CarVision-Market-Intelligence/models/model_card.md)
- [TelecomAI-Customer-Intelligence/models/model_card.md](TelecomAI-Customer-Intelligence/models/model_card.md)

---

## 🆘 Support

### Internal Team

- **MLOps Lead**: Duque Ortega Mutis (DuqueOM)
- **Email**: DuqueOrtegaMutis@gmail.com
- **GitHub**: [@DuqueOM](https://github.com/DuqueOM)
- **LinkedIn**: [Duque Ortega Mutis](https://linkedin.com/in/duqueom)

### Emergency Contacts

For **critical production issues**:
- **Email**: DuqueOrtegaMutis@gmail.com
- **Response Time**: Within 24 hours

---

<div align="center">

**Runbook Version**: 2.0 | **Last Updated**: February 2026

⭐ **Production-Ready Operations** ⭐

[📖 Quick Start](QUICK_START.md) | [🏗️ Architecture](docs/ARCHITECTURE_PORTFOLIO.md) | [🔐 Security](SECURITY.md)

</div>
