# Runbook — ML/MLOps Portfolio

Quick reference for common operations. For detailed procedures, see [docs/ARCHITECTURE_PORTFOLIO.md](docs/ARCHITECTURE_PORTFOLIO.md).

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

## 🚀 Quick Commands

### Start Full Demo Stack
```bash
make docker-demo
```
Starts all 3 APIs + MLflow + monitoring dashboards

### Stop All Services
```bash
make docker-demo-down
```

### Individual Project Demos
```bash
# BankChurn Predictor
cd BankChurn-Predictor && make docker-demo

# CarVision Market Intelligence  
cd CarVision-Market-Intelligence && make docker-demo

# TelecomAI Customer Intelligence
cd TelecomAI-Customer-Intelligence && make docker-demo
```

---

## 📊 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **BankChurn API** | http://localhost:8001 | Customer churn prediction |
| **CarVision API** | http://localhost:8002 | Vehicle price prediction |
| **TelecomAI API** | http://localhost:8003 | Plan recommendation |
| **MLflow Tracking** | http://localhost:5000 | Experiment tracking |
| **CarVision Dashboard** | http://localhost:8501 | Streamlit dashboard |

---

## 🔧 Development Commands

### Environment Setup
```bash
# Install dependencies for all projects
make install

# Individual project setup
cd BankChurn-Predictor && make install
```

### Training Models
```bash
# Reproduce DVC pipelines for all projects
make dvc-repro

# Individual training
cd BankChurn-Predictor && make train
cd CarVision-Market-Intelligence && make train
cd TelecomAI-Customer-Intelligence && make train
```

### Testing
```bash
# Run all tests
make test

# Project-specific tests
cd BankChurn-Predictor && make test
```

### Code Quality
```bash
# Linting and formatting
make lint
make format

# Type checking
make type-check
```

---

## 🐳 Docker Operations

### Build Images
```bash
# Build all project images
make docker-build

# Individual image
cd BankChurn-Predictor && make docker-build
```

### Run Services
```bash
# Full stack with monitoring
docker-compose -f docker-compose.demo.yml up -d

# Individual service
docker run -p 8001:8000 ghcr.io/duqueom/bankchurn-api:latest
```

### Clean Docker Resources
```bash
docker-compose -f docker-compose.demo.yml down
docker system prune -f
```

---

## 📈 Monitoring & Logs

### View Logs
```bash
# All services
docker-compose -f docker-compose.demo.yml logs -f

# Specific service
docker-compose -f docker-compose.demo.yml logs -f bankchurn-api
```

### Health Checks
```bash
# All APIs
curl http://localhost:8001/health
curl http://localhost:8002/health  
curl http://localhost:8003/health

# MLflow
curl http://localhost:5000
```

### Metrics
```bash
# Prometheus metrics
curl http://localhost:8001/metrics
curl http://localhost:8002/metrics
curl http://localhost:8003/metrics
```

---

## 🔄 DVC Operations

### Data Versioning
```bash
# Pull datasets
dvc pull

# Push changes
dvc push

# Reproduce pipeline
dvc repro
```

### Status Check
```bash
# Check data status
dvc status

# List tracked files
dvc list
```

---

## 🚨 Troubleshooting

### Common Issues

**Port Conflicts**
```bash
# Check what's using ports
netstat -tulpn | grep :800
# Or use different ports in docker-compose.yml
```

**Memory Issues**
```bash
# Check Docker memory
docker system df
# Clean up unused images
docker system prune -a
```

**Permission Issues**
```bash
# Fix Docker permissions
sudo usermod -aG docker $USER
# Restart Docker service
sudo systemctl restart docker
```

**MLflow Connection**
```bash
# Check MLflow server
curl http://localhost:5000
# Restart MLflow
docker-compose restart mlflow
```

### Service Recovery
```bash
# Restart all services
docker-compose -f docker-compose.demo.yml restart

# Reset environment
docker-compose -f docker-compose.demo.yml down
docker system prune -f
make docker-demo
```

---

## 📝 Quick Reference

### Make Targets
```bash
make help           # Show all available targets
make docker-demo    # Start full stack
make docker-demo-down    # Stop all services  
make install        # Install dependencies
make test          # Run tests
make lint          # Code quality checks
make dvc-repro     # Reproduce DVC pipelines
```

### Environment Variables
```bash
export MLFLOW_TRACKING_URI=http://localhost:5000
export LOG_LEVEL=INFO
```

### Useful Paths
```
./logs/              # Application logs
./mlruns/            # MLflow experiments
./data/*/raw/        # Raw datasets
./models/            # Trained models
./artifacts/         # Training outputs
```

---

## 🆘 Emergency Procedures

### Full Reset
```bash
# Stop everything
docker-compose -f docker-compose.demo.yml down

# Clean all resources
docker system prune -a --volumes

# Restart from scratch
make docker-demo
```

### Data Recovery
```bash
# Restore datasets from DVC
dvc checkout

# Pull from remote if available
dvc pull -r origin
```

### Model Rollback
```bash
# Use previous model version
cd BankChurn-Predictor
git checkout HEAD~1 -- models/best_model.pkl
make docker-build
```

---

*For detailed architecture and procedures, refer to [docs/ARCHITECTURE_PORTFOLIO.md](docs/ARCHITECTURE_PORTFOLIO.md)*
