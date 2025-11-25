# Data Flow

Data pipeline architecture from ingestion to serving across all projects.

---

## High-Level Data Flow

```mermaid
graph TB
    subgraph "Data Sources"
        S1["Bank Customer Data"]
        S2["Vehicle Listings"]
        S3["Telecom Usage Logs"]
    end
    
    subgraph "Ingestion Layer"
        DVC["DVC<br/>(Version Control)"]
        RAW["Raw Data<br/>(data/raw/)"]
    end
    
    subgraph "Processing Layer"
        CLEAN["Data Cleaning"]
        FE["Feature Engineering"]
        SPLIT["Train/Test Split"]
    end
    
    subgraph "Training Pipeline"
        TRAIN["Model Training"]
        EVAL["Evaluation"]
        REG["Model Registry<br/>(MLflow)"]
    end
    
    subgraph "Serving Layer"
        API["REST APIs"]
        BATCH["Batch Predictions"]
    end
    
    subgraph "Monitoring"
        DRIFT["Drift Detection"]
        METRICS["Performance Metrics"]
    end
    
    S1 --> DVC
    S2 --> DVC
    S3 --> DVC
    DVC --> RAW
    RAW --> CLEAN
    CLEAN --> FE
    FE --> SPLIT
    SPLIT --> TRAIN
    TRAIN --> EVAL
    EVAL --> REG
    REG --> API
    REG --> BATCH
    API --> DRIFT
    BATCH --> METRICS
```

---

## Project-Specific Data Flows

### BankChurn Predictor

```mermaid
graph LR
    subgraph "Input"
        CSV["train.csv<br/>(10,000 rows)"]
    end
    
    subgraph "Preprocessing"
        IMP["SimpleImputer<br/>(median/constant)"]
        ENC["OneHotEncoder<br/>(Geography, Gender)"]
        SCL["StandardScaler<br/>(Numerical)"]
    end
    
    subgraph "Features"
        NUM["Numerical<br/>CreditScore, Age, Balance..."]
        CAT["Categorical<br/>Geography, Gender"]
    end
    
    subgraph "Model"
        PIPE["sklearn Pipeline"]
        VC["VotingClassifier"]
    end
    
    CSV --> IMP
    IMP --> NUM
    IMP --> CAT
    NUM --> SCL
    CAT --> ENC
    SCL --> PIPE
    ENC --> PIPE
    PIPE --> VC
```

**Data Schema:**

| Column | Type | Description |
|--------|------|-------------|
| CreditScore | int | 300-850 |
| Geography | str | France, Germany, Spain |
| Gender | str | Male, Female |
| Age | int | Customer age |
| Tenure | int | Years with bank |
| Balance | float | Account balance |
| NumOfProducts | int | Number of products |
| HasCrCard | int | 0 or 1 |
| IsActiveMember | int | 0 or 1 |
| EstimatedSalary | float | Annual salary |
| Exited | int | Target (0/1) |

### CarVision Market Intelligence

```mermaid
graph LR
    subgraph "Input"
        CSV["vehicles.csv<br/>(~500K rows)"]
    end
    
    subgraph "Filtering"
        FILT["Data Cleaning<br/>- price: 1K-500K<br/>- year: 1990+<br/>- odometer: <500K"]
    end
    
    subgraph "Feature Engineering"
        FE["FeatureEngineer<br/>(Centralized)"]
        DROP["Drop Leaky Features<br/>- price_per_mile<br/>- price_category"]
    end
    
    subgraph "Preprocessing"
        NUM["Numerical Pipeline"]
        CAT["Categorical Pipeline"]
    end
    
    subgraph "Model"
        RF["RandomForest<br/>Regressor"]
    end
    
    CSV --> FILT
    FILT --> FE
    FE --> DROP
    DROP --> NUM
    DROP --> CAT
    NUM --> RF
    CAT --> RF
```

**Key Design Decisions:**

