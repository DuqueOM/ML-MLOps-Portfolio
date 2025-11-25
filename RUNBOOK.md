# Runbook — ML/MLOps Portfolio

Quick reference for common operations. For detailed procedures, see [docs/OPERATIONS_PORTFOLIO.md](docs/OPERATIONS_PORTFOLIO.md).

---

## Prerequisites

| Requirement | Version | Check Command |
|-------------|---------|---------------|
| Python | 3.11+ | `python --version` |
| Docker | 20.10+ | `docker --version` |
| Docker Compose | 2.0+ | `docker compose version` |
| Make | Any | `make --version` |
| Git | 2.30+ | `git --version` |

**System Requirements**: 8GB RAM, 20GB disk space

---

## Quick Commands

### 🚀 Start Full Demo (Recommended)

```bash
# 1. Generate demo models (first-time only)
bash scripts/setup_demo_models.sh

# 2. Start all services
make docker-demo
# or: docker-compose -f docker-compose.demo.yml up -d --build

# 3. Verify everything is running
make health-check
```

**Access Points:**
- 🏦 BankChurn API: http://localhost:8001/docs
- 🚗 CarVision API: http://localhost:8002/docs
- 🚗 CarVision Dashboard: http://localhost:8501
- 📱 TelecomAI API: http://localhost:8003/docs
- 📊 MLflow UI: http://localhost:5000

### 🛑 Stop Services

```bash
docker-compose -f docker-compose.demo.yml down

# With volume cleanup:
docker-compose -f docker-compose.demo.yml down -v
```

---

## Per-Project Commands

### BankChurn-Predictor

```bash
cd BankChurn-Predictor

# Install
pip install -r requirements.txt

# Train
python main.py --mode train --config configs/config.yaml

# Run API
uvicorn app.fastapi_app:app --host 0.0.0.0 --port 8000

# Test prediction
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"CreditScore":650,"Geography":"France","Gender":"Female","Age":40,"Tenure":3,"Balance":60000,"NumOfProducts":2,"HasCrCard":1,"IsActiveMember":1,"EstimatedSalary":50000}'
```

### CarVision-Market-Intelligence

```bash
cd CarVision-Market-Intelligence

# Install
pip install -r requirements.txt

# Train
python main.py --mode train --config configs/config.yaml

# Run API
uvicorn app.fastapi_app:app --host 0.0.0.0 --port 8000

# Run Dashboard
streamlit run app/streamlit_app.py --server.port 8501

# Test prediction
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"model_year":2018,"odometer":45000,"model":"ford f-150","fuel":"gas","transmission":"automatic"}'
```

### TelecomAI-Customer-Intelligence

```bash
cd TelecomAI-Customer-Intelligence

# Install
pip install -r requirements.txt

# Train
python main.py --mode train

# Run API
uvicorn app.fastapi_app:app --host 0.0.0.0 --port 8000

# Test prediction
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"calls":40.0,"minutes":311.9,"messages":83.0,"mb_used":19915.42}'
```

---

## Testing

### Run All Tests

```bash
# From project root
make test

# With coverage
pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Integration Tests

```bash
# Start demo stack first
docker-compose -f docker-compose.demo.yml up -d --build

# Run integration tests
pytest tests/integration/test_demo.py -v

# Cleanup
docker-compose -f docker-compose.demo.yml down
```

---

## MLflow

### Start MLflow Server

```bash
# Local file-based tracking
mlflow ui --backend-store-uri file:./mlruns --port 5000

# Or use Docker Compose stack
docker-compose -f docker-compose.mlflow.yml up -d
```

### View Experiments

```bash
# List experiments
mlflow experiments list

# View runs
mlflow runs list --experiment-id 0
```

---

## Docker Operations

### Build Individual Images

```bash
# BankChurn
docker build -t bankchurn:latest ./BankChurn-Predictor

# CarVision
docker build -t carvision:latest ./CarVision-Market-Intelligence

# TelecomAI
docker build -t telecomai:latest ./TelecomAI-Customer-Intelligence
```

### Push to GHCR

```bash
# Login
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Tag and push
docker tag bankchurn:latest ghcr.io/duqueom/bankchurn-api:latest
docker push ghcr.io/duqueom/bankchurn-api:latest
```

### Pull from GHCR

```bash
docker pull ghcr.io/duqueom/bankchurn-api:latest
docker run -p 8000:8000 ghcr.io/duqueom/bankchurn-api:latest
```

---

## Security Scans

```bash
# Python security (Bandit)
bandit -r . -f json -o bandit-report.json

# Docker image scan (Trivy)
docker run --rm aquasec/trivy image bankchurn:latest

# Secrets detection (Gitleaks)
gitleaks detect --source . --report-path gitleaks-report.json
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError` | PYTHONPATH not set | Run via `python -m` or use Makefile |
| `Connection Refused` | Container not running | `docker ps` and check logs |
| `Model not found` | Missing artifact | Run training first: `make train` |
| `Port already in use` | Another service running | `lsof -i :8000` and kill process |
| Docker build fails | Cache corruption | `docker system prune -a` |

### View Container Logs

```bash
# All services
docker-compose -f docker-compose.demo.yml logs -f

# Specific service
docker-compose -f docker-compose.demo.yml logs -f bankchurn
```

### Reset Everything

```bash
# Stop and remove all containers, networks, volumes
docker-compose -f docker-compose.demo.yml down -v --rmi all

# Remove Python caches
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type d -name .pytest_cache -exec rm -rf {} +

# Re-install dependencies
make install
```

### CI Pipeline Debug

- **Workflow file**: `.github/workflows/ci-mlops.yml`
- **Jobs**: `tests` → `coverage` → `docker-build` → `e2e`
- **If tests fail**: Check job logs, expand `coverage-report` artifact
- **If Docker fails**: Check if base image is available, review build cache

---

## Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Key variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `SEED` | Reproducibility seed | `42` |
| `MLFLOW_TRACKING_URI` | MLflow server URL | `file:./mlruns` |
| `API_HOST` | API bind address | `0.0.0.0` |
| `API_PORT` | API port | `8000` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

---

## Useful Links

- **Architecture**: [docs/ARCHITECTURE_PORTFOLIO.md](docs/ARCHITECTURE_PORTFOLIO.md)
- **Operations**: [docs/OPERATIONS_PORTFOLIO.md](docs/OPERATIONS_PORTFOLIO.md)
- **Releases**: [docs/RELEASE.md](docs/RELEASE.md)
- **Dependencies**: [docs/DEPENDENCY_CONFLICTS.md](docs/DEPENDENCY_CONFLICTS.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
