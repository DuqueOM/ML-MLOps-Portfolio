# System Architecture Overview

This document describes the high-level architecture of the ML-MLOps Portfolio, including system components, data flow, and deployment infrastructure.

## System Diagram

```mermaid
graph TB
    subgraph "Data Sources"
        DS1[("Bank Customer Data")]
        DS2[("Vehicle Listings")]
        DS3[("Telecom Usage Data")]
    end

    subgraph "Data Layer"
        DVC["DVC<br/>(Data Versioning)"]
        RAW["Raw Data<br/>data/raw/"]
        PROC["Processed Data<br/>data/processed/"]
    end

    subgraph "Training Pipeline"
        FE["Feature Engineering"]
        TRAIN["Model Training"]
        EVAL["Model Evaluation"]
        REG["Model Registry<br/>(MLflow)"]
    end

    subgraph "Serving Layer"
        API1["BankChurn API<br/>:8001"]
        API2["CarVision API<br/>:8002"]
        API3["TelecomAI API<br/>:8003"]
        DASH["Streamlit Dashboard<br/>:8501"]
    end

    subgraph "Monitoring"
        PROM["Prometheus<br/>:9090"]
        GRAF["Grafana<br/>:3000"]
        EVID["Evidently<br/>(Drift Detection)"]
    end

    DS1 --> DVC
    DS2 --> DVC
    DS3 --> DVC
    DVC --> RAW
    RAW --> PROC
    PROC --> FE
    FE --> TRAIN
    TRAIN --> EVAL
    EVAL --> REG
    REG --> API1
    REG --> API2
    REG --> API3
    API2 --> DASH
    API1 --> PROM
    API2 --> PROM
    API3 --> PROM
    PROM --> GRAF
    API1 --> EVID
    API2 --> EVID
    API3 --> EVID
```

## Component Overview

### Data Layer

| Component | Purpose | Technology |
|-----------|---------|------------|
| **DVC** | Data versioning and remote storage | DVC + S3/GCS |
| **Raw Data** | Original datasets | CSV/Parquet |
| **Processed Data** | Cleaned and transformed data | Pandas DataFrames |

### Training Pipeline

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Feature Engineering** | Transform raw data into features | Scikit-learn Pipelines |
| **Model Training** | Train ML models | XGBoost, RandomForest, Ensemble |
| **Evaluation** | Compute metrics and validate | Pytest, Custom metrics |
| **Model Registry** | Version and store models | MLflow |

### Serving Layer

| Component | Purpose | Technology |
|-----------|---------|------------|
| **REST APIs** | Serve predictions | FastAPI + Uvicorn |
| **Dashboard** | Interactive visualization | Streamlit |
| **Containers** | Package applications | Docker (multi-stage) |

### Monitoring

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Prometheus** | Metrics collection | Prometheus + exporters |
| **Grafana** | Dashboards and alerting | Grafana |
| **Evidently** | ML model monitoring | Evidently AI |

## Project-Specific Architectures

### BankChurn Predictor

```mermaid
graph LR
    subgraph "Input"
        REQ["API Request<br/>(JSON)"]
    end

    subgraph "Processing Pipeline"
        VAL["Pydantic<br/>Validation"]
        PRE["Preprocessor<br/>(ColumnTransformer)"]
        MOD["Ensemble Model<br/>(VotingClassifier)"]
    end

    subgraph "Output"
        PRED["Prediction"]
        PROB["Probability"]
        RISK["Risk Level"]
    end

    REQ --> VAL
    VAL --> PRE
    PRE --> MOD
    MOD --> PRED
    MOD --> PROB
    PROB --> RISK
```

**Key Design Decisions:**

- **Unified Pipeline**: Preprocessor + Model in single sklearn Pipeline
- **Config Validation**: Pydantic for strict configuration
- **Imbalance Handling**: SMOTE and class weights support

### CarVision Market Intelligence

```mermaid
graph LR
    subgraph "Input"
        CSV["Vehicle Data<br/>(CSV)"]
        API["API Request"]
    end

    subgraph "Feature Pipeline"
        CLEAN["Data Cleaning<br/>(filters)"]
        FEAT["FeatureEngineer<br/>(centralized)"]
        PREP["Preprocessor"]
    end

    subgraph "Model"
        RF["RandomForest<br/>Regressor"]
    end

    subgraph "Output"
        PRICE["Price Prediction"]
        ANAL["Market Analysis"]
        DASH["Dashboard"]
    end

    CSV --> CLEAN
    API --> CLEAN
    CLEAN --> FEAT
    FEAT --> PREP
    PREP --> RF
    RF --> PRICE
    RF --> ANAL
    ANAL --> DASH
```

**Key Design Decisions:**

- **Centralized Feature Engineering**: Single `FeatureEngineer` class for training, inference, and analysis
- **No Data Leakage**: `price_per_mile` and `price_category` dropped from features (they depend on target)
- **Dual Interface**: FastAPI for programmatic access, Streamlit for interactive exploration

### TelecomAI Customer Intelligence

```mermaid
graph LR
    subgraph "Input"
        USAGE["Usage Metrics"]
    end

    subgraph "Pipeline"
        FE["Feature Engineering"]
        PRE["Preprocessing"]
        VC["VotingClassifier"]
    end

    subgraph "Output"
        PLAN["Plan Recommendation"]
        CONF["Confidence Score"]
    end

    USAGE --> FE
    FE --> PRE
    PRE --> VC
    VC --> PLAN
    VC --> CONF
```

**Key Design Decisions:**

- **Voting Classifier**: Combines multiple base models for robust predictions
- **Domain Features**: Telecom-specific feature engineering

## Deployment Architecture

```mermaid
graph TB
    subgraph "Developer"
        DEV["Local Dev"]
    end

    subgraph "CI/CD"
        GH["GitHub Actions"]
        TEST["Tests & Linting"]
        BUILD["Docker Build"]
        SCAN["Security Scan"]
    end

    subgraph "Registry"
        GHCR["GitHub Container Registry"]
    end

    subgraph "Deployment"
        K8S["Kubernetes Cluster"]
        HPA["Horizontal Pod Autoscaler"]
        ING["Ingress Controller"]
    end

    DEV -->|push| GH
    GH --> TEST
    TEST --> BUILD
    BUILD --> SCAN
    SCAN -->|push image| GHCR
    GHCR -->|pull| K8S
    K8S --> HPA
    K8S --> ING
```

## Technology Stack Summary

| Layer | Technologies |
|-------|--------------|
| **Languages** | Python 3.11+, Bash |
| **ML Frameworks** | Scikit-learn, XGBoost, LightGBM |
| **Web Frameworks** | FastAPI, Streamlit |
| **MLOps** | MLflow, DVC, Evidently |
| **Containers** | Docker, Docker Compose |
| **Orchestration** | Kubernetes, GitHub Actions |
| **Monitoring** | Prometheus, Grafana |
| **Infrastructure** | Terraform (AWS/GCP) |

---

!!! note "Diagram Source"
    All diagrams are written in Mermaid and can be edited directly in the markdown files.
    Source files are located in `docs/architecture/`.
