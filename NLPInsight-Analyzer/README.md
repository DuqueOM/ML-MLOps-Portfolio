# NLPInsight Analyzer

**Sentiment Analysis with Fine-Tuned DistilBERT Transformers**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org)
[![HuggingFace](https://img.shields.io/badge/🤗-Transformers-yellow.svg)](https://huggingface.co)

## Overview

NLPInsight Analyzer demonstrates **NLP with deep learning** in a production MLOps context:

- **Transfer Learning**: Fine-tuned DistilBERT for binary sentiment classification
- **PyTorch + HuggingFace**: Modern NLP stack with Trainer API
- **GPU-Aware**: Automatic CUDA detection with CPU fallback
- **Production API**: FastAPI with Prometheus metrics, batch inference, health checks
- **Containerized**: Multi-stage Docker with CPU-optimized PyTorch

## Architecture

```
Text Input → Tokenizer (DistilBERT) → Fine-tuned Model → Softmax → Sentiment Label
```

### Pipeline
1. **Data**: CSV loading, label encoding, stratified splitting
2. **Tokenization**: HuggingFace AutoTokenizer with padding/truncation
3. **Training**: HuggingFace Trainer with early stopping, warmup scheduling
4. **Inference**: Batch-optimized prediction with confidence scores
5. **API**: FastAPI with Pydantic validation, Prometheus metrics

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Train (requires dataset in data/raw/)
python main.py --mode train --config configs/config.yaml

# Predict
python main.py --mode predict --input "This product is amazing!"

# Run API
uvicorn app.fastapi_app:app --host 0.0.0.0 --port 8000

# Tests
pytest tests/ -v
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/predict` | POST | Single text sentiment analysis |
| `/predict_batch` | POST | Batch analysis (up to 500 texts) |
| `/health` | GET | Kubernetes health check |
| `/metrics` | GET | Prometheus metrics |
| `/model_info` | GET | Model metadata and labels |

## Model Card

- **Base Model**: `distilbert-base-uncased` (66M parameters)
- **Task**: Binary sentiment classification (positive/negative)
- **Training**: 3 epochs, lr=2e-5, AdamW with warmup
- **Inference**: ~15ms per text (CPU), ~3ms (GPU)

## Tech Stack

- **Framework**: PyTorch 2.0+ / HuggingFace Transformers
- **API**: FastAPI + Pydantic + Uvicorn
- **Monitoring**: Prometheus metrics
- **Container**: Docker multi-stage (CPU-optimized)
- **Config**: Pydantic-validated YAML
