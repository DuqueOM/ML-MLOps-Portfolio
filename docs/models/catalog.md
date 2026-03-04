# Model Catalog

**Production Model Registry** — All models tracked via MLflow (v3.0.0, Python 3.11.14, sklearn 1.8.0)

## Overview

| Project | Model ID | Algorithm | Size | Primary Metric | Status |
|---------|----------|-----------|------|----------------|--------|
| **BankChurn** | `bankchurn-stacking-v3.0.0` | StackingClassifier (RF+GB+XGB+LGB→LR) | 4.1 MB | AUC 0.87 | Production |
| **CarVision** | `carvision-lgbm-v3.0.0` | LightGBM + FeatureEngineer (24 features) | 5.7 MB | R² 0.80 | Production |
| **NLPInsight** | `nlpinsight-finbert-v3.0.0` | FinBERT (ProsusAI) / TF-IDF fallback | ~260 MB / 309 KB | Acc 97% | Production |

## BankChurn Predictor

| Metric | Value |
|--------|-------|
| AUC-ROC | **0.87** |
| F1 (Churn) | 0.62 |
| Coverage | 90% (199 tests) |

**Pipeline**: `SimpleImputer → StandardScaler/OneHotEncoder → StackingClassifier(RF+GB+XGB+LGB→LR)`
**Features**: SHAP explainability, drift detection (KS+PSI+Evidently), fairness audits (disparate impact, equal opportunity)

## CarVision Market Intelligence

| Metric | Value |
|--------|-------|
| R² | **0.80** |
| RMSE | $6,744 |
| Coverage | 96% (52 tests) |

**Pipeline**: `FeatureEngineer (24 features) → ColumnTransformer → LightGBM(n=500, depth=8, lr=0.05)`
**Features**: Centralized FeatureEngineer, data leakage prevention, fairness audits (error ratio), Streamlit dashboard (4 tabs)

## NLPInsight Analyzer

| Metric | Value |
|--------|-------|
| Accuracy | **97%** |
| F1 (weighted) | 0.97 |
| Coverage | 98% (74 tests) |

**Pipeline**: `FinBERT Tokenizer → FinBERT (ProsusAI)` (production) or `TF-IDF → LogisticRegression` (fallback)
**Features**: Dual backend auto-detection, Financial PhraseBank trained, fairness audits (F1 parity), batch support (500 texts)

## Promotion Criteria

1. Primary metric exceeds baseline by ≥5%
2. Cross-validation std dev <3%
3. P95 inference <200ms
4. Test coverage >70%
5. Clean security scans
6. Model card updated

## Retraining Triggers ([ADR-006](../decisions/006-drift-triggered-retraining.md))

Automated via K8s CronJob → GitHub Actions `workflow_dispatch`.

| Trigger | BankChurn | CarVision | NLPInsight |
|---------|-----------|-----------|------------|
| **Performance** | AUC <0.75 | RMSE >$10K | F1-macro <0.80 |
| **Drift (PSI)** | PSI >0.20 | PSI >0.20 | Distribution shift >25% |
| **Scheduled** | Quarterly | Quarterly | Quarterly |

## Links

- [BankChurn Model Card](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/BankChurn-Predictor/models/model_card.md)
- [CarVision Model Card](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/CarVision-Market-Intelligence/models/model_card.md)
- [NLPInsight Model Card](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/NLPInsight-Analyzer/model_card.md)

---

*Last Updated: March 2026 — v3.3.1*
