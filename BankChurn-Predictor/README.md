# BankChurn Predictor

**Production-grade customer churn prediction — StackingClassifier ensemble with SHAP explainability**

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://python.org)
[![scikit-learn](https://img.shields.io/badge/sklearn-1.8-F7931E.svg)](https://scikit-learn.org)
[![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen.svg)]()
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](Dockerfile)

## Overview

BankChurn Predictor identifies customers at high risk of leaving the bank using an **ensemble ML pipeline** with real-time SHAP explanations. It demonstrates production ML with class-imbalanced data, model explainability, and full MLOps integration.

- **Production model**: StackingClassifier (RF + GB + XGB + LGB → LR meta-learner)
- **Explainability**: SHAP feature contributions via `?explain=true` (lazy by default)
- **API**: FastAPI with Prometheus metrics, batch inference, health checks
- **Experiment tracking**: 3 MLflow experiments (baseline → tuned → overfit demo)
- **Responsible AI**: Fairness audits (gender/geography), Evidently drift detection

## Model Performance (v3.0.0)

| Metric | Value | Context |
|--------|-------|---------|
| **AUC-ROC** | **0.87** | Excellent discrimination (benchmark: 0.75-0.80) |
| **F1-Score** | **0.62** | Above average for imbalanced churn (benchmark: 0.45-0.55) |
| **Precision** | **0.73** | 73% of predicted churns are actual churns |
| **Recall** | **0.54** | 54% of actual churns caught (precision-recall trade-off) |
| **API Latency** | **103ms p50 / 111ms p95** | In-pod (GKE); ~4.5s with `?explain=true` (KernelExplainer) |
| **Test Coverage** | **90%** | 199 tests |

### Pipeline Architecture

```python
Pipeline([
    ('features', ChurnFeatureEngineer()),          # 10 raw features → 25 engineered
    ('preprocessor', ColumnTransformer([
        ('num', StandardScaler(), numerical_cols),  # 25 → 38 encoded features
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols)
    ])),
    ('classifier', StackingClassifier(
        estimators=[
            ('rf', RandomForestClassifier(n_estimators=200, max_depth=15, class_weight='balanced')),
            ('gb', GradientBoostingClassifier(n_estimators=200, max_depth=5, subsample=0.8)),
            ('xgb', XGBClassifier(n_estimators=200, max_depth=6, scale_pos_weight=4)),
            ('lgbm', LGBMClassifier(n_estimators=200, max_depth=6, is_unbalance=True))
        ],
        final_estimator=LogisticRegression(C=1.0, max_iter=1000), cv=5
    ))
])
```

> **SHAP note**: `KernelExplainer` is used as the SHAP backend because `TreeExplainer` does not support `StackingClassifier`. SHAP values are computed in the original 10-feature space (interpretable by business). See [ADR-010](../docs/decisions/010-shap-kernelexplainer-bankchurn.md).

### Feature Importance (SHAP)

| Rank | Feature | Direction |
|------|---------|-----------|
| 1 | **Age** | Older (50+) → higher churn |
| 2 | **NumOfProducts** | Single product → higher risk |
| 3 | **IsActiveMember** | Inactive → much higher churn |
| 4 | **Geography_Germany** | Higher churn rate |
| 5 | **Balance** | Zero or very high → churn signal |

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Train
python main.py --seed 42 train --config configs/config.yaml --input data/raw/Churn.csv

# Serve
uvicorn app.fastapi_app:app --host 0.0.0.0 --port 8000

# Tests (90% coverage, 199 tests)
pytest tests/ -v --cov=src --cov=main
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/predict` | POST | Single churn prediction (add `?explain=true` for SHAP) |
| `/predict_batch` | POST | Batch predictions (up to 1,000 records) |
| `/health` | GET | Kubernetes health/readiness check |
| `/metrics` | GET | Prometheus metrics (request count, latency, churn rate) |
| `/model_info` | GET | Model metadata and version |

```bash
# Example prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"CreditScore":650,"Geography":"France","Gender":"Female","Age":40,"Tenure":3,"Balance":60000,"NumOfProducts":2,"HasCrCard":1,"IsActiveMember":1,"EstimatedSalary":50000}'

# Response
# {"prediction":1,"churn_probability":0.73,"risk_level":"HIGH","confidence":0.85,"feature_contributions":{...},"processing_time_ms":35}
```

## Data

| Attribute | Value |
|-----------|-------|
| **Records** | 10,000 (8,000 train / 2,000 test) |
| **Features** | 10 (5 numerical, 2 categorical, 3 binary) |
| **Target** | `Exited` — churned (1) or retained (0) |
| **Imbalance** | 3.9:1 (79.6% retained, 20.4% churned) |
| **Handling** | class_weight='balanced' + stratified CV |
| **Versioning** | DVC tracked |

See [data_card.md](data_card.md) for full schema and quality details.

## MLflow Experiments

| Run | Model | Test F1 | Test AUC | Purpose |
|-----|-------|---------|----------|---------|
| BC-1 | LogisticRegression | 0.29 | 0.77 | Baseline |
| **BC-2** | **StackingClassifier** | **0.62** | **0.87** | **Production** |
| BC-3 | RF (no regularization) | 0.58 | 0.85 | Overfit demo |

## Project Structure

```
BankChurn-Predictor/
├── app/fastapi_app.py          # API endpoints + SHAP
├── src/bankchurn/              # Core ML package
│   ├── config.py               # Pydantic config validation
│   ├── training.py             # Training orchestration
│   ├── prediction.py           # Inference logic
│   └── explainability.py       # SHAP integration
├── tests/                      # 199 tests (90% coverage)
├── configs/config.yaml         # Model + preprocessing config
├── data/raw/                   # Training data (DVC tracked)
├── models/                     # Trained model + model_card
├── monitoring/check_drift.py   # Evidently drift detection
├── Dockerfile                  # Production image
├── Makefile                    # Dev commands
└── pyproject.toml              # Dependencies
```

## Operational Metrics

| Metric | Value |
|--------|-------|
| Docker Image | 342 MB (`bankchurn:v3.5.0`, python:3.11-slim-bookworm) |
| Model Size | 4.1 MB (joblib compressed) |
| P50 / P95 Latency | 103ms / 111ms (in-pod, GKE) |
| SHAP Latency | ~4.5s in-pod (`?explain=true`, KernelExplainer + StackingClassifier) |
| Load Test | 0% error rate (Locust, 10 users, 2min, 979 requests via Ingress) |
| Drift Detection | PSI + KS via Evidently (weekly) |

## Tech Stack

- **ML**: scikit-learn (StackingClassifier), XGBoost, LightGBM, SHAP
- **API**: FastAPI + Pydantic + Uvicorn (2 workers)
- **Monitoring**: Prometheus custom metrics (`bankchurn_*`)
- **Responsible AI**: Fairness audits (gender/geography), Evidently drift
- **Container**: Multi-stage Docker, DVC data versioning
- **Config**: Pydantic-validated YAML

📄 [Model Card](models/model_card.md) · [Data Card](data_card.md) · [Full Docs](https://duqueom.github.io/ML-MLOps-Portfolio/projects/bankchurn/)
