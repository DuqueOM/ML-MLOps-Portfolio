# 📝 Model Card — NLPInsight Sentiment Analyzer

<div align="center">

**ProsusAI/FinBERT for Financial Sentiment Analysis**

![Version](https://img.shields.io/badge/version-3.0.0-blue)
![Framework](https://img.shields.io/badge/PyTorch-2.6+-orange)
![Status](https://img.shields.io/badge/status-Production-brightgreen)
![Last Updated](https://img.shields.io/badge/updated-March%202026-blue)

</div>

---

## 📋 Quick Reference

| Attribute | Value |
|-----------|-------|
| **Model ID** | `nlpinsight-finbert-v3.0.0` |
| **Model Type** | Multi-class Classification (3-class Sentiment) |
| **Algorithm** | ProsusAI/FinBERT (production) / TF-IDF + LogReg (fallback) |
| **Framework** | PyTorch 2.6+ / HuggingFace Transformers 4.48+ / scikit-learn 1.8+ |
| **Primary Metric** | Accuracy: **96.91%**, F1-weighted: **0.9695** |
| **Business Impact** | Automated sentiment scoring for financial intelligence |
| **Production Status** | ✅ Active |
| **Last Updated** | March 2026 |
| **Owner** | Duque Ortega Mutis (DuqueOM) |

---

## 🎯 Model Purpose

### Primary Use Case

Classify the **sentiment of financial text** (earnings reports, market commentary, financial news) into three categories: positive, neutral, or negative — enabling automated financial intelligence pipelines.

### Intended Users & Applications

| Stakeholder | Application | Value Delivered |
|-------------|-------------|-----------------|
| **Financial Analysts** | Earnings report tone analysis | Automated screening of 100+ reports/day |
| **Portfolio Managers** | News sentiment aggregation | Real-time market sentiment signals |
| **Product Teams** | Customer feedback classification | Domain-adapted sentiment scoring |
| **Data Scientists** | NLP pipeline component | Pre-trained financial sentiment module |

### Business Context

- **Volume**: Financial markets generate 10,000+ news articles/day
- **Manual Cost**: $50-100/hour for analyst sentiment review
- **Model ROI**: 90% reduction in manual review time for sentiment screening
- **Accuracy**: 97% accuracy vs 88% for traditional TF-IDF approach

### Out of Scope

❌ **Not intended for**:
- Automated trading decisions (advisory only, human-in-the-loop required)
- Non-English text analysis (English-only model)
- Sarcasm or irony detection (not annotated for pragmatic meaning)
- Fine-grained emotion beyond 3-class sentiment
- Content moderation without human review

---

## 🏗 Model Architecture

### Dual-Backend Design

```
Production Backend (FinBERT):
  Input Text → FinBERT Tokenizer (max_length=256)
             → ProsusAI/FinBERT (110M params, 12 layers, 768 hidden)
             → Classification Head (768 → 3)
             → Softmax → {negative, neutral, positive}

Fallback Backend (sklearn):
  Input Text → TfidfVectorizer (sublinear_tf, max_features=10000)
             → LogisticRegression (class_weight='balanced', C=1.0)
             → {negative, neutral, positive}

Auto-Detection:
  SentimentPredictor.__init__():
    if model.joblib exists → sklearn backend (309 KB, <5ms inference)
    elif model dir with config.json → transformer backend (440 MB, ~87ms inference)
```

### Model Selection Rationale

| Model | Accuracy | F1 (macro) | Latency | Size | Selected? |
|-------|----------|------------|---------|------|-----------|
| **TF-IDF + LogReg** | 88.08% | 0.826 | <5ms | 309 KB | ✅ Fallback |
| **DistilBERT (fine-tuned)** | 93.2% | 0.918 | ~50ms | 260 MB | ❌ |
| **ProsusAI/FinBERT** | **96.91%** | **0.9595** | ~87ms | 440 MB | ✅ **Production** |

**Why FinBERT?**: Domain-specific pre-training on financial corpora (TRC2 + Financial PhraseBank) captures semantic meaning of financial terminology that TF-IDF misses. "Revenue declined less than expected" is correctly classified as positive by FinBERT but negative by TF-IDF.

### Training Procedure

**Production Model (FinBERT)**:
- **Base Model**: ProsusAI/finbert (pre-trained on 1.8M financial documents)
- **Fine-tuning**: HuggingFace Trainer API with early stopping
- **Optimizer**: AdamW (lr=2e-5, weight_decay=0.01)
- **Schedule**: Linear warmup (10% of steps) + linear decay
- **Epochs**: 3 (with early stopping, patience=2)
- **Batch Size**: 16
- **Hardware**: CPU (GPU optional with FP16 support)
- **Reproducibility**: Seed=42, deterministic training

**Fallback Model (TF-IDF + LogReg)**:
- **Vectorizer**: TfidfVectorizer (sublinear_tf=True, max_features=10000)
- **Classifier**: LogisticRegression (class_weight='balanced', C=1.0, max_iter=1000)
- **Training**: Single-pass fit on CPU
- **Reproducibility**: Seed=42

---

## 💾 Training Data

### Dataset Overview

| Attribute | Value |
|-----------|-------|
| **Source** | Financial PhraseBank (Malo et al., 2014) |
| **Records** | 4,845 financial sentences |
| **Labels** | 3 classes (negative, neutral, positive) |
| **Annotation** | 16 financial domain experts, Fleiss' κ = 0.72 |
| **Train/Val Split** | 85% / 15% (stratified by label) |
| **Data Version** | Tracked via DVC (SHA: `c7d2e3f`) |

### Label Distribution

| Label | Count | Percentage | Example |
|-------|-------|------------|---------|
| **Positive** | 1,363 | 28.1% | "Revenue growth exceeded expectations this quarter" |
| **Neutral** | 2,879 | 59.4% | "The company reported quarterly earnings of $0.52 per share" |
| **Negative** | 603 | 12.5% | "Operating margins declined significantly due to rising costs" |

### Data Quality

- ✅ No missing values (100% complete)
- ✅ Expert-annotated with consensus threshold (≥50% agreement)
- ⚠️ Class imbalance: Handled via `class_weight='balanced'` and stratified splitting
- ⚠️ ~2% duplicate texts (common financial phrases, retained as valid patterns)

---

## 📊 Performance Metrics

### Primary Metrics

| Metric | FinBERT v3.0 (production) | TF-IDF + LogReg (fallback) | Target | Status |
|--------|:---:|:---:|:---:|:---:|
| **Accuracy** | **96.91%** | 88.08% | ≥ 85% | ✅ PASS |
| **F1 (weighted)** | **0.9695** | 0.880 | ≥ 0.85 | ✅ PASS |
| **F1 (macro)** | **0.9595** | 0.826 | ≥ 0.80 | ✅ PASS |
| **Precision (macro)** | 0.96 | 0.83 | ≥ 0.80 | ✅ PASS |
| **Recall (macro)** | 0.96 | 0.82 | ≥ 0.80 | ✅ PASS |

### Per-Class Performance (FinBERT)

| Class | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| **Negative** | 0.95 | 0.94 | 0.945 | 90 |
| **Neutral** | 0.97 | 0.98 | 0.975 | 432 |
| **Positive** | 0.96 | 0.95 | 0.955 | 205 |

### Inference Performance

| Backend | Avg Latency | P95 Latency | Throughput | Memory |
|---------|-------------|-------------|------------|--------|
| **FinBERT** | 87ms | 220ms | ~11 req/s | 512Mi |
| **TF-IDF** | <5ms | <10ms | ~200 req/s | 64Mi |
| **Batch (5 texts)** | ~200ms | ~400ms | ~25 texts/s | 512Mi |

---

## ⚠️ Limitations & Bias

### Known Limitations

| Limitation | Impact | Mitigation Strategy |
|------------|--------|---------------------|
| **English-only** | Cannot analyze non-English financial text | Document scope; plan multilingual v4.0 |
| **3-class only** | No fine-grained sentiment (very positive/negative) | Confidence scores provide granularity |
| **256 token limit** | Longer documents truncated silently | Recommend sentence-level analysis for long docs |
| **Financial domain** | Underperforms on general-purpose sentiment | Use domain-specific model only for finance |
| **Pre-2014 training data** | May miss modern financial language (crypto, ESG) | Quarterly retraining recommended |

### Bias & Fairness Analysis

| Dimension | Finding | Action |
|-----------|---------|--------|
| **Neutral dominance** | 59.4% of training data is neutral → slight neutral bias | Class weighting mitigates; monitor per-class F1 |
| **Institutional language** | Trained on formal Reuters/Bloomberg-style text | May underperform on informal financial social media |
| **Market bias** | Financial text reflects Western market perspectives | Document limitation; not suitable for emerging markets analysis |

### Ethical Considerations

- **Transparency**: Confidence scores provided for all predictions via `all_scores` field
- **Human-in-the-Loop**: Model outputs are advisory; trading decisions require human review
- **No Market Manipulation**: Should not be used to generate misleading sentiment signals
- **Privacy**: No PII stored in model weights; input texts not logged by default

---

## 🚀 Deployment & Reproducibility

### Training Reproduction

```bash
# 1. Clone and setup
git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git
cd ML-MLOps-Portfolio/NLPInsight-Analyzer

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Pull data (DVC)
dvc pull  # Or manually: place train.csv in data/raw/

# 3. Train model
python main.py --mode train --config configs/config.yaml

# 4. Verify artifacts
ls models/
# Expected: model.tar.gz (FinBERT) or model.joblib (sklearn)
```

**Reproducibility Guarantees**:
- ✅ Random seed: `seed=42` across all components
- ✅ Data versioning: DVC tracks dataset (SHA: `c7d2e3f`)
- ✅ Dependency pinning: `requirements.txt` with `~=` compatible-release
- ✅ Config-driven: All hyperparameters in `configs/config.yaml`

### API Inference

```bash
# Start FastAPI
uvicorn app.fastapi_app:app --host 0.0.0.0 --port 8000

# Test prediction
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"text": "Revenue growth exceeded expectations this quarter."}'
```

**Expected Response**:
```json
{
  "prediction": {
    "label": "positive",
    "confidence": 0.96,
    "all_scores": {"negative": 0.01, "neutral": 0.03, "positive": 0.96}
  },
  "model": "finbert",
  "inference_time_ms": 87.5
}
```

### Docker Deployment

```bash
docker pull ghcr.io/duqueom/nlpinsight-api:v3.0.0
docker run -d -p 8000:8000 ghcr.io/duqueom/nlpinsight-api:v3.0.0

curl http://localhost:8000/health
# {"status": "healthy", "model_loaded": true, "version": "1.0.0"}
```

### Kubernetes Deployment

**Production Setup**: See `k8s/nlpinsight-deployment.yaml` for full manifest

- **Replicas**: 1 (auto-scaled 1-3 based on CPU)
- **Resources**: 300m CPU / 512Mi memory (requests), 1000m CPU / 1Gi memory (limits)
- **Health Probes**: Liveness/Readiness at `/health`
- **Init Container**: Downloads FinBERT model from GCS at pod startup
- **Monitoring**: Prometheus annotations enabled

---

## 📈 Monitoring & Maintenance

### Production Monitoring

**Prometheus Metrics** (`/metrics` endpoint):

```promql
# Prediction latency (target p95: <250ms)
histogram_quantile(0.95, rate(nlpinsight_request_duration_seconds_bucket[5m]))

# Sentiment distribution (expected ~60% neutral)
rate(nlpinsight_predictions_total{sentiment="neutral"}[1h]) / rate(nlpinsight_predictions_total[1h])

# Error rate
rate(nlpinsight_requests_total{status="500"}[5m])
```

**Grafana Dashboard Panels**:
1. Request Rate (QPS)
2. Prediction Latency (p50, p95, p99)
3. Sentiment Distribution (stacked bar)
4. Error Rate (target: <0.1%)

### Retraining Triggers

| Trigger | Threshold | Frequency | Action |
|---------|-----------|-----------|--------|
| **F1-Macro Degradation** | < 0.80 | Continuous | 🚨 Immediate retrain |
| **Sentiment Distribution Shift** | ±15% from baseline | Weekly | ⚠️ Investigate |
| **New Vocabulary** | Quarterly releases | Quarterly | ✅ Scheduled retrain |
| **Time-based** | — | Monthly | ✅ Routine refresh |

---

## 📜 Model Governance

### Version History

| Version | Date | Changes | Accuracy | Status |
|---------|------|---------|----------|--------|
| **3.0.0** | Mar 2026 | ProsusAI/FinBERT (transfer learning), dual-backend | 96.91% | ✅ Active |
| 2.0.0 | Feb 2026 | TF-IDF + LogisticRegression, balanced classes | 88.08% | Fallback |
| 1.0.0 | Sep 2025 | Initial TF-IDF baseline | 85.2% | Deprecated |

### Promotion Criteria (Staging → Production)

1. ✅ Accuracy ≥ 85% on validation set
2. ✅ F1-macro ≥ 0.80
3. ✅ Per-class F1 ≥ 0.70 (no class left behind)
4. ✅ P95 latency < 500ms
5. ✅ Security scan clean (Bandit, pip-audit)
6. ✅ Code review approved

### Compliance

- **Model Registry**: MLflow (http://localhost:5000)
- **Lineage**: Git SHA + DVC data version in artifacts
- **Audit**: Predictions logged with request ID

---

## 👥 Ownership & Contacts

| Role | Name | Responsibility | Contact |
|------|------|----------------|---------|
| **Model Owner** | Duque Ortega Mutis | Development, performance, improvements | [GitHub](https://github.com/DuqueOM) |
| **MLOps Engineer** | Duque Ortega Mutis | Deployment, monitoring, infrastructure | [LinkedIn](https://linkedin.com/in/duqueom) |

---

## 📚 References & Resources

- **[Project README](README.md)** — Setup, quick start, development guide
- **[Data Card](data_card.md)** — Dataset documentation
- **[Architecture Docs](../docs/ARCHITECTURE_PORTFOLIO.md)** — System design, data flow
- **[API Documentation](http://localhost:8000/docs)** — Interactive Swagger UI (when running)

### Academic References

- Malo, P., et al. (2014). Good debt or bad debt: Detecting semantic orientations in economic texts. *JASIST*, 65(4), 782-796.
- Araci, D. (2019). FinBERT: Financial Sentiment Analysis with Pre-Trained Language Models. *arXiv:1908.10063*.
- Devlin, J., et al. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. *NAACL-HLT*.

---

<div align="center">

**Model Card Version**: 3.0 | **Last Updated**: March 2026
**Model Version**: 3.0.0 | **Framework**: PyTorch 2.6+, HuggingFace Transformers 4.48+

⭐ **Production-Ready Financial Sentiment Analysis** ⭐

</div>
