# Projects Overview

Three ML systems built end-to-end: trained, containerized, deployed on Kubernetes, and monitored in production.

[![YouTube Demo](https://img.shields.io/badge/YouTube-Watch%20Demo-red?style=for-the-badge&logo=youtube)](https://youtu.be/qmw9VlgUcn8)

## Comparison (v3.3.1)

| Aspect | BankChurn | CarVision | NLPInsight |
|--------|-----------|-----------|------------|
| **Domain** | Banking (Retention) | Automotive (Pricing) | Finance (Sentiment) |
| **Type** | Binary Classification | Regression | Multi-class Classification |
| **Algorithm** | StackingClassifier (RF+GB+XGB+LGB→LR) | LightGBM + FeatureEngineer (24 features) | FinBERT (ProsusAI) / TF-IDF fallback |
| **Primary Metric** | AUC 0.87 | R² 0.80 | Acc 97% |
| **Why This Metric** | 20% churn rate makes accuracy deceptive; AUC measures rank-ordering | RMSE penalizes large errors in dollars; MAPE distorted by cheap cars | 3-class, no class <12%; F1-macro guards minority negative class |
| **Tests** | 199 | 52 | 74 |
| **Coverage** | 90% | 96% | 98% |
| **P50 / P95 Latency** | 170ms / 350ms | 91ms / 130ms | 180ms / 450ms |

Each project page explains the business problem, metric rationale, and cost of being wrong.

## Links

- [BankChurn Predictor](bankchurn.md) — threshold tuning, cost analysis, SHAP
- [CarVision Market Intelligence](carvision.md) — pricing asymmetry, Streamlit dashboard
- [NLPInsight Analyzer](nlpinsight.md) — domain transfer learning, dual backend

---

*Last Updated: March 2026 — v3.3.1*
