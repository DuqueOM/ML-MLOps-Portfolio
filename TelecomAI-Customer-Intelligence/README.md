# TelecomAI Customer Intelligence

[![CI/CD](https://github.com/DuqueOM/ML-MLOps-Portfolio/actions/workflows/ci-mlops.yml/badge.svg)](https://github.com/DuqueOM/ML-MLOps-Portfolio/actions)
[![Code Coverage](https://img.shields.io/badge/coverage-82%25-brightgreen)](reports/coverage.txt)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](Dockerfile)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 📋 TL;DR
**TelecomAI Customer Intelligence** is a production-grade machine learning system for classifying customer plan preferences ("Smart" vs. "Ultra"). It features a modular architecture (`src/telecom`), a unified Scikit-learn pipeline for training and serving, and a high-performance FastAPI inference engine.

**Key Features:**
- 🧠 **Unified Pipeline:** Feature engineering and classification logic are bundled in a single artifact to prevent training-serving skew.
- 🚀 **FastAPI Serving:** Low-latency inference with automatic Swagger documentation and Pydantic validation.
- 📦 **Modular Design:** Clean separation of concerns (Data, Training, Evaluation, Prediction) in a pythonic package structure.
- 🐳 **Dockerized:** Reproducible environments for both training and inference.

---

## 🏗 Architecture

```mermaid
graph TD
    A[Raw Data (CSV)] -->|src.telecom.data| B(Data Loading & Split)
    B -->|src.telecom.training| C(Pipeline Construction)
    C -->|StandardScaler + Classifier| D[Model Artifact (model.joblib)]
    D -->|src.telecom.evaluation| E[Metrics JSON]
    D -->|app.fastapi_app| F[Inference API]
    F --> G[Client Request]
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed component breakdown and design decisions.

---

## ⚡ Quickstart

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Make

### 1. Run the Demo (One-Click)
Launch the API server:
```bash
make start-demo
```
Access:
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### 2. Local Development Setup
```bash
# 1. Create virtual environment & Install
make setup
make install

# 2. Run training locally
python main.py --mode train --config configs/config.yaml

# 3. Run evaluation
python main.py --mode eval --config configs/config.yaml

# 4. Run tests
pytest tests/
```

---

## 📡 API Usage

**Predict Plan Preference:**
```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
           "calls": 40,
           "minutes": 350.5,
           "messages": 12,
           "mb_used": 8500.0
         }'
```

**Expected Response:**
```json
{
  "prediction": 0,
  "probability_is_ultra": 0.15
}
```
*(0 = Smart, 1 = Ultra)*

---

## 📦 Artifacts & Outputs
| Artifact | Path | Description |
|----------|------|-------------|
| Model Pipeline | `artifacts/model.joblib` | Full Scikit-learn Pipeline (Preprocessor + Model) |
| Metrics | `artifacts/metrics.json` | Accuracy, Precision, Recall, F1, ROC-AUC |
| Confusion Matrix | `artifacts/confusion_matrix.png` | Visual performance evaluation |

---

## 🔧 Operations & Maintenance
See [OPERATIONS.md](OPERATIONS.md) for:
- 🔄 Retraining triggers
- 🚨 Alerting thresholds
- 🔙 Rollback procedures

---

## 👥 Maintainers
- **Lead MLOps:** Daniel Duque
- **Contact:** daniel.duque@example.com

---
*Generated via MLOps Documentation Standard v1.0*
