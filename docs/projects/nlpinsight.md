# NLPInsight Analyzer

Financial sentiment analysis powered by NLP.

![NLPInsight API](../media/screenshots/apis/29-fastapi-swagger-nlpinsight.png)

## Performance (v3.0.0)

| Metric | FinBERT (production) | TF-IDF (fallback) |
|--------|---------------------|-------------------|
| **Accuracy** | 97% | 88% |
| **F1 (weighted)** | 0.97 | 0.83 |
| **Labels** | 3 (negative, neutral, positive) | 3 |

## Architecture

Dual-backend inference engine:

- **Production (Docker)**: FinBERT (ProsusAI/finbert) transformer
- **Fallback**: TF-IDF + LogisticRegression (`model.joblib`, 309KB)

`Text → SentimentPredictor → [FinBERT Tokenizer → FinBERT] or [TF-IDF → LogReg] → label + confidence + all_scores`

## Key Features

- **Dual Backend**: Auto-detects model type (joblib vs transformer directory)
- **Financial Domain**: Trained on Financial PhraseBank (4,845 sentences)
- **Fairness Audits**: Per-class F1 parity, group fairness indicators
- **Data Validation**: Pandera schemas (raw + inference)
- **Lightweight Fallback**: 309KB sklearn model, <100ms inference

## Operational

| Metric | Value |
|--------|-------|
| Test Coverage | 98% (73 tests) |
| Docker Image | 2.05 GB (torch CPU-only) |
| Model Size | ~260 MB (FinBERT) / 309 KB (TF-IDF fallback) |
| P95 Latency | <220ms |

## API

```bash
curl -X POST http://localhost:8003/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"The company reported strong quarterly earnings growth"}'
```

---

*Last Updated: March 2026 — v3.2.0*
