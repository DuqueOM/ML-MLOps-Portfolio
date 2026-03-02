# Projects Overview

Three production-ready ML systems demonstrating enterprise MLOps practices.

[![YouTube Demo](https://img.shields.io/badge/YouTube-Watch%20Demo-red?style=for-the-badge&logo=youtube)](https://youtu.be/qmw9VlgUcn8)

## Comparison (v2.0.0)

| Aspect | BankChurn | CarVision | NLPInsight |
|--------|-----------|-----------|------------|
| **Domain** | Banking (Retention) | Automotive (Pricing) | Finance (Sentiment) |
| **Type** | Binary Classification | Regression | Multi-class Classification |
| **Algorithm** | VotingClassifier (LR+RF) | XGBRegressor + FeatureEngineer | TF-IDF + LogisticRegression |
| **Primary Metric** | AUC 0.8626 | R² 0.8246 | Accuracy 88.1% |
| **Coverage** | 88% | 95% | 76% |
| **Docker** | 2.11 GB (SHAP) | 1.76 GB | 2.05 GB |
| **Interface** | REST API | REST API + Streamlit | REST API |
| **Special** | SHAP explainability, drift detection | 4-tab dashboard, FeatureEngineer | Dual backend (transformer + sklearn) |

## Links

- [BankChurn Predictor](bankchurn.md)
- [CarVision Market Intelligence](carvision.md)
- [NLPInsight Analyzer](nlpinsight.md)

---

*Last Updated: March 2026*
