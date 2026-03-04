# Model Card — ChicagoTaxi Demand Predictor

## Model Details

| Field | Value |
|-------|-------|
| **Model type** | RandomForestRegressor (scikit-learn) |
| **Version** | 1.0.0 |
| **Task** | Hourly taxi demand prediction per community area |
| **Framework** | scikit-learn 1.4+ |
| **Training data** | 357,055 aggregated hourly demand records |
| **Source data** | 6.3M Chicago taxi trips (2013–2023) |

## Performance

| Metric | Value |
|--------|-------|
| R² | 0.9050 |
| RMSE | 13.58 trips |
| MAE | 4.67 trips |
| Training set | 285,644 rows |
| Test set | 71,411 rows |

## Features

| Feature | Type | Description |
|---------|------|-------------|
| `hour` | int (0–23) | Hour of day |
| `day_of_week` | int (1–7) | Day of week (1=Sun) |
| `is_weekend` | binary | Weekend indicator |
| `pickup_community_area` | int (1–77) | Chicago community area ID |
| `avg_distance_miles` | float | Average trip distance |
| `avg_fare` | float | Average trip fare |
| `avg_speed_mph` | float | Average trip speed |

## Hyperparameters

| Parameter | Value |
|-----------|-------|
| n_estimators | 200 |
| max_depth | 10 |
| min_samples_leaf | 5 |
| n_jobs | -1 (all cores) |
| random_state | 42 |

## Limitations

- Model trained on aggregated hourly data, not individual trips
- No weather features (could improve peak-hour predictions)
- Chicago-specific — not transferable to other cities without retraining
- Temporal coverage ends at 2023; patterns may shift post-pandemic

## Pipeline

1. **PySpark ETL**: 6.3M rows → 5.3M clean → 357K hourly aggregates
2. **Training**: RandomForest on aggregated features
3. **Batch prediction**: Dask parallel inference (19K rows/sec)
4. **Serving**: FastAPI queries pre-computed Parquet

## Ethical Considerations

- Data is publicly available from Chicago Open Data Portal
- No PII (trip/taxi IDs are anonymized hashes)
- Community area predictions should not be used for discriminatory resource allocation
