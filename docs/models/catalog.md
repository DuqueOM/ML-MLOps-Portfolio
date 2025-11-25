# Model Catalog

Registry of trained models and their metadata. All models are tracked via MLflow for full reproducibility.

---

## Overview

| Project | Model Type | Version | Status | Primary Metric |
|---------|-----------|---------|--------|----------------|
| BankChurn | VotingClassifier | 1.0.0 | Production | AUC-ROC: 0.853 |
| CarVision | RandomForest | 1.0.0 | Production | R²: 0.766 |
| TelecomAI | VotingClassifier | 1.0.0 | Production | AUC-ROC: 0.840 |

---

## BankChurn Predictor

### Production Model

| Attribute | Value |
|-----------|-------|
| **Model Name** | BankChurnClassifier |
| **Version** | 1.0.0 |
| **Algorithm** | VotingClassifier (LR + RF) |
| **MLflow Experiment** | `898454169632142870` |
| **MLflow Run ID** | `2baafacf2b9e40e8a7eee0e1bdf1993c` |
| **Artifact Path** | `models/model.pkl` |
| **Created** | 2025-11-23 |

### Hyperparameters

```yaml
logistic_regression:
  C: 1.0
  max_iter: 1000
  solver: lbfgs

random_forest:
  n_estimators: 100
  max_depth: 10
  min_samples_split: 5
  min_samples_leaf: 2
  class_weight: balanced

voting:
  voting: soft
  weights: [1, 2]
```

### Training Configuration

```yaml
data:
  train_path: data/raw/train.csv
  test_size: 0.2
  random_state: 42

preprocessing:
  numerical_features:
    - CreditScore
    - Age
    - Tenure
    - Balance
    - NumOfProducts
    - EstimatedSalary
  categorical_features:
    - Geography
    - Gender
  imputer:
    numerical: median
    categorical: most_frequent
  scaler: StandardScaler
  encoder: OneHotEncoder

training:
  cv_folds: 5
  scoring: roc_auc
```

### Performance Metrics

| Metric | CV Mean ± Std | Test Set |
|--------|---------------|----------|
| AUC-ROC | 0.844 ± 0.018 | 0.853 |
| Accuracy | — | 0.857 |
| Precision | 0.672 ± 0.026 | 0.692 |
| Recall | 0.537 ± 0.038 | 0.536 |
| F1 Score | 0.596 ± 0.031 | 0.604 |

### Artifacts

| Artifact | Path | Size |
|----------|------|------|
| Model Pipeline | `models/model.pkl` | ~2 MB |
| Training Results | `results/training_results.json` | 5 KB |
| Metrics | `metrics.json` | 1 KB |
| MLflow Artifacts | `mlruns/898454169632142870/` | ~10 MB |

---

## CarVision Market Intelligence

### Production Model

| Attribute | Value |
|-----------|-------|
| **Model Name** | CarVisionRegressor |
| **Version** | 1.0.0 |
| **Algorithm** | RandomForestRegressor |
| **Artifact Path** | `models/model_v1.0.0.pkl` |
| **Created** | 2025-11-20 |

### Hyperparameters

```yaml
random_forest:
  n_estimators: 100
  max_depth: 15
  min_samples_split: 5
  min_samples_leaf: 2
  random_state: 42
```

### Training Configuration

```yaml
data:
  train_path: data/raw/vehicles.csv
  target: price
  filters:
    min_price: 1000
    max_price: 500000
    min_year: 1990
    max_odometer: 500000

preprocessing:
  drop_columns:
    - price_per_mile
    - price_category
  numerical_features: auto
  categorical_features: auto
```

### Performance Metrics

| Metric | Value |
|--------|-------|
| R² | 0.766 |
| RMSE | $4,794.27 |
| MAE | $2,370.70 |
| MAPE | 27.6% |

### Artifacts

| Artifact | Path | Size |
|----------|------|------|
| Model Pipeline | `models/model_v1.0.0.pkl` | ~5 MB |
| Metrics | `artifacts/metrics.json` | 1 KB |
| Baseline Metrics | `artifacts/metrics_baseline.json` | 1 KB |

---

## TelecomAI Customer Intelligence

### Production Model

| Attribute | Value |
|-----------|-------|
| **Model Name** | TelecomClassifier |
| **Version** | 1.0.0 |
| **Algorithm** | VotingClassifier |
| **MLflow Experiment** | `211673707199893969` |
| **MLflow Run ID** | `5204423338e54f4e85719d4b5d08c5a8` |
| **Artifact Path** | `models/model.pkl` |
| **Created** | 2025-11-20 |

### Hyperparameters

```yaml
voting_classifier:
  voting: soft
  estimators:
    - logistic_regression:
        C: 1.0
        max_iter: 1000
    - random_forest:
        n_estimators: 100
        max_depth: 10
```

### Performance Metrics

| Metric | Value |
|--------|-------|
| AUC-ROC | 0.840 |
| Accuracy | 81.2% |
| Precision | 81.7% |
| Recall | 49.7% |
| F1 Score | 0.618 |

### Artifacts

| Artifact | Path | Size |
|----------|------|------|
| Model Pipeline | `models/model.pkl` | ~1.5 MB |
| Metrics | `artifacts/metrics.json` | 1 KB |
| MLflow Artifacts | `mlruns/211673707199893969/` | ~5 MB |

---

## Model Versioning

### Version Scheme

Models follow semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes to input/output schema
- **MINOR**: New features, improved performance
- **PATCH**: Bug fixes, minor adjustments

### Promotion Workflow

```mermaid
graph LR
    DEV["Development"] --> STAGING["Staging"]
    STAGING --> PROD["Production"]
    
    DEV -->|"train"| EXP["MLflow Experiment"]
    EXP -->|"register"| REG["Model Registry"]
    REG -->|"promote"| STAGING
    STAGING -->|"validate"| PROD
```

---

## Accessing Models

### Via MLflow

```python
import mlflow

# Set tracking URI
mlflow.set_tracking_uri("http://localhost:5000")

# Load production model
model = mlflow.sklearn.load_model("models:/BankChurnClassifier/Production")

# Make prediction
prediction = model.predict(X)
```

### Via Local Path

```python
import joblib

# Load from file
model = joblib.load("models/model.pkl")

# Make prediction
prediction = model.predict(X)
```

---

## Model Cards

Each project includes a detailed model card:

- [BankChurn Model Card](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/BankChurn-Predictor/models/model_card.md)
- [CarVision Model Card](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/CarVision-Market-Intelligence/models/model_card.md)
- [TelecomAI Model Card](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/TelecomAI-Customer-Intelligence/models/model_card.md)
