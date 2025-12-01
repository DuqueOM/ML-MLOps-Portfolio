# System Architecture

## Overview

TelecomAI Customer Intelligence is a machine learning service designed to recommend mobile plans ("Ultra" vs "Smart") based on user behavior. The system is built on a modular Python architecture, containerized with Docker, and exposed via a high-performance FastAPI interface.

## Components

```mermaid
graph TD
    User[Client / User] -->|HTTP POST /predict| API[FastAPI Service]
    API -->|Load| Model[ML Pipeline (Joblib)]
    Model -->|Transform| Preprocessor[StandardScaler]
    Model -->|Inference| Classifier[RandomForest/GradientBoosting]
    
    subgraph Training Pipeline
        RawData[(data/raw/users_behavior.csv)] -->|Load| ETL[Data Loader]
        ETL -->|Split| Splitter[Train/Test Split]
        Splitter -->|Train| Trainer[Model Training]
        Trainer -->|Evaluate| Evaluator[Metrics Calculation]
        Trainer -->|Save| Artifacts[Model Artifacts]
    end
```

### 1. Data Ingestion & Processing
- **Source:** CSV file (`data/raw/data/raw/users_behavior.csv`).
- **Logic:** `src/telecom/data.py` handles loading and schema validation.
- **Preprocessing:** Scikit-Learn `Pipeline` with `SimpleImputer` and `StandardScaler`. Encapsulated within the model artifact to ensure training-serving skew prevention.

### 2. Model Training
- **Framework:** Scikit-Learn.
- **Models:** Supports Logistic Regression, Random Forest, and Gradient Boosting via configuration.
- **Configuration:** Pydantic-based strict config (`src/telecom/config.py`) ensures type safety for hyperparameters.
- **Tracking:** Metrics (Accuracy, F1, ROC-AUC) are logged to `artifacts/metrics.json`.

### 3. Inference Service
- **Framework:** FastAPI with Uvicorn.
- **Lifecycle:** Model is loaded *once* at startup using `lifespan` events (Singleton pattern) to minimize latency.
- **Schema:** Input/Output validation via Pydantic models.

## Design Decisions & Trade-offs

| Decision | Choice | Rationale | Trade-off |
| :--- | :--- | :--- | :--- |
| **Config Format** | YAML + Pydantic | Combines human readability of YAML with strict validation of Python objects. | Requires an extra parsing step. |
| **Model format** | Joblib | Efficient for Scikit-Learn pipelines (handles numpy arrays well). | Python-specific serialization (security risk if loading untrusted models). |
| **API Framework** | FastAPI | Async support, auto-docs (Swagger), and Pydantic integration. | Newer ecosystem than Flask (though robust). |
| **Docker Image** | `python:3.11-slim` | Small image size, secure (non-root user). | Minimal build tools included (requires multi-stage or cleanups). |

## CI/CD & DevOps

- **CI Pipeline:** GitHub Actions runs linting (Ruff), type checking (Mypy), and tests (Pytest) on every push.
- **Containerization:** Dockerfile follows security best practices (non-root user, no-cache installs).
- **Version Control:** Data versioning via DVC (implied/ready for integration).
