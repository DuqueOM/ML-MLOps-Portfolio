# BankChurn Predictor

Predict which bank customers are likely to leave — and quantify the cost of getting it wrong.

![BankChurn API](../media/screenshots/apis/25-fastapi-swagger-bankchurn.png)

## The Problem

A bank with 100K customers and a 20% annual churn rate loses ~$30M/year in lifetime value. The question isn't "can we predict churn?" — it's "at what threshold do we act, and what does each error cost?"

## Why AUC-ROC, Not Accuracy

The dataset is 80/20 retained/churned. A model predicting "no churn" for everyone scores 79.6% accuracy — and catches zero churners. AUC-ROC measures **rank-ordering quality** across all thresholds, independently of class imbalance.

| Metric | Value | Why It Matters |
|--------|-------|----------------|
| **AUC-ROC** | 0.87 | Rank-ordering: 87% of the time, a churner scores higher than a non-churner |
| **F1** | 0.62 | Harmonic mean at default threshold (0.50) |
| **Precision** | 0.73 | 73% of flagged customers actually churn |
| **Recall** | 0.54 | 54% of actual churners caught (at 0.50); **78% at production threshold 0.35** |

**Production threshold: 0.35** — a missed churner costs ~$1,500 LTV; an unnecessary retention offer costs ~$50. At 30:1 cost ratio, we favor recall over precision.

## Architecture

```
Request → Pydantic Validation → ColumnTransformer(SimpleImputer + StandardScaler + OneHotEncoder)
        → StackingClassifier(RF + GradientBoosting + XGBoost + LightGBM → LogisticRegression meta-learner)
        → Prediction + Risk Level + optional SHAP explanation
```

**Why StackingClassifier**: 4 diverse base learners capture complementary patterns (bagging + boosting + tree + gradient). AUC improved from 0.84 (best single model) to 0.87. CV variance is tight (±0.006), confirming generalization over memorization. See [ADR-003](../decisions/003-stacking-classifier-bankchurn.md).

## Operational

| Metric | Value | Context |
|--------|-------|---------|
| Test Coverage | 90% (199 tests) | CI threshold: 85% |
| Docker Image | 1.09 GB | Optimized from 2.11 GB (-48%) via multi-stage build |
| Model Size | 4.1 MB | Joblib compress=3; includes preprocessor + 4 base learners + meta-learner |
| P50 / P95 Latency | 170ms / 350ms | Locust, 10 users, GKE via port-forward |
| SHAP | Lazy, CPU-only | `?explain=true` adds ~200ms; skipped by default |

## Responsible AI

- **Fairness**: Disparate impact ratio and equal opportunity difference audited by Gender and Geography
- **Drift**: Evidently AI monitors PSI/KS per feature; alert fires if >30% features drift
- **Validation**: Pandera schemas reject invalid inputs (CreditScore ∈ [300, 850], Age > 0)

## Try It

```bash
curl -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -d '{"CreditScore":650,"Geography":"France","Gender":"Male","Age":40,"Tenure":5,"Balance":60000,"NumOfProducts":2,"HasCrCard":1,"IsActiveMember":1,"EstimatedSalary":50000}'
```

📄 [Full Model Card](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/BankChurn-Predictor/models/model_card.md) — includes metric rationale, performance benchmarks, and production decision narrative.

---

*Last Updated: March 2026 — v3.4.0*
