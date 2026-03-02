# CarVision Market Intelligence

Vehicle price prediction platform with interactive dashboard.

![CarVision API](../media/screenshots/apis/27-fastapi-swagger-carvision.png)

## Performance (v2.0.0)

| Metric | Value |
|--------|-------|
| **R²** | 0.8246 |
| **RMSE** | $6,273 |
| **MAE** | $3,671 |

## Architecture

`Vehicle Data → Data Cleaning (price 1K-500K, year≥1990) → FeatureEngineer (vehicle_age, brand tiers, depreciation, miles_per_year) → ColumnTransformer → XGBRegressor(n=500, depth=8, lr=0.05) → Price`

## Key Features

- **Centralized FeatureEngineer**: Single class for training/inference/analysis (prevents skew)
- **Data Leakage Prevention**: `price_per_mile`, `price_category` excluded from features
- **Streamlit Dashboard**: 4 tabs (Portfolio, Market, Metrics, Predictor)
- **Advanced Validation**: 5-fold CV, bootstrap CI, temporal backtest

## Operational

| Metric | Value |
|--------|-------|
| Test Coverage | 95% (37 tests) |
| Docker Image | 1.76 GB |
| Model Size | 5.7 MB |
| P95 Latency | <150ms |

## API

```bash
curl -X POST http://localhost:8002/predict \
  -H "Content-Type: application/json" \
  -d '{"model_year":2020,"odometer":30000,"fuel":"gas","transmission":"automatic","type":"sedan","condition":"excellent"}'
```

---

*Last Updated: March 2026*
