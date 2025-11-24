# TelecomAI Customer Intelligence

[![CI](https://github.com/DuqueOM/ML-MLOps-Portfolio/actions/workflows/ci-mlops.yml/badge.svg)](https://github.com/DuqueOM/ML-MLOps-Portfolio/actions)
[![Coverage](https://img.shields.io/badge/coverage-96%25-green)](reports/coverage.txt)
[![Python](https://img.shields.io/badge/python-3.11-blue)](pyproject.toml)

## TL;DR

A production-ready ML system for predicting telecom customer churn/plan upgrades using Scikit-Learn and FastAPI. Features automated pipelines, Dockerized inference, and comprehensive testing.

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
- **Model:** `artifacts/model.joblib`
- **Metrics:** `artifacts/metrics.json`
- **Data:** `users_behavior.csv` (Managed via DVC)

## Maintainers
- **Lead MLOps:** [Your Name/Contact]
