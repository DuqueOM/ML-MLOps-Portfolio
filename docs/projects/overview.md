# Projects Overview

Four ML systems built end-to-end: trained, containerized, deployed on Kubernetes, and monitored in production.

[![YouTube Demo](https://img.shields.io/badge/YouTube-Watch%20Demo-red?style=for-the-badge&logo=youtube)](https://youtu.be/qmw9VlgUcn8)

## Comparison (v3.5.0)

| Aspect | BankChurn | | NLPInsight | ChicagoTaxi |
|--------|-----------|-----------|------------|-------------|
| **Domain** | Banking (Retention) | Automotive (Pricing) | Finance (Sentiment) | Transportation (Demand) |
| **Type** | Binary Classification | Regression | Multi-class Classification | Batch Pipeline |
| **Algorithm** | StackingClassifier (RF+GB+XGB+LGB→LR) | LightGBM + FeatureEngineer (24 features) | FinBERT (ProsusAI) / TF-IDF fallback | PySpark ETL + RandomForest |
| **Primary Metric** | AUC 0.87 | R² 0.80 | Acc 97% | R² 0.91 |
| **Why This Metric** | 20% churn rate makes accuracy deceptive; AUC measures rank-ordering | RMSE penalizes large errors in dollars; MAPE distorted by cheap cars | 3-class, no class <12%; F1-macro guards minority negative class | Hourly demand counts; R² captures temporal periodicity |
| **Tests** | 199 | 52 | 74 | 122 |
| **Coverage** | 90% | 96% | 98% | 91% |
| **Throughput** | 170ms p50 | 91ms p50 | 180ms p50 | 19K rows/sec (batch) |

Each project page explains the business problem, metric rationale, and cost of being wrong.

## Links

- [BankChurn Predictor](bankchurn.md) — threshold tuning, cost analysis, SHAP
- [NLPInsight Analyzer](nlpinsight.md) — domain transfer learning, dual backend
- [ChicagoTaxi Demand Pipeline](chicagotaxi.md) — PySpark ETL, Dask batch prediction, 6.3M rows

---

*Last Updated: March 2026 — v3.5.0*
