# Model Catalog

**Production Model Registry** — All models tracked via MLflow (v2.0.0, Python 3.11.14, sklearn 1.8.0)

## Overview

| Project | Model ID | Algorithm | Size | Primary Metric | Status |
|---------|----------|-----------|------|----------------|--------|
| **BankChurn** | `bankchurn-voting-v2.0.0` | VotingClassifier (LR+RF) | 4.1 MB | AUC 0.8626 | Production |
| **CarVision** | `carvision-xgb-v2.0.0` | XGBRegressor + FeatureEngineer | 5.7 MB | R² 0.8246 | Production |
| **NLPInsight** | `nlpinsight-tfidf-v2.0.0` | TF-IDF + LogisticRegression | 309 KB | Accuracy 88.08% | Production |

## BankChurn Predictor

| Metric | Value |
|--------|-------|
| AUC-ROC | **0.8626** |
| F1 (Churn) | 0.616 |
| Precision | 67.35% |
| Recall | 56.76% |
| CV AUC (5-fold) | 0.856 ± 0.005 |

**Pipeline**: `SimpleImputer → StandardScaler/OneHotEncoder → VotingClassifier(LR + RF, soft, weights=[1,2])`
**Features**: SHAP explainability, drift detection (PSI), fairness analysis

## CarVision Market Intelligence

| Metric | Value |
|--------|-------|
| R² | **0.8246** |
| RMSE | $6,273 |
| MAE | $3,671 |

**Pipeline**: `FeatureEngineer (24 features) → ColumnTransformer → XGBRegressor(n=500, depth=8, lr=0.05)`
**Features**: Centralized FeatureEngineer, data leakage prevention, Streamlit dashboard (4 tabs)

## NLPInsight Analyzer

| Metric | Value |
|--------|-------|
| Accuracy | **88.08%** |
| F1 (macro) | 0.826 |
| Precision (macro) | 87.94% |

**Pipeline**: `TF-IDF Vectorizer → LogisticRegression` (sklearn) or `AutoTokenizer → DistilBERT` (transformer)
**Features**: Dual backend auto-detection, Financial PhraseBank trained, batch support (500 texts)

## Promotion Criteria

1. Primary metric exceeds baseline by ≥5%
2. Cross-validation std dev <3%
3. P95 inference <200ms
4. Test coverage >70%
5. Clean security scans
6. Model card updated

## Retraining Triggers

| Trigger | BankChurn | CarVision | NLPInsight |
|---------|-----------|-----------|------------|
| **Performance** | AUC <0.75 | R² <0.70 | Accuracy <0.80 |
| **Drift** | >30% features | >30% features | >30% features |
| **Scheduled** | Quarterly | Quarterly | Quarterly |

## Links

- [BankChurn Model Card](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/BankChurn-Predictor/models/model_card.md)
- [CarVision Model Card](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/CarVision-Market-Intelligence/models/model_card.md)
- [NLPInsight Model Card](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/NLPInsight-Analyzer/models/model_card.md)

---

*Last Updated: March 2026*
