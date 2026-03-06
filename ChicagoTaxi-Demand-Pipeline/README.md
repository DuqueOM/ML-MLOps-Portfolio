# ChicagoTaxi Demand Pipeline

**Batch demand prediction pipeline processing 6.3M taxi trips with PySpark ETL and Dask inference.**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![PySpark](https://img.shields.io/badge/PySpark-4.1-E25A1C?style=flat-square&logo=apachespark&logoColor=white)](https://spark.apache.org)
[![Dask](https://img.shields.io/badge/Dask-2026-FDA061?style=flat-square&logo=dask&logoColor=white)](https://dask.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)

---

## Problem

Predict hourly taxi demand per Chicago community area to optimize driver allocation. The dataset contains **6.3M trips (2013-2023)** from the [Chicago Open Data Portal](https://data.cityofchicago.org/Transportation/Taxi-Trips/wrvz-psew) — too large for pandas, requiring distributed processing.

## Solution

| Stage | Tool | Input | Output |
|-------|------|-------|--------|
| **ETL** | PySpark | 2.8 GB CSV (6.3M rows) | 95 MB Parquet (partitioned) |
| **Aggregation** | PySpark | 5.3M clean trips | 357K hourly demand rows |
| **Training** | scikit-learn | 357K aggregated rows | RandomForest (R² 0.905) |
| **Batch Predict** | Dask | 357K rows × 4 partitions | 19K rows/sec throughput |
| **Serving** | FastAPI | Pre-computed Parquet | Query API for demand by area/hour |

## Key Metrics

| Metric | Value |
|--------|-------|
| Raw rows processed | 6,364,313 |
| Clean rows retained | 5,369,172 (84.4%) |
| ETL throughput | 4,741 rows/sec |
| Model R² | 0.905 |
| Model RMSE | 13.58 trips |
| Batch prediction throughput | 19,061 rows/sec |
| CSV → Parquet compression | 97% (2.8 GB → 95 MB) |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# 1. Download data from Chicago Open Data Portal
# Place CSV in data/raw/taxi_trips.csv

# 2. Run PySpark ETL
python scripts/spark_etl.py \
    --input data/raw/taxi_trips.csv \
    --output data/processed/taxi_trips_parquet

# 3. Train model + batch predict
python scripts/batch_predict.py \
    --input data/processed/taxi_trips_parquet/hourly_demand \
    --output data/processed/taxi_predictions \
    --train

# 4. Serve predictions via API
uvicorn app.fastapi_app:app --host 0.0.0.0 --port 8000
# Docs at http://localhost:8000/docs
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    DATA SOURCE                           │
│  Chicago Open Data Portal — 6.3M taxi trips (2.8 GB)    │
└──────────────────────┬──────────────────────────────────┘
                       │
              ┌────────▼────────┐
              │   PySpark ETL   │  local[*] or Dataproc/EMR
              │  5 stages:      │
              │  ingest → clean │
              │  → engineer     │
              │  → aggregate    │
              │  → export       │
              └────────┬────────┘
                       │
         ┌─────────────┴─────────────┐
         │                           │
┌────────▼────────┐      ┌──────────▼──────────┐
│  Trip Parquet   │      │  Hourly Demand      │
│  (partitioned   │      │  Parquet (357K rows) │
│   by year/month)│      └──────────┬──────────┘
└─────────────────┘                 │
                           ┌────────▼────────┐
                           │  Dask Batch     │
                           │  Prediction     │
                           │  (4 partitions) │
                           └────────┬────────┘
                                    │
                           ┌────────▼────────┐
                           │  FastAPI        │
                           │  Serving Layer  │
                           │  /demand        │
                           │  /areas         │
                           │  /pipeline/status│
                           └─────────────────┘
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check + predictions status |
| GET | `/demand?area=8&hour=14` | Query demand by area and hour |
| GET | `/areas` | Community area summaries with peak hours |
| GET | `/pipeline/status` | Last ETL run metadata |
| GET | `/metrics` | Prometheus metrics |

## Project Structure

```
ChicagoTaxi-Demand-Pipeline/
├── app/
│   └── fastapi_app.py          # API serving pre-computed predictions
├── configs/
│   └── config.yaml             # ETL and model configuration
├── scripts/
│   ├── spark_etl.py            # PySpark ETL pipeline (5 stages)
│   └── batch_predict.py        # Dask batch prediction + training
├── models/
│   ├── model.joblib             # Trained RandomForest
│   └── metrics.json             # Model evaluation metrics
├── tests/
│   ├── test_api.py              # FastAPI endpoint tests
│   └── test_etl.py              # ETL logic unit tests
├── Dockerfile                   # API serving image (Python 3.11)
├── requirements.txt             # Full dependencies (incl. PySpark, Dask)
└── requirements-prod.txt        # Production API dependencies only
```

## Data

| Attribute | Value |
|-----------|-------|
| **Raw Records** | 6,364,313 taxi trips (2013–2023) |
| **Clean Records** | 5,369,172 (84.4% retained after cleaning) |
| **Aggregated** | 357,055 hourly demand rows (model input) |
| **Target** | `demand_count` — trips per hour per community area |
| **Source** | [Chicago Open Data Portal](https://data.cityofchicago.org/Transportation/Taxi-Trips/wrvz-psew) |
| **Size** | 2.8 GB CSV → 95 MB Parquet (97% compression) |
| **Versioning** | Raw CSV in `data/raw/` (gitignored, too large for Git) |

See [data_card.md](data_card.md) for full schema, cleaning rules, and quality details.

## Operational Metrics

| Metric | Value |
|--------|-------|
| Docker Image | 154 MB (`chicagotaxi:v3.5.0`, python:3.11-slim-bookworm) |
| Model Size | ~2 MB (joblib compressed) |
| P50 / P95 Latency | 75ms / 460ms `/demand` (in-pod, GKE) |
| ETL Throughput | 4,741 rows/sec (PySpark local[*]) |
| Batch Prediction | 19,061 rows/sec (Dask, 4 partitions) |
| Test Coverage | 91% (22 tests) |

## Tech Stack

- **ETL**: PySpark 4.1 (distributed cleaning, aggregation, Parquet export)
- **ML**: scikit-learn RandomForestRegressor (R² 0.905)
- **Batch Inference**: Dask (parallel prediction with partitioned data)
- **API**: FastAPI + Pydantic + Uvicorn (serves pre-computed predictions)
- **Monitoring**: Prometheus custom metrics (`chicagotaxi_*`)
- **Container**: Docker (Python 3.11-slim)
- **Config**: YAML-based pipeline configuration

📄 [Model Card](model_card.md) · [Data Card](data_card.md) · [Full Docs](https://duqueom.github.io/ML-MLOps-Portfolio/projects/chicagotaxi/)
