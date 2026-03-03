# 📝 Data Card — NLPInsight Analyzer Dataset

<div align="center">

**Financial PhraseBank — Sentiment Classification Dataset**

![Records](https://img.shields.io/badge/records-4,845-blue)
![Features](https://img.shields.io/badge/features-2-green)
![Target](https://img.shields.io/badge/target-3--class-orange)
![Last Updated](https://img.shields.io/badge/updated-March%202026-blue)

</div>

---

## 📋 Dataset Overview

| Attribute | Value |
|-----------|-------|
| **Dataset Name** | Financial PhraseBank |
| **Type** | Text Classification (Sentiment Analysis) |
| **Records** | 4,845 financial sentences |
| **Features** | 1 input feature (`text`) |
| **Target Variable** | `label` (negative, neutral, positive) |
| **Class Distribution** | Positive: 28.1%, Neutral: 59.4%, Negative: 12.5% |
| **Domain** | Financial news, earnings reports, market commentary |
| **Data Version** | v1.0.0 (tracked via DVC) |
| **Last Updated** | February 2026 |

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
positive:  1,363 (28.1%)  — Sentences with positive financial sentiment
neutral:   2,879 (59.4%)  — Factual/neutral financial statements
negative:    603 (12.5%)  — Sentences with negative financial sentiment
```

**Imbalance Ratio**: Neutral class dominates (59.4%); negative class underrepresented (12.5%)

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
- Annotated by **16 financial domain experts** (Malo et al., 2014)
- Consensus threshold: sentences included where ≥50% of annotators agreed
- Inter-annotator agreement: Fleiss' κ = 0.72 (substantial agreement)

### Known Quality Issues

| Issue | Count | Impact | Treatment |
|-------|-------|--------|-----------|
| **Duplicate texts** | ~97 (2%) | Slight bias toward common phrases | Retained (real market language patterns) |
| **Short sentences** | ~180 (<20 chars) | May lack sufficient context | Retained (valid headlines) |
| **Neutral dominance** | 59.4% | Model may overpredict neutral | `class_weight='balanced'` in training |

---

## ⚖️ Bias & Fairness

### Data Representation

| Dimension | Distribution | Potential Bias |
|-----------|-------------|----------------|
| **Language** | English only | ⚠️ **No multilingual support** |
| **Domain** | Financial news/reports | ⚠️ **Not generalizable** to social media, product reviews |
| **Time Period** | Pre-2014 financial text | ⚠️ **May not reflect** post-2020 market language (COVID, crypto, AI hype) |
| **Source** | Reuters, Bloomberg-style | ⚠️ **Institutional bias** toward formal financial language |
| **Class Balance** | Neutral 59%, Positive 28%, Negative 12% | ⚠️ **Negative class underrepresented** |

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
| **Origin** | Financial PhraseBank (Malo et al., 2014) — Academic dataset |
| **License** | CC BY-NC-SA 3.0 (non-commercial, share-alike) |
| **PII Status** | ✅ **No PII**: Public financial text, no personal data |
| **Citation** | Malo, P., et al. (2014). "Good debt or bad debt: Detecting semantic orientations in economic texts." *JASIST*, 65(4), 782-796. |

### Privacy Guarantees

- ✅ **Publicly available text**: All sentences from public financial reports/news
- ✅ **No personal information**: No names, accounts, or identifiable data
- ✅ **No proprietary data**: Academic research dataset
- ✅ **Anonymized sources**: Original article sources not linked

---

## 📂 Data Splits & Versioning

### Splitting Strategy

```python
Train:      4,118 records (85%)
Validation:   727 records (15%)
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
| **F1-Macro Degradation** | Continuous monitoring | Retrain if F1 < 0.80 |
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

1. **Small Dataset**: 4,845 samples — sufficient for fine-tuning but not for training from scratch
2. **Temporal Gap**: Pre-2014 text; modern financial language (crypto, SPACs, meme stocks) not represented
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
- **Original Paper**: Malo, P., Sinha, A., Korhonen, P., Wallenius, J., & Takala, P. (2014). Good debt or bad debt: Detecting semantic orientations in economic texts. *Journal of the Association for Information Science and Technology*, 65(4), 782-796.

---

<div align="center">

**Data Card Version**: 1.0 | **Last Updated**: March 2026
**Dataset Version**: 1.0.0 | **Records**: 4,845

⭐ **Production-Ready Financial Sentiment Data** ⭐

</div>
