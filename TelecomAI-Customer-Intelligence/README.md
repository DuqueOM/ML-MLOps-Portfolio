# TelecomAI Customer Intelligence

[![CI Status](https://img.shields.io/github/actions/workflow/status/DuqueOM/ML-MLOps-Portfolio/ci-mlops.yml?branch=main&label=CI)](https://github.com/DuqueOM/ML-MLOps-Portfolio/actions/workflows/ci-mlops.yml)
[![Coverage](https://img.shields.io/badge/Coverage-96%25-brightgreen)](../reports/)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](Dockerfile)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)

---

<!-- 
=============================================================================
🎬 DEMO GIF PLACEHOLDER
=============================================================================
TODO: Record a 6-8 second GIF showing:
1. API prediction call (curl or Swagger UI)
2. Response with plan recommendation

Create GIF:
1. Record screen: API request → response with prediction
2. Convert: ffmpeg -i video.mp4 -vf "fps=15,scale=800:-1" telecom-demo.gif
3. Place in: ../media/gifs/telecom-preview.gif
4. Uncomment the line below
=============================================================================
-->

<div align="center">

<!-- ![TelecomAI Demo](../media/gifs/telecom-preview.gif) -->
**[🎬 DEMO GIF — PENDING]** <!-- Remove this line after adding GIF -->

**[📺 Watch Full Demo Video](#)** <!-- TODO: Replace # with YouTube/Drive link -->

</div>

---

## TL;DR

A production-ready ML system for predicting telecom customer plan preferences using Scikit-Learn and FastAPI. Features automated pipelines, Dockerized inference, and comprehensive testing.

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
| **Data** | `users_behavior.csv` | User behavior dataset (managed via DVC) |

---

## 📋 CI Notes

| Component | Details |
|-----------|---------|
| **Workflow** | `.github/workflows/ci-mlops.yml` |
| **Coverage** | 96% (threshold: 70%) |
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
