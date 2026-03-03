# NLPInsight Analyzer

**Financial Sentiment Analysis — FinBERT (ProsusAI) + TF-IDF Fallback**

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.6+-ee4c2c.svg)](https://pytorch.org)
[![HuggingFace](https://img.shields.io/badge/🤗-FinBERT-yellow.svg)](https://huggingface.co/ProsusAI/finbert)
[![scikit-learn](https://img.shields.io/badge/sklearn-1.8-F7931E.svg)](https://scikit-learn.org)
[![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen.svg)]()

## Overview

NLPInsight Analyzer demonstrates **NLP in a production MLOps context** with a **dual-backend inference engine**:

- **Production Model**: ProsusAI/FinBERT transformer (97% accuracy, ~260 MB)
- **Fallback Model**: TF-IDF + LogisticRegression (88% accuracy, 309 KB)
- **Auto-Detection**: `SentimentPredictor` loads transformer or joblib based on model path
- **Production API**: FastAPI with Prometheus metrics, batch inference, health checks
- **Financial Domain**: Trained on Financial PhraseBank (4,845 sentences, 3-class sentiment)
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
| **FinBERT** (production) | ~260 MB | ~87ms P95 | 97% | Docker/K8s deployment |
| **sklearn** (fallback) | 309 KB | <10ms P95 | 88% | Low resource, no PyTorch |

The production deployment uses FinBERT for accuracy. The TF-IDF fallback provides a lightweight option when PyTorch is unavailable.

### Pipeline
1. **Data**: Financial PhraseBank CSV → label encoding → stratified split
2. **Training (FinBERT)**: ProsusAI/finbert → HuggingFace Trainer with early stopping
3. **Training (sklearn)**: TF-IDF vectorization → LogisticRegression with class weights
4. **Inference**: Unified `SentimentPredictor` with auto-backend detection
5. **API**: FastAPI + Pydantic validation + Prometheus metrics

## Model Performance (v3.0.0)

| Metric | FinBERT (production) | TF-IDF + LogReg (fallback) |
|--------|---------------------|----------------------------|
| **Accuracy** | **96.91%** | 88.08% |
| **F1 (weighted)** | **0.9695** | 0.880 |
| **F1 (macro)** | **0.9629** | 0.826 |
| **Labels** | negative, neutral, positive | negative, neutral, positive |
| **Model Size** | ~260 MB | 309 KB |
| **P95 Latency** | <220ms (K8s) | <10ms |

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

# Tests (98% coverage, 73 tests)
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
| Test Coverage | 98% (73 tests) |
| Docker Image | 2.05 GB (torch CPU-only) |
| Model Size | ~260 MB (FinBERT) / 309 KB (TF-IDF fallback) |
| P95 Latency | <220ms (K8s via port-forward) |
| Load Test | 0% error rate (Locust, 10 users, 30s) |

## Tech Stack

- **ML**: ProsusAI/FinBERT (PyTorch + HuggingFace Transformers) / scikit-learn (TF-IDF fallback)
- **API**: FastAPI + Pydantic + Uvicorn (2 workers)
- **Monitoring**: Prometheus custom metrics (`nlpinsight_*`)
- **Responsible AI**: Fairness audits (F1 parity), Pandera data validation
- **Container**: Multi-stage Docker (CPU-optimized PyTorch)
- **Config**: Pydantic-validated YAML
- **Data**: Financial PhraseBank (Malo et al., 2014)