!!! warning "Data Leakage Prevention"
    `price_per_mile` and `price_category` are dropped from features because they 
    are derived from the target variable (`price`) and would cause data leakage.

### TelecomAI Customer Intelligence

```mermaid
graph LR
    subgraph "Input"
        CSV["telecom.csv"]
    end
    
    subgraph "Features"
        USAGE["Usage Metrics<br/>calls, minutes, messages, mb_used"]
        PLAN["Plan Type<br/>is_ultimate"]
    end
    
    subgraph "Model"
        VC["VotingClassifier<br/>(LR + RF)"]
    end
    
    subgraph "Output"
        PRED["Prediction<br/>upgrade: 0/1"]
    end
    
    CSV --> USAGE
    CSV --> PLAN
    USAGE --> VC
    PLAN --> VC
    VC --> PRED
```

---

## Data Versioning with DVC

### Architecture

```mermaid
graph TB
    subgraph "Local"
        WORK["Working Directory"]
        CACHE[".dvc/cache"]
        DVC_FILES[".dvc files"]
    end
    
    subgraph "Remote Storage"
        S3["S3/GCS Bucket"]
    end
    
    subgraph "Git"
        GIT["Git Repository"]
    end
    
    WORK --> |"dvc add"| CACHE
    CACHE --> |"dvc push"| S3
    DVC_FILES --> |"git commit"| GIT
    S3 --> |"dvc pull"| CACHE
    CACHE --> WORK
```

### Commands

```bash
# Track data file
dvc add data/raw/train.csv

# Push to remote
dvc push

# Pull on another machine
dvc pull
```

---

## Feature Engineering Pipeline

### Centralized Approach (CarVision Example)

```python
# src/carvision/features.py
class FeatureEngineer:
    """Centralized feature engineering for training and inference."""
    
    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fit and transform training data."""
        ...
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform inference data."""
        ...
```

**Benefits:**
- Single source of truth for feature logic
- Consistent features in training and serving
- Easy to update and version

---

## Inference Data Flow

### Real-time (API)

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI
    participant Val as Pydantic
    participant Model as sklearn Pipeline
    participant Resp as Response
    
    Client->>API: POST /predict
    API->>Val: Validate input
    Val-->>API: Valid data
    API->>Model: model.predict(X)
    Model-->>API: predictions
    API->>Resp: Format response
    Resp-->>Client: JSON result
```

### Batch Processing

```mermaid
graph LR
    CSV["Input CSV"] --> LOAD["Load Data"]
    LOAD --> VALID["Validate Schema"]
    VALID --> CHUNK["Chunk Processing"]
    CHUNK --> PRED["Model Predict"]
    PRED --> OUT["Output CSV"]
```

---

## Data Quality Checks

### Validation Rules

| Project | Check | Action |
|---------|-------|--------|
| BankChurn | CreditScore ∈ [300, 850] | Reject |
| BankChurn | Age ∈ [18, 100] | Reject |
| CarVision | Price > 0 | Filter |
| CarVision | Year ≥ 1900 | Filter |
| Telecom | mb_used ≥ 0 | Coerce to 0 |

### Evidently Monitoring

```python
from evidently import ColumnDriftMetric
from evidently.report import Report

# Create drift report
report = Report(metrics=[ColumnDriftMetric(column_name="CreditScore")])
report.run(reference_data=train_df, current_data=prod_df)
```

---

## Data Storage Locations

| Type | Path | Format |
|------|------|--------|
| Raw Data | `data/raw/` | CSV |
| Processed | `data/processed/` | Parquet |
| Model Artifacts | `models/` | Pickle |
| MLflow Artifacts | `mlruns/` | Various |
| Predictions | `results/` | CSV/JSON |

---

## Data Retention Policy

| Data Type | Retention | Notes |
|-----------|-----------|-------|
| Raw training data | Permanent | Versioned via DVC |
| Model artifacts | 90 days | Keep last 5 versions |
| Prediction logs | 30 days | For monitoring |
| MLflow experiments | Permanent | Historical record |
