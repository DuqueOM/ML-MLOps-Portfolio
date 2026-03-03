# Data Flow

Data pipeline architecture from ingestion to serving across all projects.

## Pipeline Overview

`Data Sources → DVC Versioning → Cleaning → Feature Engineering → Train/Test Split → Model Training → MLflow → REST API → Monitoring`

## Project-Specific Flows

### BankChurn
`Churn.csv (10K rows) → Pandera Validation → SimpleImputer(median/constant) → OneHotEncoder(Geography,Gender) → StandardScaler → StackingClassifier(RF+GB+XGB+LGB→LR)`

### CarVision
`vehicles.csv (~500K) → Pandera Validation → Data Cleaning (price 1K-500K, year≥1990) → FeatureEngineer (24 features) → Drop leaky features → LightGBM`

> **Data Leakage Prevention**: `price_per_mile` and `price_category` dropped — they derive from the target variable `price`.

### NLPInsight
`Financial texts → Pandera Validation → FinBERT Tokenizer → FinBERT (ProsusAI) → Sentiment (positive/negative/neutral)`
- Fallback: TF-IDF + LogisticRegression

## Data Versioning (DVC)

```bash
dvc add data/raw/train.csv    # Track
dvc push                       # Push to GCS/S3
dvc pull                       # Pull on another machine
```

## Storage

| Type | Path | Format |
|------|------|--------|
| Raw Data | `data/raw/` | CSV |
| Models | `models/model.joblib` | Joblib |
| MLflow | `mlruns/` | Various |
| GCS Models | `gs://*-ml-models-production/{project}/model.joblib` | Joblib |

## Data Quality (Pandera Schemas)

| Project | Validation | Schema | Action |
|---------|-----------|--------|--------|
| BankChurn | CreditScore ∈ [300, 850], Age > 0 | `BankChurnRawSchema` + `BankChurnInferenceSchema` | Reject |
| CarVision | Price ∈ [1K, 500K], Year ≥ 1990 | `CarVisionRawSchema` + `CarVisionInferenceSchema` | Filter |
| NLPInsight | Text non-empty, valid labels | `NLPInsightRawSchema` + `NLPInsightInferenceSchema` | Reject |

---

*Last Updated: March 2026 — v3.3.0*
