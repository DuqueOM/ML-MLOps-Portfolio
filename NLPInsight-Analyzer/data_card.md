# 📝 Data Card — NLPInsight Analyzer Dataset

<div align="center">

**Twitter Financial News Sentiment — Classification Dataset**

![Records](https://img.shields.io/badge/records-11,931-blue)
![Features](https://img.shields.io/badge/features-2-green)
![Target](https://img.shields.io/badge/target-3--class-orange)
![Last Updated](https://img.shields.io/badge/updated-March%202026-blue)

</div>

---

## 📋 Dataset Overview

| Attribute | Value |
|-----------|-------|
| **Dataset Name** | Twitter Financial News Sentiment |
| **Type** | Text Classification (Sentiment Analysis) |
| **Records** | 11,931 financial tweets |
| **Features** | 1 input feature (`text`) |
| **Target Variable** | `label` (negative, neutral, positive) |
| **Class Distribution** | Positive: 26.9%, Neutral: 58.0%, Negative: 15.1% |
| **Domain** | Financial tweets (stock tickers, market commentary, earnings reactions) |
| **Source** | [HuggingFace: zeroshot/twitter-financial-news-sentiment](https://huggingface.co/datasets/zeroshot/twitter-financial-news-sentiment) |
| **Data Version** | v2.0.0 (tracked via DVC) |
| **Last Updated** | March 2026 |

> **Dataset upgrade (v3.5.0)**: Replaced Financial PhraseBank (4,845 expert-annotated sentences, 97% acc) with Twitter Financial News (11,931 real tweets, 80.6% acc). The harder, noisier dataset better demonstrates real-world NLP capability.

---

## 🎯 Intended Use

### Primary Purpose
Train and evaluate sentiment classification models for **financial text analysis**, enabling automated sentiment scoring of earnings reports, market commentary, and financial news.

### Appropriate Use Cases
- ✅ Financial sentiment scoring for market intelligence
- ✅ Earnings report tone analysis
- ✅ News sentiment aggregation for portfolio signals
- ✅ Educational NLP/transformer fine-tuning projects

### Inappropriate Use Cases
- ❌ **Automated trading decisions** (model output should inform, not execute)
- ❌ **Non-English text analysis** (English-only dataset)
- ❌ **General-purpose sentiment** (domain-specific to finance)
- ❌ **Fine-grained emotion detection** (3-class only: negative/neutral/positive)
- ❌ **Sarcasm or irony detection** (not annotated for pragmatic meaning)

---

## 📊 Schema & Features

### Feature Dictionary

| Feature | Type | Description | Example |
|---------|------|-------------|---------|
| `text` | string | Financial sentence (1-10,000 chars) | "Revenue growth exceeded expectations this quarter" |
| `label` | categorical | Sentiment label | `positive`, `neutral`, `negative` |

### Label Distribution

```
positive:  3,212 (26.9%)  — Tweets with positive financial sentiment
neutral:   6,920 (58.0%)  — Factual/neutral financial statements
negative:  1,799 (15.1%)  — Tweets with negative financial sentiment
```

**Imbalance Ratio**: Neutral class dominates (58.0%); negative class has highest business value (15.1%)

### Data Quality Validation (Pandera)

```python
# Automated schema validation (data/validate_data.py)
NLPInsightRawSchema:
  - text: non-empty, max 10,000 chars
  - label: one of [negative, neutral, positive]
  - Dataset: min 50 samples, min 2 distinct labels
```

---

## 🔍 Data Quality

### Completeness
```
Missing Values: 0 (100% complete)
Duplicates: ~2% duplicate texts (common financial phrases)
Invalid Entries: 0 (all labels valid)
```

### Statistical Summary

**Text Length**:
```
Mean:   124 characters
Median: 108 characters
Min:    10 characters
Max:    1,847 characters
Std:    82 characters
```

**Annotation Quality**:
- Community-annotated financial tweets from Twitter
- Labels derived from market context and financial language patterns
- Higher noise level than expert-annotated datasets (realistic for production NLP)

### Known Quality Issues

| Issue | Count | Impact | Treatment |
|-------|-------|--------|----------|
| **Noisy text** | ~15% | Stock tickers, URLs, abbreviations | Retained (real-world NLP challenge) |
| **Short tweets** | ~20% (<30 chars) | May lack sufficient context | Retained (valid market signals) |
| **Neutral dominance** | 58.0% | Model may overpredict neutral | `class_weight='balanced'` in training |

---

## ⚖️ Bias & Fairness

### Data Representation

| Dimension | Distribution | Potential Bias |
|-----------|-------------|----------------|
| **Language** | English only | ⚠️ **No multilingual support** |
| **Domain** | Financial news/reports | ⚠️ **Not generalizable** to social media, product reviews |
| **Time Period** | Recent financial tweets | ✅ Reflects modern market language (COVID, crypto, AI) |
| **Source** | Twitter / financial accounts | ⚠️ **Informal language bias** — may not generalize to formal reports |
| **Class Balance** | Neutral 58%, Positive 27%, Negative 15% | ⚠️ **Negative class underrepresented** |

### Bias Mitigation

1. **Class Weighting**: `class_weight='balanced'` in sklearn; weighted loss in transformer training
2. **Stratified Splitting**: 85/15 train/val maintains class proportions
3. **Per-Class Metrics**: F1-macro ensures minority class performance is tracked
4. **Domain Awareness**: Model card explicitly states financial-domain limitation

### Ethical Considerations

- **Market Manipulation**: Model should not be used to generate misleading sentiment signals
- **Automation Risk**: Outputs are advisory; human review required for trading decisions
- **Transparency**: Confidence scores provided with all predictions
- **No PII**: Dataset contains no personally identifiable information

---

## 🔐 Privacy & Compliance

### Data Source & Licensing

| Attribute | Details |
|-----------|---------|
| **Origin** | Twitter Financial News Sentiment — HuggingFace dataset |
| **License** | MIT License |
| **PII Status** | ✅ **No PII**: Public financial tweets, anonymized |
| **Source** | [HuggingFace](https://huggingface.co/datasets/zeroshot/twitter-financial-news-sentiment) |

### Privacy Guarantees

- ✅ **Publicly available text**: All sentences from public financial reports/news
- ✅ **No personal information**: No names, accounts, or identifiable data
- ✅ **No proprietary data**: Academic research dataset
- ✅ **Anonymized sources**: Original article sources not linked

---

## 📂 Data Splits & Versioning

### Splitting Strategy

```python
Train:      10,141 records (85%)
Validation:   1,790 records (15%)
Stratification: Maintains label proportions in both splits
Random Seed: 42 (reproducible)
```

**Validation Methods**:
- **Stratified Split**: 85/15 preserving class distribution
- **Cross-Validation**: Used during hyperparameter tuning (sklearn backend)
- **Early Stopping**: Validation F1 monitored during transformer fine-tuning

### Data Versioning

**DVC Tracking**:
```bash
dvc add data/raw/train.csv
dvc push  # To remote storage (GCS/S3)

# Current version
DVC SHA: c7d2e3f (committed February 2026)
File Size: 1.2 MB (CSV)
```

---

## 🔄 Refresh Strategy

### Update Triggers

| Trigger | Frequency | Action |
|---------|-----------|--------|
| **F1-Macro Degradation** | Continuous monitoring | Retrain if F1-macro < 0.60 |
| **New Financial Vocabulary** | Quarterly | Add domain-specific sentences (crypto, AI, ESG) |
| **Language Drift** | Semi-annual | Monitor for shifts in financial language patterns |
| **Regulatory Changes** | Event-driven | Update if new compliance terminology emerges |

### Data Quality Checks (Automated)

```python
# data/validate_data.py
def validate_nlpinsight_data(file_path):
    # Schema: text (non-empty, <10K chars), label (3-class)
    # Min 50 samples, min 2 distinct labels
    # Reports: label distribution, avg text length, duplicates
    return NLPInsightRawSchema.validate(df, lazy=True)
```

---

## 📈 Known Issues & Limitations

### Data Limitations

1. **Noisy text**: Real tweets with typos, abbreviations, stock tickers — harder but more realistic
2. **Social media bias**: Twitter language differs from formal financial reports
3. **Annotation Subjectivity**: Financial sentiment is inherently ambiguous (one annotator's "neutral" is another's "positive")
4. **Class Imbalance**: Negative class only 12.5% — model may underperform on bearish sentiment
5. **Sentence-Level Only**: No document-level or paragraph-level sentiment support
6. **No Contextual Features**: Missing metadata (source, date, company, sector)

### Recommended Enhancements (Production)

- 📊 **Augment with recent data**: Post-2020 financial text (COVID recovery, AI boom, rate hikes)
- 🌍 **Multilingual expansion**: Financial sentiment in Spanish, Mandarin, German
- 📅 **Temporal features**: Publication date, market conditions at time of writing
- 🏢 **Entity features**: Company name, sector, market cap for contextual sentiment
- 📈 **Fine-grained labels**: 5-class (very negative, negative, neutral, positive, very positive)

---

## 👥 Ownership & Contacts

| Role | Name | Responsibility |
|------|------|----------------|
| **Data Owner** | Duque Ortega Mutis (DuqueOM) | Dataset curation, versioning |
| **Data Governance** | Duque Ortega Mutis (DuqueOM) | Quality validation, compliance |

**Repository**: `NLPInsight-Analyzer/`
**Documentation**: See [README.md](README.md) and [model_card.md](model_card.md)

---

## 📚 References

- **Project README**: [NLPInsight-Analyzer/README.md](README.md)
- **Model Card**: [model_card.md](model_card.md)
- **Architecture**: [Portfolio Architecture](../docs/ARCHITECTURE_PORTFOLIO.md)
- **Dataset**: [Twitter Financial News Sentiment](https://huggingface.co/datasets/zeroshot/twitter-financial-news-sentiment)
- **Previous Dataset**: Financial PhraseBank (Malo et al., 2014) — used as benchmark comparison in model_card.md

---

<div align="center">

**Data Card Version**: 2.0 | **Last Updated**: March 2026
**Dataset Version**: 2.0.0 | **Records**: 11,931

⭐ **Production-Ready Financial Sentiment Data** ⭐

</div>
