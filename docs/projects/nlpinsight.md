# NLPInsight Analyzer

Classify financial text sentiment — and understand why domain-specific pre-training matters more than model size.

![NLPInsight API](../media/screenshots/apis/29-fastapi-swagger-nlpinsight.png)

## The Problem

Financial markets generate 10,000+ news articles/day. Manual sentiment review costs $50–100/hour per analyst. Automated classification must handle domain nuance: "revenue declined less than expected" is **positive** in financial context — a pattern that bag-of-words models consistently misclassify.

## Why Accuracy Works Here (and F1-Macro as Guard Rail)

The dataset has 3 classes: 59.4% neutral, 28.1% positive, 12.5% negative. No class falls below 12%, making accuracy meaningful (unlike BankChurn's 20/80 split). F1-macro (0.96) guards the minority negative class — the highest-value signal for risk management.

| Metric | FinBERT | TF-IDF Fallback | Why It Matters |
|--------|---------|-----------------|----------------|
| **Accuracy** | 96.91% | 88.08% | +8.8 points from domain-specific transfer learning |
| **F1 (weighted)** | 0.9695 | 0.880 | Overall system performance weighted by class frequency |
| **F1 (macro)** | 0.9595 | 0.826 | Safety guard: ensures minority negative class isn't neglected |
| **Negative Recall** | 0.94 | — | 94% of actual negative texts are caught |

The 8.8-point accuracy gap between TF-IDF and FinBERT comes from **domain-specific pre-training** on Reuters/Bloomberg financial text — ~3.7% of that gain from FinBERT's pre-training alone, before any fine-tuning.

## Architecture

```
Production:  Text → FinBERT Tokenizer (max 256 tokens) → ProsusAI/FinBERT (110M params)
                   → Classification Head → Softmax → {negative, neutral, positive} + confidence scores

Fallback:    Text → TfidfVectorizer (max 10K features) → LogisticRegression (class_weight='balanced')
                   → {negative, neutral, positive}

Auto-detect: SentimentPredictor checks for model.joblib (sklearn) or config.json (transformer)
```

**Why dual backend**: FinBERT adds 87ms per request; TF-IDF runs in <5ms. For latency-critical pipelines, deploy the fallback. For accuracy-critical analyst workflows, use FinBERT. The API auto-detects which backend to use based on model availability.

## Operational

| Metric | Value | Context |
|--------|-------|---------|
| Test Coverage | 98% (74 tests) | CI threshold: 85% |
| Docker Image | 1.4 GB | PyTorch CPU-only; optimized from 2.05 GB (-32%) |
| Model Size | ~260 MB (FinBERT) / 309 KB (fallback) | FinBERT downloaded via Init Container from GCS |
| P50 / P95 Latency | 180ms / 450ms | Locust, 10 users, GKE via port-forward |

## Responsible AI

- **Fairness**: Per-class F1 parity monitored; no class F1 below 0.90
- **Drift**: Sentiment distribution monitored via Prometheus (`nlpinsight_predictions_total{sentiment}`); shift alerts calibrated as relative change from 7-day baseline (not absolute — a market crisis legitimately shifts the distribution)
- **Validation**: Pandera schemas for input text and label format

## Try It

```bash
curl -X POST http://localhost:8003/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"The company reported strong quarterly earnings growth"}'
```

📄 [Full Model Card](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/NLPInsight-Analyzer/model_card.md) — includes metric rationale, performance benchmarks, and production decision narrative.

---

*Last Updated: March 2026 — v3.4.0*
