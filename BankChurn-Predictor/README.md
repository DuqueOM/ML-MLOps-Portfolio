# BankChurn-Predictor

![CI Status](https://img.shields.io/github/actions/workflow/status/DuqueOM/ML-MLOps-Portfolio/ci-mlops.yml?branch=main)
![Coverage](https://img.shields.io/badge/Coverage-43%25-yellow)
![Python](https://img.shields.io/badge/Python-3.13-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![MLflow](https://img.shields.io/badge/MLflow-Tracking-blue)

> **TL;DR**: An enterprise-grade MLOps pipeline for predicting bank customer churn. It uses an ensemble of Logistic Regression and Random Forest, served via high-performance FastAPI, with full reproducibility via DVC and Make.

---

## 📋 Overview

BankChurn-Predictor is designed to identify customers at risk of leaving the bank (churn). By predicting churn probability, the bank can proactively engage high-risk customers with retention offers.

The system implements a complete MLOps lifecycle:
1.  **Data Validation**: Schema checks and drift detection.
2.  **Training Pipeline**: Reproducible training with `scikit-learn`, `imbalanced-learn` (SMOTE), and `optuna` for hyperparameter tuning.
3.  **Serving**: Asynchronous FastAPI application.
4.  **Observability**: MLflow for experiment tracking and logs.

### Key Features
- **Ensemble Model**: VotingClassifier combining linear and non-linear baselines.
- **Resampling Strategy**: Custom `ResampleClassifier` handling class imbalance (approx 20% churn rate).
- **Production-Ready API**: Typed Pydantic schemas, health checks, and batch prediction endpoints.
- **Reproducibility**: `dvc.yaml` pipelines and `Makefile` automation.

### Architecture High-Level
```mermaid
graph LR
    A[Raw Data (CSV)] --> B[Preprocessing (StandardScaler/OneHot)]
    B --> C[Training (VotingClassifier)]
    C --> D[Model Registry (MLflow/Local)]
    D --> E[FastAPI Service]
    E --> F[Prometheus/Logs]
    
    subgraph Training Pipeline
    B
    C
    end
    
    subgraph Serving
    E
    end
```

---

## 🚀 Quickstart

### Prerequisites
- Python 3.10+ (Tested on 3.13)
- Docker & Docker Compose
- Make

### Run in 5 Minutes
```bash
# 1. Install dependencies
make install

# 2. Train the model (uses default configs/config.yaml)
make train

# 3. Start the API
make api-start
```

### Verify
```bash
# Health check
curl localhost:8000/health

# Prediction
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

---

## 💾 Data

Input data is expected in CSV format. Key columns:

| Column | Type | Description |
|--------|------|-------------|
| CreditScore | int | Credit score (300-850) |
| Geography | str | France, Spain, Germany |
| Gender | str | Female, Male |
| Age | int | Customer age |
| Exited | int | **Target**: 1 (Churn), 0 (Retained) |

---

## 🧠 Training

The training pipeline is defined in `src/bankchurn/training.py` and orchestrated via `Makefile`.

```bash
# Standard training
make train

# With hyperparameter optimization (Coming Soon)
# make train-hyperopt
```

Configuration is managed in `configs/config.yaml`. You can adjust:
- `model.ensemble_voting`: 'soft' or 'hard'
- `data.target_column`: 'Exited'
- `model.test_size`: 0.2

---

## 📡 Serving

The API is built with FastAPI (`app/fastapi_app.py`).

- **POST /predict**: Real-time single prediction. Returns probability and risk level.
- **POST /predict_batch**: Batch processing (max 1000 records).
- **GET /metrics**: Operational metrics (latency, request count).

---

## 📊 Monitoring

- **Experiment Tracking**: MLflow logs params, metrics (F1, AUC), and artifacts.
- **Drift Detection**: `make check-drift` runs Evidently reports comparing reference vs current data.

---

## 🛠 Troubleshooting

| Symptom | Possible Cause | Resolution |
|---------|----------------|------------|
| `ModuleNotFoundError: src` | Python path issue | Run via `python -m` or use `make` commands which handle paths. |
| `Scaler mean equals global mean` | Data Leakage | Ensure `training.py` splits data *before* fitting preprocessor (Fixed in v1.0.0). |
| `Docker connection refused` | Port conflict | Check if port 8000 is used: `lsof -i :8000`. |

---

## 👥 Maintainers

- **Daniel Duque** - Lead MLOps Engineer

---

## ✅ Acceptance Checklist
- [x] Tests pass (`make test`)
- [x] API starts (`make api-start`)
- [x] Docker builds (`make docker-build`)
- [x] Linting clean (`make lint`)
