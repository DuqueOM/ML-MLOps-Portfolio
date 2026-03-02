# NLPInsight Analyzer

Financial sentiment analysis powered by NLP.

![NLPInsight API](../media/screenshots/apis/29-fastapi-swagger-nlpinsight.png)

## Performance (v2.0.0)

| Metric | TF-IDF (production) | DistilBERT |
|--------|---------------------|------------|
| **Accuracy** | 88.08% | ~85% |
| **F1 (macro)** | 0.826 | ~0.82 |
| **Labels** | 3 (negative, neutral, positive) | 3 |

## Architecture

Dual-backend inference engine:

- **Production (Docker)**: TF-IDF + LogisticRegression (`model.joblib`, 309KB)
- **Optional**: DistilBERT fine-tuned on Financial PhraseBank (~260MB)

`Text → SentimentPredictor → [TF-IDF → LogReg] or [Tokenizer → DistilBERT] → label + confidence + all_scores`

## Key Features

- **Dual Backend**: Auto-detects model type (joblib vs transformer directory)
- **Financial Domain**: Trained on Financial PhraseBank (4,845 sentences)
- **Lightweight Production**: 309KB sklearn model, <100ms inference

## Operational

| Metric | Value |
|--------|-------|
| Test Coverage | 95.5% (59 tests) |
| Docker Image | 2.05 GB (torch CPU-only) |
| Model Size | 309 KB (sklearn) |
| P95 Latency | <220ms |

## API

```bash
curl -X POST http://localhost:8003/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"The company reported strong quarterly earnings growth"}'
```

---

*Last Updated: March 2026*
