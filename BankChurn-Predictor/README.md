# BankChurn-Predictor

![CI Status](https://img.shields.io/github/actions/workflow/status/DuqueOM/ML-MLOps-Portfolio/ci-mlops.yml?branch=main)
![Coverage](https://img.shields.io/badge/Coverage-77%25-brightgreen)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![MLflow](https://img.shields.io/badge/MLflow-Tracking-blue)
![DVC](https://img.shields.io/badge/DVC-Enabled-945DD6)

> **TL;DR**: An enterprise-grade MLOps pipeline for predicting bank customer churn. It uses an ensemble of Logistic Regression and Random Forest, served via high-performance FastAPI, with full reproducibility via DVC and Make.

---

## 📋 Overview

BankChurn-Predictor is a production-grade Machine Learning service designed to identify customers at risk of leaving the bank (churn). By predicting churn probability, the bank can proactively engage high-risk customers with retention offers.

### Key Features
- **Robust Modeling**: VotingClassifier ensemble combining linear and non-linear baselines with custom resampling for class imbalance.
- **Production API**: Fast, typed, and documented REST API using FastAPI.
- **Reproducibility**: Full data and pipeline versioning with DVC and Git.
- **Observability**: Integrated MLflow tracking and drift monitoring.

### Architecture

```mermaid
graph LR
    A[Raw Data (CSV)] --> B[Preprocessing (StandardScaler/OneHot)]
    B --> C[Training Pipeline (Ensemble)]
    C --> D[Model Registry (MLflow/Local)]
    D --> E[Inference API (FastAPI)]
    E --> F[Monitoring (Prometheus/Logs)]
```

---

## 🚀 Quickstart

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- Make

### Run in 5 Minutes (Demo)

```bash
# 1. Install dependencies
make install

# 2. Start the full stack (API + Monitoring)
make docker-demo

# 3. Check health
curl localhost:8000/health
```

### Request Examples

**Single Prediction:**

```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
           "CreditScore": 600,
           "Geography": "France",
           "Gender": "Female",
           "Age": 40,
           "Tenure": 3,
           "Balance": 60000.0,
           "NumOfProducts": 2,
           "HasCrCard": 1,
           "IsActiveMember": 1,
           "EstimatedSalary": 50000.0
         }'
```

**Batch Prediction:**

```bash
# Assuming you have a json file with a list of customers
curl -X POST "http://localhost:8000/predict_batch" \
     -H "Content-Type: application/json" \
     -d @data/batch_request.json
```

---

## 💾 Data

| Column | Type | Description |
|--------|------|-------------|
| CreditScore | int | Credit score (300-850) |
| Geography | str | France, Spain, Germany |
| Gender | str | Female, Male |
| Age | int | Customer age |
| Exited | int | **Target**: 1 (Churn), 0 (Retained) |

Data is versioned using DVC. To pull the latest data:
```bash
dvc pull
```

---

## 🧠 Training

The training pipeline is reproducible and managed via `dvc.yaml` or `Makefile`.

```bash
# Run full training pipeline
make train

# Run with hyperparameter optimization
make train-hyperopt
```

**Expected Artifacts:**
- `models/best_model.pkl`: The full serialized scikit-learn pipeline (Preprocessor + Classifier).
- `models/metrics.json`: JSON file containing F1 score, AUC, and other evaluation metrics.
- `models/model_card.md`: Automated model card describing the model's provenance and performance.

---

## 📡 Serving

The API documentation (Swagger UI) is available at `http://localhost:8000/docs` when the service is running.

**Endpoints:**
- `GET /health`: Liveness probe checking model status.
- `POST /predict`: Real-time inference returning churn probability and risk level.
- `POST /predict_batch`: Bulk inference for up to 1000 records.
- `GET /metrics`: Prometheus-compatible metrics (latency, request count).

---

## 📊 Monitoring

- **Experiments**: View runs in MLflow (`http://localhost:5000`).
- **Drift**: Periodic checks compare live traffic against training reference using `evidently`.

---

## 🛠 Troubleshooting

| Issue | Possible Cause | Fix |
|-------|----------------|-----|
| `ModuleNotFoundError` | PYTHONPATH not set | Run via `python -m` or use `make` commands which handle paths. |
| `Connection Refused` | Docker container down | Check `docker ps` and logs `docker logs bankchurn-demo`. |
| `Scaler mean equals global mean` | Data Leakage | Ensure `training.py` splits data *before* fitting preprocessor (Fixed in v1.0.0). |

---

## 👥 Maintainers

- **Daniel Duque** - Lead MLOps Engineer

---

## ✅ Acceptance Checklist

- [x] Tests pass (`make test`)
- [x] API starts and responds (`make api-start`)
- [x] Docker image builds (`make docker-build`)
- [x] Security scan passes (`make security-scan`)
