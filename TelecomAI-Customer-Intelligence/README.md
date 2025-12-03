# TelecomAI Customer Intelligence

[![CI Status](https://img.shields.io/github/actions/workflow/status/DuqueOM/ML-MLOps-Portfolio/ci-mlops.yml?branch=main&label=CI)](https://github.com/DuqueOM/ML-MLOps-Portfolio/actions/workflows/ci-mlops.yml)
[![Coverage](https://img.shields.io/badge/Coverage-97%25-brightgreen)](../reports/)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](Dockerfile)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)

---

<div align="center">

![TelecomAI Demo](../media/gifs/telecom-preview.gif)

### 📺 Portfolio Demo

[![YouTube Demo](https://img.shields.io/badge/YouTube-Watch%20Demo-red?style=for-the-badge&logo=youtube)](https://youtu.be/qmw9VlgUcn8)

</div>

---

## TL;DR

A production-ready ML system for predicting telecom customer plan preferences using Scikit-Learn and FastAPI. Features automated pipelines, Dockerized inference, and comprehensive testing.

### Key Features
- **Production API**: FastAPI with Prometheus metrics endpoint for observability.
- **High Coverage**: 97% test coverage with comprehensive unit and integration tests.
- **Containerized**: Docker-ready with optimized multi-stage builds.
- **Observability**: Prometheus metrics (`/metrics`) for production monitoring.

## Quickstart

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Make

### One-Click Demo
```bash
make docker-demo
# API available at http://localhost:8000
```

### Local Development
```bash
# Install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Train model
python main.py --mode train

# Run API
uvicorn app.fastapi_app:app --reload
```

## Architecture

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed component diagrams and design decisions.

## Operations

See [OPERATIONS.md](docs/OPERATIONS.md) for runbooks, monitoring, and deployment guides.

## API Reference

### Predict Endpoint
`POST /predict`

**Request:**
```json
{
  "calls": 40.0,
  "minutes": 311.9,
  "messages": 83.0,
  "mb_used": 19915.42
}
```

**Response:**
```json
{
  "prediction": 0,
  "probability_is_ultra": 0.12
}
```

## Artifacts & Data

| Artifact | Location | Description |
|----------|----------|-------------|
| **Model** | `artifacts/model.joblib` | Trained pipeline (preprocessor + classifier) |
| **Metrics** | `artifacts/metrics.json` | Evaluation metrics (AUC, Accuracy, F1) |
| **Data** | `data/raw/users_behavior.csv` | User behavior dataset (managed via DVC) |

---

## 📊 MLflow Integration

This project integrates with MLflow for experiment tracking with **3 tracked experiments** comparing different classification approaches.

### Tracked Experiments

| Run | Model | Test Accuracy | Test F1 | Purpose |
|-----|-------|---------------|---------|--------|
| TL-1_Baseline_LogReg | LogisticRegression | 0.74 | 0.30 | Baseline |
| TL-2_GradientBoosting_Tuned | GradientBoosting | 0.81 | 0.63 | Tuned |
| **TL-3_RandomForest** | RandomForest | **0.82** | **0.63** | Best model |

### Run Experiments

```bash
# Point to the portfolio's central MLflow server
export MLFLOW_TRACKING_URI=http://localhost:5000

# Run all TelecomAI experiments (from portfolio root)
python scripts/run_experiments.py
```

### What Gets Logged

| Category | Items |
|----------|-------|
| **Parameters** | n_estimators, max_depth, learning_rate |
| **Metrics** | train/test accuracy, F1, ROC-AUC |
| **Tags** | run_type (baseline/tuned/alternative), project |

### Full Portfolio Demo (with MLflow UI)

Run all 3 projects from the portfolio root:

```bash
cd ..  # Go to portfolio root
docker compose -f docker-compose.demo.yml up --build -d

# Access points:
# - TelecomAI API: http://localhost:8003/docs
# - MLflow UI: http://localhost:5000
```

---

## 📋 CI Notes

| Component | Details |
|-----------|---------|
| **Workflow** | `.github/workflows/ci-mlops.yml` |
| **Coverage** | 97% (threshold: 80%) |
| **Python** | 3.11, 3.12 (matrix) |

**If tests fail**: Check the `tests` job logs → expand coverage artifact.

---

## 📄 Model Card

See [models/model_card.md](models/model_card.md) for:
- Model architecture (VotingClassifier ensemble)
- Performance metrics (AUC-ROC, Accuracy, F1-Score)
- Feature descriptions and data requirements
- Reproduction instructions

---

## ✅ Acceptance Checklist

- [x] Tests pass (`pytest`)
- [x] API starts and responds
- [x] Docker image builds
- [x] Model card documented

---

## 👥 Maintainers

- **Daniel Duque** - Lead MLOps Engineer - [GitHub](https://github.com/DuqueOM)
