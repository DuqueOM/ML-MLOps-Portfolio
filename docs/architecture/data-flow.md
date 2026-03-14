# Data Flow

Data pipeline architecture from ingestion to serving across all projects.

## Pipeline Overview

`Data Sources → DVC Versioning → Cleaning → Feature Engineering → Train/Test Split → Model Training → MLflow → REST API → Monitoring`

## Project-Specific Flows

### BankChurn
`Churn.csv (10K rows) → Pandera Validation → SimpleImputer(median/constant) → OneHotEncoder(Geography,Gender) → StandardScaler → StackingClassifier(RF+GB+XGB+LGB→LR)`

### NLPInsight
`Financial tweets → Pandera Validation → TF-IDF Vectorizer → LogisticRegression → Sentiment (positive/negative/neutral)`
- GPU option: FinBERT (ProsusAI) for higher accuracy when GPU available

### ChicagoTaxi
`6.3M taxi trips (CSV) → PySpark ETL → Hourly aggregation (357K rows) → Lag features → RandomForest → Batch predictions (Parquet) → FastAPI serving`

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
| NLPInsight | Text non-empty, valid labels | `NLPInsightRawSchema` + `NLPInsightInferenceSchema` | Reject |
| ChicagoTaxi | Duration 60s–86400s, distance 0.1–500mi, area 1–77 | PySpark cleaning rules | Drop |

---

*Last Updated: March 2026 — v3.5.3*
