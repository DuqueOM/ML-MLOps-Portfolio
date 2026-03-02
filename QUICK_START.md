# 🚀 Quick Start — ML/MLOps Portfolio

<div align="center">

**Get Started in 5 Minutes**

![Docker](https://img.shields.io/badge/Docker-Required-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![Make](https://img.shields.io/badge/Make-Included-orange)
![Last Updated](https://img.shields.io/badge/updated-March%202026-blue)

</div>

---

## ⚡ One-Command Demo (Recommended)

Start the **entire portfolio stack** (3 ML APIs + Dashboard + MLflow) with a single command:

```bash
make docker-demo
```

**What this does**:
1. ✅ Builds optimized Docker images for all 3 projects
2. ✅ Starts MLflow Tracking Server (experiment management)
3. ✅ Launches BankChurn, CarVision, NLPInsight APIs
4. ✅ Starts CarVision Streamlit Dashboard
5. ✅ Runs automated health checks

**Access Points** (available after `make docker-demo`):

| Service | URL | Description |
|---------|-----|-------------|
| **🏦 BankChurn API** | [http://localhost:8001/docs](http://localhost:8001/docs) | Churn prediction (Swagger UI) |
| **🚗 CarVision API** | [http://localhost:8002/docs](http://localhost:8002/docs) | Vehicle pricing (Swagger UI) |
| **🚗 CarVision Dashboard** | [http://localhost:8501](http://localhost:8501) | Interactive analytics (Streamlit) |
| **📝 NLPInsight API** | [http://localhost:8003/docs](http://localhost:8003/docs) | Sentiment analysis (Swagger UI) |
| **📊 MLflow UI** | [http://localhost:5000](http://localhost:5000) | Experiment tracking |

---

## 📺 Video Walkthrough

Watch the complete portfolio demonstration:

[![YouTube Demo](https://img.shields.io/badge/YouTube-Watch%20Demo-red?style=for-the-badge&logo=youtube)](https://youtu.be/qmw9VlgUcn8)

**Topics Covered**: Architecture, API usage, Dashboard features, MLflow experiments, deployment

---

## 🎯 Quick API Examples

### BankChurn Prediction

```bash
curl -X POST "http://localhost:8001/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "CreditScore": 650, "Geography": "France", "Gender": "Female",
       "Age": 40, "Tenure": 3, "Balance": 60000, "NumOfProducts": 2,
       "HasCrCard": 1, "IsActiveMember": 1, "EstimatedSalary": 50000
     }'

# Response: {"churn_probability": 0.23, "churn_prediction": 0, "risk_level": "LOW"}
```

### CarVision Price Prediction

```bash
curl -X POST "http://localhost:8002/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "model_year": 2018, "odometer": 45000, "model": "ford f-150",
       "fuel": "gas", "transmission": "automatic"
     }'

# Response: {"predicted_price": 24500.0, "vehicle_age": 8, "brand": "ford"}
```

### NLPInsight Sentiment Analysis

```bash
curl -X POST "http://localhost:8003/predict" \
     -H "Content-Type: application/json" \
     -d '{"text": "The company reported strong quarterly earnings growth"}'

# Response: {"label": "positive", "confidence": 0.92, "scores": {"positive": 0.92, "neutral": 0.06, "negative": 0.02}}
```

---

## 🛠️ Prerequisites

### System Requirements

| Component | Version | Check Command |
|-----------|---------|---------------|
| **Docker** | 20.10+ | `docker --version` |
| **Docker Compose** | 2.0+ | `docker compose version` |
| **Python** | 3.11+ | `python --version` |
| **Make** | Any | `make --version` |

**Resources**: 8GB RAM minimum, 20GB disk space

### Installation

```bash
# Clone repository
git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git
cd ML-MLOps-Portfolio

# Install dependencies (optional, for local development)
make install
```

---

## 📊 MLflow Experiment Tracking

### View Experiments

After starting the demo stack, open [http://localhost:5000](http://localhost:5000) to see:

- **3 Experiments**: BankChurn, CarVision, NLPInsight
- **Performance Metrics**: F1-Score, AUC-ROC, Accuracy, RMSE
- **Business Metrics**: Revenue impact, retention estimates
- **Model Artifacts**: Config files, model checkpoints

### Log New Experiments

```bash
# Set MLflow tracking URI
export MLFLOW_TRACKING_URI=http://localhost:5000

# Run experiments from each project
cd BankChurn-Predictor && make mlflow-demo && cd ..
cd CarVision-Market-Intelligence && make mlflow-demo && cd ..
cd NLPInsight-Analyzer && make mlflow-demo && cd ..
```

**Results**: New runs appear in MLflow UI with full lineage (params, metrics, artifacts)

---

## ✅ Validation & Testing

### Health Checks

```bash
# Verify all services are running
make health-check

# Or manually:
curl http://localhost:8001/health  # BankChurn
curl http://localhost:8002/health  # CarVision
curl http://localhost:8003/health  # NLPInsight
```

**Expected**: `{"status": "healthy", "model_loaded": true, "model_version": "..."}`

### Integration Tests

```bash
# Ensure demo stack is running
docker compose -f docker-compose.demo.yml up -d

# Run comprehensive integration tests
pytest tests/integration/test_demo.py -v

# Expected: 15+ tests pass (health checks, predictions, schema validation)
```

---

## 🛑 Stop & Cleanup

### Stop Services

```bash
# Stop all containers
docker compose -f docker-compose.demo.yml down

# Stop + remove volumes (clean slate)
docker compose -f docker-compose.demo.yml down -v
```

### View Logs

```bash
# All services
docker compose -f docker-compose.demo.yml logs -f

# Specific service
docker compose -f docker-compose.demo.yml logs -f bankchurn
```

---

## 🔧 Local Development

For detailed development instructions, see:

- **[Operations Runbook](RUNBOOK.md)** — Day-to-day operations
- **[Architecture Docs](docs/ARCHITECTURE_PORTFOLIO.md)** — System design
- **Project READMEs** — Individual project setup
  - [BankChurn-Predictor/README.md](BankChurn-Predictor/README.md)
  - [CarVision-Market-Intelligence/README.md](CarVision-Market-Intelligence/README.md)
  - [NLPInsight-Analyzer/README.md](NLPInsight-Analyzer/README.md)

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Port already in use** | Kill existing process: `lsof -i :8001` (or 8002, 8003) |
| **Container not starting** | Check logs: `docker compose logs <service>` |
| **Model not found** | Run `bash scripts/setup_demo_models.sh` first |
| **Connection refused** | Wait 30s after `docker-compose up` for services to start |
| **Out of memory** | Increase Docker memory limit (8GB minimum) |

---

## 📚 Next Steps

1. **Explore the Dashboard**: Open [http://localhost:8501](http://localhost:8501) for interactive analytics
2. **Review Experiments**: Check [http://localhost:5000](http://localhost:5000) for model comparisons
3. **Read Documentation**: See [docs/](docs/) for architecture, operations, and deployment
4. **Customize Models**: Modify configs in each project's `configs/config.yaml`
5. **Deploy to Production**: Follow guides in [docs/OPERATIONS_PORTFOLIO.md](docs/OPERATIONS_PORTFOLIO.md)

---

<div align="center">

**Quick Start Version**: 2.0 | **Last Updated**: February 2026

⭐ **Production-Ready ML Portfolio** ⭐

[📖 Full Documentation](README.md) | [🔧 Operations](RUNBOOK.md) | [🏗️ Architecture](docs/ARCHITECTURE_PORTFOLIO.md)

</div>
