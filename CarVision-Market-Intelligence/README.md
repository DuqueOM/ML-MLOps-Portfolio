# CarVision Market Intelligence

[![CI/CD](https://github.com/DuqueOM/ML-MLOps-Portfolio/actions/workflows/ci-mlops.yml/badge.svg)](https://github.com/DuqueOM/ML-MLOps-Portfolio/actions)
[![Code Coverage](https://img.shields.io/badge/coverage-88%25-brightgreen)](reports/coverage.txt)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](Dockerfile)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 📋 TL;DR
**CarVision Market Intelligence** is an end-to-end MLOps solution for predicting vehicle market prices and analyzing automotive trends. It transforms raw classifieds data into actionable insights using a Random Forest regression model served via a scalable REST API and an interactive Streamlit dashboard.

**Key Features:**
- 🚀 **Production-Ready API:** FastAPI implementation with Pydantic validation and automatic feature engineering.
- 📊 **Interactive Dashboard:** Streamlit application for business intelligence, price estimation, and market trend visualization.
- 🛠 **MLOps Pipeline:** Modular package-based architecture (`src/carvision`) for reproducible training and evaluation.
- 🐳 **Containerized:** Optimized Docker builds with explicit PYTHONPATH handling for reliability.

---

## 🏗 Architecture

```mermaid
graph TD
    A[Raw Data (CSV)] -->|src.carvision.data| B(Cleaning & Splitting)
    B --> C(Training Pipeline)
    C -->|RandomForest| D[Model Artifacts]
    D --> E[Inference API (FastAPI)]
    D --> F[Dashboard (Streamlit)]
    E --> G[Client Applications]
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for a deep dive into components, data flow, and design decisions.

---

## ⚡ Quickstart

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Make

### 1. Run the Demo (One-Click)
Launch the full stack (API + Dashboard) using Docker:
```bash
# Build and start services
docker-compose up --build
```
Access:
- **Dashboard:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs

### 2. Local Development Setup
```bash
# 1. Create virtual environment and install dependencies
make setup
make install

# 2. Run training locally
make train

# 3. Run evaluation
make eval

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
           "fuel": "gas",
           "transmission": "automatic",
           "drive": "4wd",
           "type": "pickup",
           "paint_color": "white"
         }'
```

**Expected Response:**
```json
{
  "prediction": 24500.50
}
```

---

## 📦 Artifacts & Outputs
| Artifact | Path | Description |
|----------|------|-------------|
| Model | `artifacts/model.joblib` | Trained Scikit-learn Pipeline (Preprocessor + Regressor) |
| Metrics | `artifacts/metrics.json` | Evaluation metrics (RMSE, MAE, R2) |
| Feature Cols | `artifacts/feature_columns.json` | Schema definition for inference alignment |
| Executive Report | `reports/market_analysis.html` | HTML report with market insights |

---

## 🔧 Operations & Maintenance
See [OPERATIONS.md](OPERATIONS.md) for:
- 🔄 Retraining strategies
- 🚨 Monitoring & Alerts
- 🔙 Rollback procedures

---

## 👥 Maintainers
- **Lead MLOps:** Daniel Duque
- **Contact:** daniel.duque@example.com

---
*Generated via MLOps Documentation Standard v1.0*
