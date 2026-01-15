# {PROJECT_NAME}

[![CI/CD](https://github.com/{REPO_OWNER}/{REPO_NAME}/actions/workflows/ci-mlops.yml/badge.svg)](https://github.com/{REPO_OWNER}/{REPO_NAME}/actions)
[![Code Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen)](reports/coverage.txt)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](Dockerfile)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 📋 TL;DR
{PROJECT_DESCRIPTION}

**Key Features:**
- 🚀 **Production-Ready API:** FastAPI implementation with Pydantic validation.
- 📊 **Interactive Dashboard:** Streamlit application for business intelligence.
- 🛠 **MLOps Pipeline:** Automated training, evaluation, and versioning (DVC + MLflow).
- 🐳 **Containerized:** Optimized Docker builds for training and inference.

---

## 🏗 Architecture

```mermaid
graph TD
    A[Raw Data] -->|DVC| B(Preprocessing)
    B --> C(Training Pipeline)
    C -->|MLflow| D[Model Registry]
    D --> E[Inference API (FastAPI)]
    D --> F[Dashboard (Streamlit)]
    E --> G[Prometheus Metrics]
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for a deep dive into components and decision logs.

---

## ⚡ Quickstart

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Make

### 1. Run the Demo (One-Click)
Launch the full stack (API + Dashboard):
```bash
make start-demo
```
Access:
- **Dashboard:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs

### 2. Local Development Setup
```bash
# 1. Create virtual environment
make setup

# 2. Install dependencies
make install

# 3. Run training locally
make train

# 4. Run tests
make test
```

---

## 📡 API Usage

**Predict Price:**
```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
           "model_year": 2018,
           "model": "ford f-150",
           "condition": "good",
           "odometer": 50000,
           "cylinders": 6,
           "fuel": "gas"
         }'
```

---

## 📦 Artifacts & Outputs
| Artifact | Path | Description |
|----------|------|-------------|
| Model | `artifacts/model.joblib` | Trained pipeline (Preprocessor + Regressor) |
| Metrics | `artifacts/metrics.json` | Evaluation metrics (RMSE, MAE, R2) |
| Feature Cols | `artifacts/feature_columns.json` | Schema definition for inference |

---

## 🔧 Operations & Maintenance
See [OPERATIONS.md](OPERATIONS.md) for:
- 🔄 Retraining strategies
- 🚨 Monitoring & Alerts
- 🔙 Rollback procedures

---

## 👥 Maintainers
- **Lead MLOps:** Duque Ortega Mutis (DuqueOM)
- **Contact:** contact@duqueom.dev

---
*Generated via MLOps Documentation Standard v1.0*
