# {PROJECT_NAME}

[![CI](https://github.com/DuqueOM/ML-MLOps-Portfolio/actions/workflows/ci-mlops.yml/badge.svg)](https://github.com/DuqueOM/ML-MLOps-Portfolio/actions)
[![Coverage](https://img.shields.io/badge/coverage-{COVERAGE_PERCENT}%25-green)](reports/coverage.txt)
[![Python](https://img.shields.io/badge/python-3.11-blue)](pyproject.toml)

## TL;DR

{TLDR_SUMMARY}

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
{SAMPLE_REQUEST_JSON}
```

**Response:**
```json
{SAMPLE_RESPONSE_JSON}
```

## Artifacts & Data
- **Model:** `artifacts/model.joblib`
- **Metrics:** `artifacts/metrics.json`
- **Data:** `users_behavior.csv` (Managed via DVC)

## Maintainers
- **Lead MLOps:** [Your Name/Contact]
