# CarVision Market Intelligence

**Vehicle price prediction — LightGBM pipeline with Streamlit dashboard and FastAPI serving**

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://python.org)
[![LightGBM](https://img.shields.io/badge/LightGBM-Regression-02569B.svg)](https://lightgbm.readthedocs.io)
[![Coverage](https://img.shields.io/badge/coverage-96%25-brightgreen.svg)]()
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](Dockerfile)

## Overview

CarVision Market Intelligence predicts used vehicle prices using a **LightGBM regression pipeline** with centralized feature engineering. It demonstrates end-to-end ML with an interactive Streamlit dashboard for market analytics and a FastAPI production API.

- **Production model**: LightGBM (auto-selected over RF, XGBoost, Ridge via MLflow)
- **Feature engineering**: Centralized `FeatureEngineer` class (24 derived features)
- **Dual interface**: FastAPI REST API + Streamlit dashboard (4 analytics tabs)
- **Experiment tracking**: 4 MLflow experiments (Ridge → RF → XGBoost → LightGBM)
- **Responsible AI**: Error ratio analysis across vehicle segments

## Model Performance (v3.0.0)

| Metric | Value | Context |
|--------|-------|---------|
| **R²** | **0.80** | 80% of price variance explained (benchmark: 0.65-0.75) |
| **RMSE** | **$6,744** | Average prediction error (benchmark: $7,000-8,000) |
| **MAE** | **$3,973** | Median error is lower than RMSE — outliers in luxury segment |
| **MAPE** | **32.9%** | Acceptable for wide price range ($500–$375K) |
| **API Latency** | **<30ms p95** | FastAPI + LightGBM native inference |
| **Test Coverage** | **96%** | 183 tests |

### Pipeline Architecture

```python
pipeline = Pipeline([
    ('feature_engineer', FeatureEngineer()),
    ('preprocessor', ColumnTransformer([
        ('num_impute', SimpleImputer(strategy='median'), numeric_features),
        ('cat_encode', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])),
    ('scaler', StandardScaler()),
    ('regressor', LGBMRegressor(
        n_estimators=500, max_depth=8, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8, random_state=42
    ))
])
```

### Feature Engineering Highlights

The centralized `FeatureEngineer` class derives 24 features from raw vehicle data:
- **Temporal**: `vehicle_age`, `age_bins`, `is_classic` (>25 years)
- **Derived**: `mileage_per_year`, `condition_score`, `brand_tier`
- **Interactions**: `age × condition`, `mileage × fuel_type`

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Train (auto-selects best model via MLflow)
python main.py

# Serve API
uvicorn app.fastapi_app:app --host 0.0.0.0 --port 8000

# Launch dashboard
streamlit run app/streamlit_app.py --server.port 8501

# Tests (96% coverage, 183 tests)
pytest tests/ -v --cov=src --cov=app
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/predict` | POST | Single vehicle price prediction |
| `/predict_batch` | POST | Batch predictions (up to 1,000 vehicles) |
| `/health` | GET | Kubernetes health/readiness check |
| `/metrics` | GET | Prometheus metrics (request count, latency, predictions) |
| `/model_info` | GET | Model metadata, feature list, version |

```bash
# Example prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"year":2018,"manufacturer":"ford","model":"f-150","condition":"good","cylinders":"6 cylinders","fuel":"gas","odometer":45000,"transmission":"automatic","drive":"4wd","type":"truck","paint_color":"white","state":"ca"}'

# Response
# {"predicted_price":28450.0,"confidence_interval":{"low":21706,"high":35194},"processing_time_ms":12}
```

## Data

| Attribute | Value |
|-----------|-------|
| **Records** | 51,525 vehicles (41,220 train / 10,305 test) |
| **Features** | 12 raw → 24 engineered via `FeatureEngineer` |
| **Target** | `price` (USD, range: $500–$375,000) |
| **Source** | US used vehicle listings (Craigslist) |
| **Versioning** | DVC tracked |

See [data_card.md](data_card.md) for full schema, quality checks, and cleaning rules.

## MLflow Experiments

| Run | Model | R² | RMSE | Purpose |
|-----|-------|----|------|---------|
| CV-1 | Ridge | 0.52 | $10,400 | Linear baseline |
| CV-2 | RandomForest | 0.75 | $7,500 | Tree baseline |
| CV-3 | XGBoost | 0.78 | $7,100 | Boosting |
| **CV-4** | **LightGBM** | **0.80** | **$6,744** | **Production** |

## Project Structure

```
CarVision-Market-Intelligence/
├── app/
│   ├── fastapi_app.py          # REST API serving
│   └── streamlit_app.py        # Interactive dashboard (4 tabs)
├── src/carvision/              # Core ML package
│   ├── features.py             # FeatureEngineer class (24 features)
│   ├── data.py                 # Data loading + cleaning
│   └── config.py               # Pydantic config validation
├── tests/                      # 183 tests (96% coverage)
├── configs/config.yaml         # Model + feature config
├── data/raw/                   # Training data (DVC tracked)
├── models/                     # Trained model + model_card
├── monitoring/                 # Drift detection
├── Dockerfile                  # Production image
├── Makefile                    # Dev commands
└── pyproject.toml              # Dependencies
```

## Operational Metrics

| Metric | Value |
|--------|-------|
| Docker Image | 1.76 GB |
| Model Size | 5.7 MB (joblib compressed) |
| P95 Latency | <30ms (API), <2s (dashboard load) |
| Load Test | 0% error rate (Locust, 10 users, 2min) |
| Dashboard | Streamlit with Plotly + Altair charts |

## Tech Stack

- **ML**: LightGBM, scikit-learn (Pipeline + ColumnTransformer), custom FeatureEngineer
- **API**: FastAPI + Pydantic + Uvicorn (2 workers)
- **Dashboard**: Streamlit + Plotly + Altair (4 analytics tabs)
- **Monitoring**: Prometheus custom metrics (`carvision_*`)
- **Container**: Multi-stage Docker, DVC data versioning
- **Config**: Pydantic-validated YAML

📄 [Model Card](models/model_card.md) · [Data Card](data_card.md) · [Full Docs](https://duqueom.github.io/ML-MLOps-Portfolio/projects/carvision/)
