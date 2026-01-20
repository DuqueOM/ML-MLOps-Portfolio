# 🚀 Quick Start Guide

Get the ML-MLOps Portfolio running in **under 5 minutes**.

---

## Prerequisites

| Component | Version | Check Command |
|-----------|---------|---------------|
| **Docker** | 20.10+ | `docker --version` |
| **Docker Compose** | 2.0+ | `docker compose version` |
| **Git** | 2.30+ | `git --version` |

**System Requirements**: 8GB RAM minimum, 20GB disk space

---

## ⚡ One-Command Demo

```bash
# 1. Clone repository
git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git
cd ML-MLOps-Portfolio

# 2. Generate demo models (first-time only)
bash scripts/setup_demo_models.sh

# 3. Start full demo stack
docker-compose -f docker-compose.demo.yml up -d --build

# 4. Verify services (wait 30s for startup)
docker-compose -f docker-compose.demo.yml ps
```

---

## 🌐 Access Points

Once the stack is running, access the services:

| Service | URL | Description |
|---------|-----|-------------|
| **🏦 BankChurn API** | [http://localhost:8001/docs](http://localhost:8001/docs) | Churn prediction (Swagger UI) |
| **🚗 CarVision API** | [http://localhost:8002/docs](http://localhost:8002/docs) | Vehicle pricing (Swagger UI) |
| **🚗 CarVision Dashboard** | [http://localhost:8501](http://localhost:8501) | Interactive analytics (Streamlit) |
| **📱 TelecomAI API** | [http://localhost:8003/docs](http://localhost:8003/docs) | Plan recommendation (Swagger UI) |
| **📊 MLflow UI** | [http://localhost:5000](http://localhost:5000) | Experiment tracking |

---

## 🧪 Test the APIs

### BankChurn Prediction

```bash
curl -X POST "http://localhost:8001/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "CreditScore": 650, "Geography": "France", "Gender": "Female",
    "Age": 40, "Tenure": 3, "Balance": 60000, "NumOfProducts": 2,
    "HasCrCard": 1, "IsActiveMember": 1, "EstimatedSalary": 50000
  }'
```

**Expected Response**:
```json
{
  "churn_probability": 0.23,
  "churn_prediction": 0,
  "risk_level": "LOW",
  "confidence": "HIGH"
}
```

### CarVision Price Prediction

```bash
curl -X POST "http://localhost:8002/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "model_year": 2018, "odometer": 45000, "model": "ford f-150",
    "fuel": "gas", "transmission": "automatic"
  }'
```

**Expected Response**:
```json
{
  "predicted_price": 24500.0,
  "vehicle_age": 8,
  "brand": "ford",
  "confidence_interval_95": [22300, 26700]
}
```

### TelecomAI Plan Recommendation

```bash
curl -X POST "http://localhost:8003/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "calls": 40.0, "minutes": 311.9, "messages": 83.0, "mb_used": 19915.42
  }'
```

**Expected Response**:
```json
{
  "prediction": 0,
  "probability_is_ultra": 0.12,
  "confidence": "HIGH",
  "recommendation": "Smart plan ($40/mo) is optimal"
}
```

---

## ✅ Health Checks

Verify all services are running:

```bash
# Quick health check (all services)
curl http://localhost:8001/health  # BankChurn
curl http://localhost:8002/health  # CarVision
curl http://localhost:8003/health  # TelecomAI

# Expected response from each:
# {"status": "healthy", "model_loaded": true, "model_version": "1.5.0"}
```

---

## 🧪 Run Integration Tests

Verify the full stack is working correctly:

```bash
# Run comprehensive integration tests
pytest tests/integration/test_demo.py -v

# Or use shell script (legacy)
bash scripts/run_demo_tests.sh
```

**Expected**: 15+ tests pass (health checks, predictions, schema validation)

---

## 🛑 Stop the Demo

```bash
# Stop all containers
docker-compose -f docker-compose.demo.yml down

# Stop + remove volumes (clean slate)
docker-compose -f docker-compose.demo.yml down -v
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Port already in use** | Kill process: `lsof -i :8001` (or 8002, 8003, 8501, 5000) |
| **Container not starting** | Check logs: `docker-compose -f docker-compose.demo.yml logs <service>` |
| **Model not found** | Run `bash scripts/setup_demo_models.sh` first |
| **Connection refused** | Wait 30s after startup for services to initialize |
| **Out of memory** | Increase Docker memory limit (8GB minimum) |

### View Logs

```bash
# All services (real-time)
docker-compose -f docker-compose.demo.yml logs -f

# Specific service
docker-compose -f docker-compose.demo.yml logs -f bankchurn

# Last 50 lines
docker-compose -f docker-compose.demo.yml logs --tail=50
```

---

## 📚 Next Steps

1. **Explore the Dashboard**: Open [CarVision Streamlit Dashboard](http://localhost:8501) for interactive analytics
2. **Review Experiments**: Check [MLflow UI](http://localhost:5000) for model comparisons (9 tracked runs)
3. **Read Documentation**:
   - [Installation Guide](installation.md) — Detailed setup instructions
   - [Development Setup](development.md) — Local development environment
   - [Project Overview](../projects/overview.md) — Deep dive into each project
   - [Architecture](../architecture/overview.md) — System design and data flow
4. **Customize Models**: Modify configs in each project's `configs/config.yaml`
5. **Deploy to Production**: Follow [Operations Guide](../operations/deployment.md)

---

!!! tip "For Recruiters"
    **Quick evaluation path**:
    
    1. Start demo stack (3 minutes)
    2. Explore [Streamlit Dashboard](http://localhost:8501) (interactive UI)
    3. Test APIs via [Swagger UI](http://localhost:8001/docs)
    4. Review [MLflow experiments](http://localhost:5000)
    5. Check [Model Cards](../models/catalog.md) for technical depth

!!! info "Video Walkthrough"
    Prefer video? Watch the complete portfolio demonstration:
    
    [![YouTube Demo](https://img.shields.io/badge/YouTube-Watch%20Demo-red?style=for-the-badge&logo=youtube)](https://youtu.be/qmw9VlgUcn8)

---

**Last Updated**: March 2026
