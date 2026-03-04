# Model Card — ChicagoTaxi Demand Predictor

| Attribute | Value |
|-----------|-------|
| **Model ID** | `chicagotaxi-rf-v1.0.0` |
| **Model Type** | Regression (hourly demand count) |
| **Algorithm** | RandomForestRegressor (scikit-learn 1.8+) |
| **Primary Metric** | R² 0.905, RMSE 13.58 |
| **Training Data** | 357,055 aggregated hourly demand records |
| **Source Data** | 6,364,313 Chicago taxi trips (2013–2023) |
| **Production Status** | Active |
| **Last Updated** | March 2026 |

---

## Purpose

Predict **hourly taxi demand per community area** in Chicago to enable driver allocation optimization. The model answers: "How many trips will originate from area X in hour Y?"

### Why This Model Matters

Chicago has 77 community areas with vastly different demand patterns. Area 8 (Near North Side) averages 85 trips/hour at 6pm; area 54 (Riverdale) averages 0.3. Without demand prediction, drivers cluster in high-traffic areas and underserved neighborhoods wait longer.

### Out of Scope

- Real-time individual trip prediction (this is batch/aggregate)
- Fare prediction or route optimization
- Other cities without retraining on local data

---

## Performance

| Metric | Value | Context |
|--------|-------|---------|
| **R²** | 0.905 | 90.5% of demand variance explained by temporal + spatial features alone |
| **RMSE** | 13.58 trips | Average hourly prediction error |
| **MAE** | 4.67 trips | Median error is lower — RMSE penalizes peak-hour outliers |
| **Training set** | 285,644 rows (80%) | Random split with temporal stratification |
| **Test set** | 71,411 rows (20%) | Held-out evaluation |

### Why R² and Not MAPE

MAPE (Mean Absolute Percentage Error) is undefined when true demand = 0 and distorted when demand is low (e.g., 1 trip predicted as 2 = 100% MAPE). R² measures the proportion of variance explained, which is meaningful for count data across areas with wildly different baselines.

### Comparison with Portfolio

| Project | Metric | Value | Type |
|---------|--------|-------|------|
| CarVision | R² | 0.80 | Price regression |
| **ChicagoTaxi** | **R²** | **0.91** | Demand regression |

ChicagoTaxi benefits from strong temporal periodicity (rush hours, weekends) that vehicle pricing lacks.

---

## Features

| Feature | Type | Description | Importance |
|---------|------|-------------|------------|
| `hour` | int (0–23) | Hour of day | High — captures rush hour peaks |
| `day_of_week` | int (1–7) | Day of week (1=Sun, Spark convention) | High — weekday vs weekend |
| `is_weekend` | binary | Weekend indicator | Medium — derived from day_of_week |
| `pickup_community_area` | int (1–77) | Chicago community area ID | High — location is key driver |
| `avg_distance_miles` | float | Mean trip distance in the hour/area | Medium |
| `avg_fare` | float | Mean trip fare in the hour/area | Medium |
| `avg_speed_mph` | float | Mean trip speed in the hour/area | Low — correlates with time of day |

**Not included (intentional)**: weather, holidays, events. These would improve accuracy but add external data dependencies that complicate the batch pipeline.

---

## Hyperparameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `n_estimators` | 200 | Diminishing returns beyond 200 (tested 100, 200, 500) |
| `max_depth` | 10 | Prevents overfitting on area-specific patterns |
| `min_samples_leaf` | 5 | Smooths predictions for low-traffic areas |
| `n_jobs` | -1 | Full CPU parallelism for training speed |
| `random_state` | 42 | Reproducibility |

---

## Data Pipeline

| Stage | Tool | Input | Output | Throughput |
|-------|------|-------|--------|------------|
| **Extract** | PySpark 4.1 | 2.8 GB CSV | Schema-validated DataFrame | — |
| **Clean** | PySpark | 6.3M rows | 5.3M rows (15.6% dropped) | 4,741 rows/sec |
| **Aggregate** | PySpark | 5.3M trip rows | 357K hourly demand rows | — |
| **Export** | PySpark | DataFrame | 95 MB Parquet (97% compression) | — |
| **Train** | scikit-learn | 357K rows | model.joblib (~2 MB) | — |
| **Predict** | Dask (4 partitions) | 357K rows | Parquet with predictions | 19,061 rows/sec |
| **Serve** | FastAPI | Parquet | JSON API responses | <50ms p95 |

### Cleaning Rules

| Rule | Threshold | Rows Dropped |
|------|-----------|-------------|
| Trip duration | 60s < t < 86,400s | ~8% |
| Trip distance | 0.1 ≤ d ≤ 500 mi | ~3% |
| Community area | 1 ≤ area ≤ 77 | ~4% |
| Fare range | $0 ≤ fare ≤ $10,000 | <1% |

---

## Limitations

- **Aggregated model**: predicts hourly counts, not individual trip likelihood
- **No weather features**: peak-hour accuracy could improve 3-5% with temperature/precipitation
- **Chicago-specific**: community area IDs are unique to Chicago; retraining needed for other cities
- **Temporal cutoff**: training data ends 2023; post-pandemic mobility patterns may shift
- **Cold areas**: areas with <5 trips/hour have higher relative error (MAE matters more than RMSE there)

---

## Ethical Considerations

- **Public data**: sourced from [Chicago Open Data Portal](https://data.cityofchicago.org/Transportation/Taxi-Trips/wrvz-psew) under open license
- **No PII**: trip and taxi IDs are anonymized hashes in the source dataset
- **Fairness risk**: demand predictions by area could inadvertently reinforce service disparities if used to *reduce* coverage in low-demand (often low-income) areas. Predictions should inform *equitable* allocation, not justify abandonment
- **Transparency**: all cleaning rules and thresholds are documented in `src/chicagotaxi/cleaning.py`

---

*Model trained with Python 3.13 + scikit-learn locally. Production Docker image uses Python 3.11.*
