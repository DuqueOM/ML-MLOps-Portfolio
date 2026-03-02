# Data Flow

Data pipeline architecture from ingestion to serving across all projects.

## Pipeline Overview

`Data Sources → DVC Versioning → Cleaning → Feature Engineering → Train/Test Split → Model Training → MLflow → REST API → Monitoring`

## Project-Specific Flows

### BankChurn
`Churn.csv (10K rows) → SimpleImputer(median/constant) → OneHotEncoder(Geography,Gender) → StandardScaler → VotingClassifier(LR+RF)`

### CarVision
`vehicles.csv (~500K) → Data Cleaning (price 1K-500K, year≥1990) → FeatureEngineer (vehicle_age, brand tiers, depreciation) → Drop leaky features → XGBRegressor`

> **Data Leakage Prevention**: `price_per_mile` and `price_category` dropped — they derive from the target variable `price`.

### NLPInsight
`Reviews → TF-IDF Vectorization → LogisticRegression → Sentiment (positive/negative/neutral)`

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

## Data Quality

| Project | Validation | Action |
|---------|-----------|--------|
| BankChurn | CreditScore ∈ [300, 850] | Reject |
| CarVision | Price ∈ [1K, 500K] | Filter |
| NLPInsight | Text non-empty | Reject |

---

*Last Updated: March 2026*
