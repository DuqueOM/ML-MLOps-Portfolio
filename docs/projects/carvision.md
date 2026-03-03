# CarVision Market Intelligence

Vehicle price prediction platform with interactive dashboard.

![CarVision API](../media/screenshots/apis/27-fastapi-swagger-carvision.png)

## Performance (v3.3.0)

| Metric | Value |
|--------|-------|
| **R²** | 0.80 |
| **RMSE** | $6,744 |

## Architecture

`Vehicle Data → Data Cleaning (price 1K-500K, year≥1990) → FeatureEngineer (24 features) → ColumnTransformer → LightGBM(n=500, depth=8, lr=0.05) → Price`

## Key Features

- **Centralized FeatureEngineer**: Single class for training/inference/analysis (prevents skew)
- **Data Leakage Prevention**: `price_per_mile`, `price_category` excluded from features
- **Streamlit Dashboard**: 4 tabs (Portfolio, Market, Metrics, Predictor)
- **Fairness Audits**: Error ratio, MAE/RMSE parity by group (fuel type, condition)
- **Data Validation**: Pandera schemas (raw + inference)
- **Advanced Validation**: 5-fold CV, bootstrap CI, temporal backtest

## Operational

| Metric | Value |
|--------|-------|
| Test Coverage | 96% (52 tests) |
| Docker Image | 518 MB (optimized, -71%) |
| Model Size | 5.7 MB |
| P95 Latency | <170ms (K8s port-forward) |

## API

```bash
curl -X POST http://localhost:8002/predict \
  -H "Content-Type: application/json" \
  -d '{"model_year":2020,"odometer":30000,"fuel":"gas","transmission":"automatic","type":"sedan","condition":"excellent"}'
```

---

*Last Updated: March 2026 — v3.3.0*
