# BankChurn-Predictor

[![CI Status](https://img.shields.io/github/actions/workflow/status/DuqueOM/ML-MLOps-Portfolio/ci-mlops.yml?branch=main&label=CI)](https://github.com/DuqueOM/ML-MLOps-Portfolio/actions/workflows/ci-mlops.yml)
[![Coverage](https://img.shields.io/badge/Coverage-79%25-brightgreen)](../reports/)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](Dockerfile)
[![MLflow](https://img.shields.io/badge/MLflow-Tracking-0194E2?logo=mlflow&logoColor=white)](https://mlflow.org)
[![DVC](https://img.shields.io/badge/DVC-Enabled-945DD6)](https://dvc.org)

---

<div align="center">

![BankChurn Demo](../media/gifs/bankchurn-preview.gif)

### 📺 Portfolio Demo

[![YouTube Demo](https://img.shields.io/badge/YouTube-Watch%20Demo-red?style=for-the-badge&logo=youtube)](https://youtu.be/qmw9VlgUcn8)

</div>

---

> **TL;DR**: An enterprise-grade MLOps pipeline for predicting bank customer churn. Features a unified sklearn Pipeline with ensemble classifiers (LogisticRegression + RandomForest), configurable resampling for class imbalance, served via high-performance FastAPI, with full experiment tracking via MLflow and reproducibility via DVC.

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
- `artifacts/training_results.json`: JSON file containing F1 score, AUC, and other evaluation metrics.
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

## 📊 MLflow Integration

This project integrates with MLflow for experiment tracking with **3 tracked experiments** demonstrating model comparison.

![MLflow Experiments](../media/screenshots/mlflow-experiments.PNG)

### Tracked Experiments

| Run | Model | Test F1 | Test AUC | Purpose |
|-----|-------|---------|----------|--------|
| BC-1_Baseline | LogisticRegression | 0.29 | 0.77 | Simple baseline |
| **BC-2_RandomForest_Tuned** | RandomForest (balanced) | **0.64** | **0.87** | Best model |
| BC-3_Overfit_Demo | RF (no regularization) | 0.58 | 0.85 | Overfitting demo |

### Run Experiments

```bash
# Point to the portfolio's central MLflow server
export MLFLOW_TRACKING_URI=http://localhost:5000

# Run all BankChurn experiments (from portfolio root)
python scripts/run_experiments.py
```

### What Gets Logged

| Category | Items |
|----------|-------|
| **Parameters** | n_estimators, max_depth, min_samples_split, class_weight |
| **Metrics** | train/test accuracy, F1, ROC-AUC |
| **Tags** | run_type (baseline/tuned/overfit), project |

### Full Portfolio Demo (with MLflow UI)

Run all 3 projects from the portfolio root:

```bash
cd ..  # Go to portfolio root
docker compose -f docker-compose.demo.yml up --build -d

# Access points:
# - BankChurn API: http://localhost:8001/docs
# - MLflow UI: http://localhost:5000
```

### Drift Monitoring

Periodic drift checks compare live traffic against training reference using `evidently`:

```bash
make check-drift
```

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

## 📋 CI Notes

| Component | Details |
|-----------|---------|
| **Workflow** | `.github/workflows/ci-mlops.yml` |
| **Coverage** | 79.5% (threshold: 79%) |
| **Python** | 3.11, 3.12 (matrix) |

**If tests fail**: Check the `tests` job logs → expand coverage artifact.

---

## 📄 Model Card

See [models/model_card.md](models/model_card.md) for:
- Model architecture and training data
- Performance metrics (AUC, F1, Precision, Recall)
- Limitations and bias considerations
- Reproduction instructions

---

## ✅ Acceptance Checklist

- [x] Tests pass (`make test`)
- [x] API starts and responds (`make api-start`)
- [x] Docker image builds (`make docker-build`)
- [x] Security scan passes (`make security-scan`)
- [x] Model card documented
