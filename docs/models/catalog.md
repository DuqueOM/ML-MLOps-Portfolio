# Model Catalog

**Production Model Registry** — All models tracked via MLflow (v3.0.0, Python 3.11.14, sklearn 1.8.0)

## Overview

| Project | Model ID | Algorithm | Size | Primary Metric | Status |
|---------|----------|-----------|------|----------------|--------|
| **BankChurn** | `bankchurn-stacking-v3.0.0` | StackingClassifier (RF+GB+XGB+LGB→LR) | 4.1 MB | AUC 0.87 | Production |
| **NLPInsight** | `nlpinsight-tfidf-v3.5.0` | TF-IDF + LogReg (prod) / FinBERT (GPU) | ~5 MB / ~440 MB | Acc 80.6% | Production |
| **ChicagoTaxi** | `chicagotaxi-rf-v3.5.0` | RandomForest (lag features) | ~2 MB | R² 0.9649 | Production |

## BankChurn Predictor

| Metric | Value |
|--------|-------|
| AUC-ROC | **0.87** |
| F1 (Churn) | 0.62 |
| Coverage | 90% (199 tests) |

**Pipeline**: `SimpleImputer → StandardScaler/OneHotEncoder → StackingClassifier(RF+GB+XGB+LGB→LR)`
**Features**: SHAP explainability, drift detection (KS+PSI+Evidently), fairness audits (disparate impact, equal opportunity)

## NLPInsight Analyzer

| Metric | Value |
|--------|-------|
| Accuracy | **80.6%** |
| F1 (macro) | 0.748 |
| Coverage | 98% (74 tests) |

**Pipeline**: `TF-IDF + LogisticRegression` (production) or `FinBERT Tokenizer → FinBERT (ProsusAI)` (GPU)
**Features**: Dual backend auto-detection, Twitter Financial News trained, fairness audits (F1 parity), batch support (500 texts)

## ChicagoTaxi Demand Pipeline

| Metric | Value |
|--------|-------|
| R² | **0.9649** |
| RMSE | 7.87 trips |
| Coverage | 91% (22 tests) |

**Pipeline**: `PySpark ETL → Lag Features → RandomForest (temporal split)`
**Features**: 6.3M trips processed, leak-free lag features, Dask batch prediction (19K rows/sec)

## Promotion Criteria

1. Primary metric exceeds baseline by ≥5%
2. Cross-validation std dev <3%
3. P95 inference <200ms
4. Test coverage >70%
5. Clean security scans
6. Model card updated

## Retraining Triggers ([ADR-006](../decisions/006-drift-triggered-retraining.md))

Automated via K8s CronJob → GitHub Actions `workflow_dispatch`.

| Trigger | BankChurn | ChicagoTaxi | NLPInsight |
|---------|-----------|-------------|------------|
| **Performance** | AUC <0.75 | R² <0.90 | F1-macro <0.60 |
| **Drift (PSI)** | PSI >0.20 | PSI >0.20 | Distribution shift >25% |
| **Scheduled** | Quarterly | Quarterly | Quarterly |

## Links

- [BankChurn Model Card](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/BankChurn-Predictor/models/model_card.md)
- [NLPInsight Model Card](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/NLPInsight-Analyzer/model_card.md)
- [ChicagoTaxi Model Card](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/ChicagoTaxi-Demand-Pipeline/model_card.md)

---

*Last Updated: March 2026 — v3.5.0*
