# NLPInsight Analyzer

**Financial Sentiment Analysis — TF-IDF + LogReg (Production) / FinBERT (GPU)**

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.6+-ee4c2c.svg)](https://pytorch.org)
[![HuggingFace](https://img.shields.io/badge/🤗-FinBERT-yellow.svg)](https://huggingface.co/ProsusAI/finbert)
[![scikit-learn](https://img.shields.io/badge/sklearn-1.8-F7931E.svg)](https://scikit-learn.org)
[![Coverage](https://img.shields.io/badge/coverage-98.4%25-brightgreen.svg)]()

## Overview

NLPInsight Analyzer demonstrates **NLP in a production MLOps context** with a **dual-backend inference engine**:

- **Production Model**: TF-IDF + LogisticRegression (80.6% accuracy, ~5 MB, <5ms inference)
- **GPU Model**: ProsusAI/FinBERT transformer (~85-88% accuracy, ~440 MB)
- **Auto-Detection**: `SentimentPredictor` loads transformer or joblib based on model path
- **Production API**: FastAPI with Prometheus metrics, batch inference, health checks
- **Financial Domain**: Trained on Twitter Financial News Sentiment (11,931 real tweets, 3-class sentiment)
- **Responsible AI**: Fairness audits (per-class F1 parity), Pandera data validation

## Architecture

```
                    ┌─ [directory detected] → Tokenizer → FinBERT ─────────┐
Text Input → SentimentPredictor ─┤                                                    ├→ label + confidence + all_scores
                    └─ [joblib detected] → TF-IDF → LogisticRegression ────┘
```

### Why Dual Backend?

| Backend | Model Size | Inference | Accuracy | Use Case |
|---------|-----------|-----------|----------|----------|
| **sklearn** (production) | ~5 MB | <5ms P95 | 80.6% | Docker/K8s deployment (CPU) |
| **FinBERT** (GPU) | ~440 MB | ~87ms P95 | ~85-88% | GPU environments |

The production deployment uses TF-IDF + LogReg for CPU-optimized inference. FinBERT is available for GPU environments when higher accuracy is needed.

### Pipeline
1. **Data**: Twitter Financial News CSV → label encoding → stratified split
2. **Training (FinBERT)**: ProsusAI/finbert → HuggingFace Trainer with early stopping
3. **Training (sklearn)**: TF-IDF vectorization → LogisticRegression with class weights
4. **Inference**: Unified `SentimentPredictor` with auto-backend detection
5. **API**: FastAPI + Pydantic validation + Prometheus metrics

## Model Performance (v3.5.0)

| Metric | TF-IDF + LogReg (production) | FinBERT (GPU) |
|--------|------------------------------|---------------|
| **Accuracy** | **80.6%** | ~85-88%* |
| **F1 (weighted)** | **0.810** | ~0.85* |
| **F1 (macro)** | **0.748** | ~0.82* |
| **Labels** | negative, neutral, positive | negative, neutral, positive |
| **Model Size** | ~5 MB | ~440 MB |
| **P95 Latency** | <5ms | ~220ms (K8s) |

\* *FinBERT fine-tuning requires GPU. Estimated from published benchmarks.*

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Train FinBERT (production)
python main.py --mode train --config configs/config.yaml

# Predict (auto-detects backend from model path)
python main.py --mode predict --input "Revenue growth exceeded expectations"

# Run API
uvicorn app.fastapi_app:app --host 0.0.0.0 --port 8000

# Tests (98% coverage, 74 tests)
pytest tests/ -v --cov=src/nlpinsight
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/predict` | POST | Single text sentiment analysis |
| `/predict_batch` | POST | Batch analysis (up to 500 texts) |
| `/health` | GET | Kubernetes health/readiness check |
| `/metrics` | GET | Prometheus metrics (request count, latency, predictions by sentiment) |
| `/model_info` | GET | Model metadata, backend type, label mapping |

```bash
# Example prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "The company reported strong quarterly earnings growth"}'

# Response
# {"prediction":{"label":"positive","confidence":0.96,"all_scores":{"negative":0.01,"neutral":0.03,"positive":0.96}},"model":"finbert","inference_time_ms":87.5}
```

## Operational Metrics

| Metric | Value |
|--------|-------|
| Test Coverage | 98% (74 tests) |
| Docker Image | 267 MB (`nlpinsight:v3.5.0`, python:3.11-slim-bookworm, no torch) |
| Model Size | ~5 MB (TF-IDF production) / ~440 MB (FinBERT GPU) |
| P50 / P95 Latency | 5ms / 15ms (in-pod, GKE, TF-IDF) |
| Load Test | 0% error rate (Locust, 10 users, 2min, 1,030 requests via Ingress) |

## Data

| Attribute | Value |
|-----------|-------|
| **Records** | 11,931 financial tweets |
| **Features** | 1 input (`text`) |
| **Target** | `label` — negative, neutral, positive |
| **Distribution** | Positive 26.9%, Neutral 58.0%, Negative 15.1% |
| **Source** | [Twitter Financial News Sentiment](https://huggingface.co/datasets/zeroshot/twitter-financial-news-sentiment) |
| **Versioning** | DVC tracked |

See [data_card.md](data_card.md) for full dataset documentation.

## Project Structure

```
NLPInsight-Analyzer/
├── app/fastapi_app.py          # API endpoints (dual-backend)
├── src/nlpinsight/             # Core ML package
│   ├── predictor.py            # SentimentPredictor (auto-backend)
│   ├── training.py             # FinBERT + sklearn training
│   └── config.py               # Pydantic config validation
├── tests/                      # 74 tests (98% coverage)
├── configs/config.yaml         # Model + training config
├── data/raw/                   # Twitter Financial News (DVC tracked)
├── models/                     # FinBERT checkpoint or sklearn joblib
├── monitoring/                 # Drift detection
├── Dockerfile                  # Production image (CPU-optimized PyTorch)
├── Makefile                    # Dev commands
└── pyproject.toml              # Dependencies
```

## Tech Stack

- **ML**: ProsusAI/FinBERT (PyTorch + HuggingFace Transformers) / scikit-learn (TF-IDF fallback)
- **API**: FastAPI + Pydantic + Uvicorn (2 workers)
- **Monitoring**: Prometheus custom metrics (`nlpinsight_*`)
- **Responsible AI**: Fairness audits (F1 parity), Pandera data validation
- **Container**: Multi-stage Docker (CPU-optimized PyTorch)
- **Config**: Pydantic-validated YAML
- **Data**: Twitter Financial News Sentiment (11,931 tweets)

📄 [Model Card](model_card.md) · [Data Card](data_card.md) · [Full Docs](https://duqueom.github.io/ML-MLOps-Portfolio/projects/nlpinsight/)
