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
| Model R² | 0.9050 |
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

## Data Source

| Field | Details |
|-------|---------|
| Source | [Chicago Data Portal](https://data.cityofchicago.org/Transportation/Taxi-Trips/wrvz-psew) |
| Period | 2013–2023 |
| Rows | 6,364,313 |
| Size | 2.8 GB (CSV) |
| License | [Chicago Open Data Terms](https://www.chicago.gov/city/en/narr/foia/data_702702702702702702702702702702702702702702702702702702702702702702702702702702702702702702702702702702702702702702702702702702702702702702702702.html) |

## Why This Matters

This project demonstrates skills often required for ML/Data Engineering roles:
- **Distributed processing** with PySpark (not just pandas)
- **Parquet + partitioning** for efficient columnar storage (97% compression)
- **Batch ML inference** at scale with Dask
- **Separation of concerns**: ETL → Training → Serving as independent stages
- **Same infrastructure patterns** as the other portfolio services (K8s, GCS, Prometheus)
