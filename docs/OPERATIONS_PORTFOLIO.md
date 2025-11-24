# Operations Portfolio - ML/MLOps Multi-Project

## Quick Start Guide

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
docker-compose -f docker-compose.demo.yml up --build

# Access services:
# - MLflow UI: http://localhost:5000
# - BankChurn API: http://localhost:8001/docs
# - CarVision API: http://localhost:8002/docs
# - CarVision Dashboard: http://localhost:8501
# - TelecomAI API: http://localhost:8003/docs
```

**Stop services**:
```bash
docker-compose -f docker-compose.demo.yml down
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
docker-compose -f docker-compose.demo.yml up -d

# Run integration tests
pytest tests/integration/test_demo.py -v

# Tear down
docker-compose -f docker-compose.demo.yml down
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
docker-compose -f docker-compose.demo.yml build
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
docker-compose -f docker-compose.demo.yml --profile monitoring up
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

**Prometheus Metrics**:
```bash
# Access Prometheus
open http://localhost:9090

# Example queries:
# - Request rate: rate(http_requests_total[5m])
# - Error rate: rate(http_requests_total{status=~"5.."}[5m])
```

**Grafana Dashboards**:
```bash
# Access Grafana
open http://localhost:3000
# Default credentials: admin/admin
```

### Logs

**Docker logs**:
```bash
# View logs for specific service
docker-compose -f docker-compose.demo.yml logs bankchurn

# Follow logs
docker-compose -f docker-compose.demo.yml logs -f carvision

# All services
docker-compose -f docker-compose.demo.yml logs
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
docker-compose -f docker-compose.demo.yml build --no-cache
```

#### Model Not Found
```bash
# Ensure model is trained first
cd <project>
python main.py --mode train

# Check artifacts directory
ls -la artifacts/
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
docker-compose -f docker-compose.demo.yml build
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

## Scaling Recommendations

### Horizontal Scaling
- Use Kubernetes HPA (Horizontal Pod Autoscaler)
- Target: CPU 70%, Memory 80%

### Vertical Scaling
- Increase container resources in K8s manifests
- Monitor with Prometheus/Grafana

### Database Scaling
- Move MLflow to PostgreSQL for production
- Implement connection pooling

## Disaster Recovery

1. **Regular backups**: Daily automated backups
2. **Multi-region deployment**: Deploy to multiple cloud regions
3. **Failover strategy**: Use load balancers with health checks
4. **Incident response**: Document runbooks for common issues
