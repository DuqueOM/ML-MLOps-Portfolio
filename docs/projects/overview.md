# Projects Overview

Three ML systems built end-to-end: trained, containerized, deployed on Kubernetes, and monitored in production.

[![YouTube Demo](https://img.shields.io/badge/YouTube-Watch%20Demo-red?style=for-the-badge&logo=youtube)](https://youtu.be/qmw9VlgUcn8)

## Comparison (v3.3.0)

| Aspect | BankChurn | CarVision | NLPInsight |
|--------|-----------|-----------|------------|
| **Domain** | Banking (Retention) | Automotive (Pricing) | Finance (Sentiment) |
| **Type** | Binary Classification | Regression | Multi-class Classification |
| **Algorithm** | StackingClassifier (RF+GB+XGB+LGB→LR) | LightGBM + FeatureEngineer (24 features) | FinBERT (ProsusAI) / TF-IDF fallback |
| **Primary Metric** | AUC 0.87 | R² 0.80 | Acc 97% |
| **Tests** | 198 | 52 | 74 |
| **Coverage** | 90% | 96% | 98% |
| **Interface** | REST API | REST API + Streamlit | REST API |
| **Fairness** | Disparate impact, equal opportunity | Error ratio, MAE parity | F1 parity |
| **Special** | SHAP explainability, drift detection | 4-tab dashboard, FeatureEngineer | Dual backend (transformer + sklearn) |

## Links

- [BankChurn Predictor](bankchurn.md)
- [CarVision Market Intelligence](carvision.md)
- [NLPInsight Analyzer](nlpinsight.md)

---

*Last Updated: March 2026 — v3.3.0*
