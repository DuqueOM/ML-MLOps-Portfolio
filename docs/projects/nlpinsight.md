# NLPInsight Analyzer

Classify financial text sentiment — and understand why domain-specific pre-training matters more than model size.

![NLPInsight API](../media/screenshots/apis/29-fastapi-swagger-nlpinsight.png)

## The Problem

Financial markets generate 10,000+ news articles/day. Manual sentiment review costs $50–100/hour per analyst. Automated classification must handle domain nuance: "revenue declined less than expected" is **positive** in financial context — a pattern that bag-of-words models consistently misclassify.

## Why Accuracy Works Here (and F1-Macro as Guard Rail)

The dataset has 3 classes: 58.0% neutral, 26.9% positive, 15.1% negative. Trained on **Twitter Financial News Sentiment** (11,931 real tweets) — noisy, informal text with stock tickers and abbreviations. F1-macro (0.748) guards the minority negative class — the highest-value signal for risk management.

| Metric | TF-IDF + LogReg (production) | FinBERT (GPU) | Why It Matters |
|--------|------------------------------|---------------|----------------|
| **Accuracy** | **80.6%** | ~85-88%* | Honest metric on hard, noisy tweets |
| **F1 (weighted)** | 0.810 | ~0.85* | Overall system performance weighted by class frequency |
| **F1 (macro)** | 0.748 | ~0.82* | Safety guard: ensures minority negative class isn't neglected |

\* *FinBERT fine-tuning requires GPU. Estimated from published benchmarks.*

80.6% on real financial tweets (vs 97% on the easier Financial PhraseBank) is an honest, defensible metric. The dataset upgrade from curated sentences to noisy tweets better demonstrates real-world NLP capability.

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

*Last Updated: March 2026 — v3.5.0*
