# CarVision Market Intelligence

Estimate used vehicle prices — and know when to trust the estimate.

![CarVision API](../media/screenshots/apis/27-fastapi-swagger-carvision.png)

## The Problem

Dealers need pricing guidance for inventory acquisition. A $15K error on a $20K vehicle is catastrophic; a $500 error on the same vehicle is noise. The metric must reflect this asymmetry.

## Why RMSE, Not MAPE

MAPE (32.9%) sounds high but is misleading: a $500 error on a $1,500 salvage car is 33% MAPE; the same $500 on a $30K sedan is 1.7%. MAPE distorts toward low-price vehicles that represent minimal financial risk. RMSE penalizes large errors quadratically — exactly the behavior we want for a pricing tool.

| Metric | Value | Why It Matters |
|--------|-------|----------------|
| **R²** | 0.80 | 80% of price variance explained; remaining 20% requires unobserved features (condition, accident history) |
| **RMSE** | $6,744 | Dollar-interpretable error; maps directly to pricing risk |
| **MAE** | $3,973 | Median-like error; less sensitive to outliers than RMSE |
| **MAPE** | 32.9% | Tracked but not optimized — distorted by sub-$10K segment |

**Model is unbiased** (residual mean = -$12), letting dealers apply their own margin strategy on top.

## Architecture

```
Vehicle Data → Data Cleaning (price $1K–$500K, year ≥ 1990)
             → FeatureEngineer (24 features: vehicle_age, brand extraction, etc.)
             → ColumnTransformer → LightGBM(n=500, depth=8, lr=0.05)
             → Predicted Price
```

**Why centralized FeatureEngineer**: A single class handles feature creation for training, API inference, and dashboard analysis. This prevents train-serve skew — the #1 silent failure mode in ML pricing systems. `price_per_mile` and `price_category` are explicitly excluded (they derive from the target variable).

## Operational

| Metric | Value | Context |
|--------|-------|---------|
| Test Coverage | 96% (52 tests) | CI threshold: 85% |
| Docker Image | 518 MB (API) / 950 MB (dashboard) | Multi-target Dockerfile; -71% from 1.76 GB |
| Model Size | 5.7 MB | Joblib compress=3 |
| P50 / P95 Latency | 91ms / 130ms | Locust, 10 users, GKE via port-forward |
| Dashboard | 4 tabs | Portfolio, Market Analysis, Metrics, Price Predictor |

## Responsible AI

- **Fairness**: Error ratio and MAE/RMSE parity audited by fuel type and condition
- **Drift**: PSI monitoring on feature distributions; RMSE regression beyond $8K triggers investigation
- **Validation**: Pandera schemas + 5-fold CV + bootstrap CI + temporal backtest

## Try It

```bash
curl -X POST http://localhost:8002/predict \
  -H "Content-Type: application/json" \
  -d '{"model_year":2020,"odometer":30000,"fuel":"gas","transmission":"automatic","type":"sedan","condition":"excellent"}'
```

📄 [Full Model Card](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/CarVision-Market-Intelligence/models/model_card.md) — includes metric rationale, performance benchmarks, and production decision narrative.

---

*Last Updated: March 2026 — v3.3.1*
