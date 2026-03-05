# ChicagoTaxi Demand Pipeline

Process 6.3 million taxi trips into hourly demand predictions — the data engineering complement to the portfolio's online inference services.

## The Problem

Chicago has 77 community areas, each with different taxi demand patterns by hour, day, and season. Predicting hourly demand per area enables driver allocation optimization. The dataset is 2.8 GB (too large for pandas), requiring distributed processing.

## Why PySpark + Dask

| Stage | Tool | Reason |
|-------|------|--------|
| ETL | PySpark | Schema enforcement, distributed cleaning, partitioned Parquet export |
| Aggregation | PySpark | GroupBy over 5.3M rows into 357K hourly demand records |
| Batch Predict | Dask | Parallel inference across 4 partitions (19K rows/sec) |
| Serving | FastAPI | Query pre-computed predictions by area/hour |

pandas would OOM on the full CSV. PySpark handles the heavy ETL; Dask handles the embarrassingly parallel batch prediction. FastAPI serves the pre-computed results — no model inference at request time.

## Pipeline Metrics

| Metric | Value | Context |
|--------|-------|---------|
| Raw rows | 6,364,313 | Chicago Open Data Portal, 2013–2023 |
| Clean rows | 5,369,172 | 15.6% dropped (invalid duration, distance, area) |
| Hourly demand rows | 357,055 | Aggregated by area × hour × day |
| CSV → Parquet | 2.8 GB → 95 MB | 97% compression via columnar + snappy |
| ETL throughput | 4,741 rows/sec | PySpark local[*], 4g driver memory |
| Model R² | 0.905 | RandomForest, 200 trees, max_depth=10 |
| RMSE | 13.58 trips | On hourly demand counts |
| Batch prediction | 19,061 rows/sec | Dask, 4 partitions |

## Why R² 0.905 Is Strong

This is a regression problem on aggregated hourly counts. R² 0.905 means 90.5% of demand variance is explained by temporal + spatial features alone — without weather, events, or holiday calendars. RMSE of 13.58 on hourly counts means predictions are off by ~14 trips per hour per area on average.

For comparison, achieves R² 0.80 on vehicle pricing (a harder, higher-variance problem). The taxi demand model benefits from strong temporal periodicity.

## Operational

| Metric | Value |
|--------|-------|
| Test Coverage | 91% (122 tests) |
| CI Threshold | 85% |
| Docker Image | Python 3.11-slim, multi-stage |
| Model Size | ~2 MB (RandomForest, joblib) |
| API Endpoints | `/demand`, `/areas`, `/pipeline/status`, `/health`, `/metrics` |

## Data Cleaning Rules

| Rule | Threshold | Rows Affected |
|------|-----------|---------------|
| Trip duration | 60s < t < 86,400s | ~8% |
| Trip distance | 0.1 ≤ d ≤ 500 miles | ~3% |
| Community area | 1 ≤ area ≤ 77 | ~4% |
| Fare range | $0 ≤ fare ≤ $10,000 | <1% |
| Comma stripping | `"1,326"` → `1326` | All numeric fields |

## Try It

```bash
# Query demand for community area 8 at 2pm
curl "http://localhost:8004/demand?area=8&hour=14&limit=5"

# List all areas ranked by demand
curl "http://localhost:8004/areas"

# Pipeline ETL metadata
curl "http://localhost:8004/pipeline/status"
```

📄 [Full Model Card](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/ChicagoTaxi-Demand-Pipeline/model_card.md)

---

*Source: [Chicago Data Portal — Taxi Trips](https://data.cityofchicago.org/Transportation/Taxi-Trips/wrvz-psew)*
