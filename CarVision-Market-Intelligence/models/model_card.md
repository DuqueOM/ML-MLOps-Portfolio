# Model Card — CarVision Price Predictor v1.0

## Model Overview

| Field | Value |
|-------|-------|
| **Model Name** | CarVision-RandomForest |
| **Version** | 1.0.0 |
| **Type** | Regression (Price Prediction) |
| **Framework** | Scikit-learn |
| **Last Updated** | November 2025 |

---

## Purpose

**Primary Use**: Predict the market value of used vehicles based on specifications and condition.

**Intended Users**:
- Dealerships for pricing optimization
- Buyers for fair market value assessment
- Analysts for market trend analysis

**Out of Scope**:
- Insurance valuation (different methodology)
- Collector/antique vehicle pricing
- Commercial fleet valuation

---

## Model Architecture

```
Pipeline: [FeatureEngineer] → [Preprocessor] → [RandomForestRegressor]

FeatureEngineer:
  - vehicle_age = current_year - model_year
  - brand extraction from model name
  - Temporal features (if applicable)

Preprocessor:
  - Numerical: StandardScaler (odometer, vehicle_age)
  - Categorical: OneHotEncoder (brand, fuel, transmission)
  - Missing values: SimpleImputer

Model:
  - RandomForestRegressor
    - n_estimators=100
    - max_depth=15
    - min_samples_split=5
```

---

## Training Data

| Attribute | Value |
|-----------|-------|
| **Source** | US vehicle listings dataset |
| **Size** | ~50,000 records (after cleaning) |
| **Features** | 5+ input features |
| **Target** | `price` (USD) |
| **Date Range** | Various model years |
| **Split** | 80% train / 20% test |

### Feature Dictionary

| Feature | Type | Description | Example |
|---------|------|-------------|---------|
| model_year | int | Vehicle manufacture year | 2018 |
| odometer | int | Mileage in miles | 45000 |
| model | str | Vehicle make/model | "ford f-150" |
| fuel | str | Fuel type | gas, diesel, electric |
| transmission | str | Transmission type | automatic, manual |

### Engineered Features

| Feature | Derivation |
|---------|-----------|
| vehicle_age | current_year - model_year |
| brand | First word of model name |

---

## Performance Metrics

### Primary Metrics

| Metric | Train | Test | Target |
|--------|-------|------|--------|
| **RMSE** | **[INSERT]** | **[INSERT]** | — |
| **MAE** | **[INSERT]** | **[INSERT]** | — |
| **R²** | **[INSERT]** | **[INSERT]** | ≥ 0.80 |
| **MAPE** | **[INSERT]** | **[INSERT]** | ≤ 15% |

### Validation Methods

| Method | Result |
|--------|--------|
| **Cross-Validation (5-fold)** | R² = **[INSERT]** ± **[INSERT]** |
| **Bootstrap (1000 samples)** | 95% CI: **[INSERT]** - **[INSERT]** |
| **Temporal Backtest** | R² = **[INSERT]** (out-of-time) |

### Error Distribution

```
Residual Statistics:
  Mean:   ~0 (unbiased)
  Std:    $[INSERT]
  P5:     -$[INSERT]
  P95:    +$[INSERT]
```

---

## Limitations & Bias

### Known Limitations

1. **Price Range**: Best performance on vehicles $5,000-$50,000. Luxury vehicles (>$100K) have higher error.

2. **Regional Pricing**: Trained on US data. Prices in other markets may differ significantly.

3. **Missing Features**: Does not account for vehicle condition, accident history, or service records.

4. **Market Volatility**: Static model; does not adjust for supply/demand fluctuations.

### Bias Considerations

| Dimension | Assessment | Mitigation |
|-----------|------------|------------|
| **Brand** | Premium brands underrepresented | Monitored per-brand RMSE |
| **Age** | Newer vehicles have more data | Weighted sampling considered |
| **Geography** | US-only training data | Document limitation |

---

## How to Reproduce

### Training

```bash
cd CarVision-Market-Intelligence

# 1. Install dependencies
pip install -r requirements.txt

# 2. Ensure data is available
# Place vehicles_us.csv in project root or data/raw/

# 3. Train model
python main.py --mode train --config configs/config.yaml

# 4. Artifacts produced:
#    - artifacts/model.joblib (full pipeline)
#    - artifacts/metrics.json (evaluation metrics)
#    - artifacts/metrics_bootstrap.json (confidence intervals)
#    - artifacts/metrics_temporal.json (backtest results)
```

### Inference

```bash
# Start API
uvicorn app.fastapi_app:app --host 0.0.0.0 --port 8000

# Test prediction
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "model_year": 2018,
       "odometer": 45000,
       "model": "ford f-150",
       "fuel": "gas",
       "transmission": "automatic"
     }'
```

**Expected Response**:
```json
{
  "prediction": 24500.0,
  "vehicle_age": 6,
  "brand": "ford"
}
```

---

## Deployment

| Environment | URL | Status |
|-------------|-----|--------|
| **Local API** | `http://localhost:8000` | ✅ Available |
| **Streamlit Dashboard** | `http://localhost:8501` | ✅ Available |
| **GHCR Image** | `ghcr.io/duqueom/carvision-api:latest` | **[PENDING PUSH]** |

### Docker Deployment

```bash
# Pull and run
docker pull ghcr.io/duqueom/carvision-api:latest
docker run -p 8000:8000 ghcr.io/duqueom/carvision-api:latest

# Or run dashboard
docker run -p 8501:8501 ghcr.io/duqueom/carvision-dashboard:latest
```

---

## Dashboard Features

The Streamlit dashboard (`app/streamlit_app.py`) provides:

1. **Overview Tab**: Portfolio KPIs, price distribution, inventory breakdown
2. **Market Analysis Tab**: Investment insights, risk analysis
3. **Model Metrics Tab**: RMSE/MAE/R², bootstrap CIs, temporal backtest
4. **Price Predictor Tab**: Single-vehicle prediction with market percentile

---

## Monitoring & Maintenance

### Drift Detection

- **Feature Drift**: Monitor odometer and price distributions
- **Prediction Drift**: Track mean predicted price over time
- **Freshness**: Data should be updated monthly for market relevance

### Retraining Triggers

| Trigger | Threshold | Action |
|---------|-----------|--------|
| MAPE increase | > 20% | Schedule retrain |
| New vehicle models | Quarterly | Add to training data |
| Market shift | Manual trigger | Full retrain |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Nov 2025 | Initial release with centralized FeatureEngineer |

---

## Owners & Contacts

| Role | Name | Contact |
|------|------|---------|
| **Model Owner** | Daniel Duque | [GitHub](https://github.com/DuqueOM) |
| **MLOps Lead** | Daniel Duque | [LinkedIn](https://linkedin.com/in/duqueom) |

---

## References

- [Architecture Documentation](docs/ARCHITECTURE.md)
- [API Documentation](http://localhost:8000/docs)
- [Dashboard](http://localhost:8501)
- [Experiment Tracking (MLflow)](http://localhost:5000)
