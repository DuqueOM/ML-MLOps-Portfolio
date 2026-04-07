# Model Validation Criteria

## Acceptance Rules

1. **Minimum threshold**: New model MUST meet the absolute minimum metric
2. **No regression**: New model MUST NOT regress >2% from current baseline
3. **Cross-validation**: CV score must be within 1 std of mean (no overfitting)
4. **Inference time**: p95 latency must remain <500ms under load

## Per-Service Criteria

### BankChurn-Predictor (Classification)

| Metric | Minimum | Current Baseline (v3.0.0) | Notes |
|--------|---------|--------------------------|-------|
| AUC-ROC | ≥ 0.85 | 0.8693 | Primary metric |
| F1 Score | ≥ 0.60 | 0.6243 | At threshold 0.35 |
| Recall | ≥ 0.70 | ~0.78 | Churner detection priority |
| CV AUC | within 1σ | 0.856 ± 0.005 | Overfitting check |

**Business context**: Missed churner costs $1,500-$3,000 LTV. False retention offer costs ~$50. 30:1 cost ratio justifies threshold 0.35 (not 0.50).

### NLPInsight-Analyzer (NLP Sentiment)

| Metric | Minimum | Current Baseline (v3.0.0) | Notes |
|--------|---------|--------------------------|-------|
| Accuracy | ≥ 0.95 | 0.9691 | Primary metric |
| F1-weighted | ≥ 0.95 | 0.9695 | Class balance check |
| Inference time | <200ms | ~87ms avg | FinBERT is heavier than TF-IDF |

### ChicagoTaxi-Demand-Pipeline (Regression)

| Metric | Minimum | Current Baseline (v3.0.0) | Notes |
|--------|---------|--------------------------|-------|
| R² | ≥ 0.75 | 0.7955 | Primary metric |
| RMSE | ≤ $7,500 | $6,744 | Absolute error bound |
| MAE | report only | — | Complementary metric |

**Data integrity**: Verify no data leakage — no same-period aggregate features (avg_fare, avg_speed). Use only lag features (1h, 24h, 168h, rolling 24h) with temporal train/test split.

## Rejection Procedure

If new model fails validation:
1. Log failure reason in MLflow
2. Keep current production model active
3. Investigate root cause (data quality? feature drift? hyperparameters?)
4. Document findings in drift detection log
5. Re-attempt with corrective action
