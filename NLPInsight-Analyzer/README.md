# NLPInsight Analyzer

**Financial Sentiment Analysis — Dual-Backend NLP (TF-IDF + DistilBERT)**

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://python.org)
[![scikit-learn](https://img.shields.io/badge/sklearn-1.8-F7931E.svg)](https://scikit-learn.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org)
[![HuggingFace](https://img.shields.io/badge/🤗-Transformers-yellow.svg)](https://huggingface.co)
[![Coverage](https://img.shields.io/badge/coverage-95.5%25-brightgreen.svg)]()

## Overview

NLPInsight Analyzer demonstrates **NLP in a production MLOps context** with a unique **dual-backend inference engine**:

- **Production Model**: TF-IDF + LogisticRegression (309KB, <100ms, 88% accuracy)
- **Advanced Option**: Fine-tuned DistilBERT (66M params, GPU-aware)
- **Auto-Detection**: `SentimentPredictor` loads joblib or transformer based on model path
- **Production API**: FastAPI with Prometheus metrics, batch inference, health checks
- **Financial Domain**: Trained on Financial PhraseBank (4,845 sentences, 3-class sentiment)

## Architecture

```
                    ┌─ [joblib detected] → TF-IDF → LogisticRegression ─┐
Text Input → SentimentPredictor ─┤                                              ├→ label + confidence + all_scores
                    └─ [directory detected] → Tokenizer → DistilBERT ───┘
```

### Why Dual Backend?

| Backend | Model Size | Inference | Use Case |
|---------|-----------|-----------|----------|
| **sklearn** (production) | 309 KB | ~87ms P95 | Docker/K8s deployment, low resource |
| **transformer** (advanced) | ~260 MB | ~15ms GPU | GPU environments, research |

The production deployment uses the sklearn backend for efficiency — a 309KB model vs ~260MB, with no GPU requirement.

### Pipeline
1. **Data**: Financial PhraseBank CSV → label encoding → stratified split
2. **Training (sklearn)**: TF-IDF vectorization → LogisticRegression with class weights
3. **Training (transformer)**: HuggingFace Trainer with early stopping, warmup scheduling
4. **Inference**: Unified `SentimentPredictor` with auto-backend detection
5. **API**: FastAPI + Pydantic validation + Prometheus metrics

## Model Performance (v2.0.0)

| Metric | TF-IDF + LogReg (production) | DistilBERT |
|--------|------------------------------|------------|
| **Accuracy** | 88.08% | ~85% |
| **F1 (macro)** | 0.826 | ~0.82 |
| **Labels** | negative, neutral, positive | negative, neutral, positive |
| **Model Size** | 309 KB | ~260 MB |
| **P95 Latency** | <220ms (K8s) | ~15ms (GPU) |

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Train sklearn model (production)
python -c "
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib, os
# See scripts/train_production_models.py for full training
"

# Train DistilBERT (advanced)
python main.py --mode train --config configs/config.yaml

# Predict (auto-detects backend from model path)
python main.py --mode predict --input "Revenue growth exceeded expectations"

# Run API
uvicorn app.fastapi_app:app --host 0.0.0.0 --port 8000

# Tests (95.5% coverage)
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
# {"prediction":{"label":"positive","confidence":0.89,"all_scores":{"negative":0.03,"neutral":0.08,"positive":0.89}},"model":"tfidf-logreg","inference_time_ms":2.1}
```

## Operational Metrics

| Metric | Value |
|--------|-------|
| Test Coverage | 95.5% (336/352 lines, 59 tests) |
| Docker Image | 2.05 GB (torch CPU-only) |
| Model Size | 309 KB (sklearn) / ~260 MB (transformer) |
| P95 Latency | <220ms (K8s via port-forward) |
| Load Test | 0% error rate (Locust, 10 users, 30s) |

## Tech Stack

- **ML**: scikit-learn (TF-IDF + LogisticRegression) / PyTorch + HuggingFace Transformers
- **API**: FastAPI + Pydantic + Uvicorn (2 workers)
- **Monitoring**: Prometheus custom metrics (`nlpinsight_*`)
- **Container**: Multi-stage Docker (CPU-optimized PyTorch)
- **Config**: Pydantic-validated YAML
- **Data**: Financial PhraseBank (Malo et al., 2014)
