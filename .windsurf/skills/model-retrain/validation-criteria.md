# Model Validation Criteria

## Acceptance Rules

1. **Minimum threshold**: New model MUST meet the absolute minimum metric
2. **No regression**: New model MUST NOT regress >2% from current baseline
3. **Cross-validation**: CV score must be within 1 std of mean (no overfitting signal)
4. **Inference time**: p95 latency must remain <500ms under load (p50 <200ms for BankChurn)
5. **Data integrity**: No data leakage — verify before training, especially ChicagoTaxi

## Per-Service Criteria

### BankChurn-Predictor (Classification — StackingClassifier)

| Metric | Minimum | Current Baseline (v3.6.0) | Notes |
|--------|---------|--------------------------|-------|
| AUC-ROC | ≥ 0.85 | **0.87** | Primary metric |
| F1 Score | ≥ 0.60 | **0.62** | At threshold 0.35 (30:1 cost ratio) |
| Recall | ≥ 0.70 | ~0.78 | Churner detection priority |
| CV AUC | within 1σ | 0.856 ± 0.005 | Overfitting check |

**Business context**: Missed churner costs $1,500–$3,000 LTV. False retention offer costs ~$50.
30:1 cost ratio justifies threshold 0.35 (not default 0.50).

**SHAP requirement**: KernelExplainer MUST be used — TreeExplainer is incompatible with
StackingClassifier and returns all-zero values in production (ADR-010).

---

### NLPInsight-Analyzer (NLP Sentiment — TF-IDF + LogisticRegression in production)

> ⚠️ **IMPORTANT**: Production model is **TF-IDF + LogisticRegression** (5ms, 267MB image).
> FinBERT (ProsusAI/FinBERT) is a GPU-only optional path — NOT deployed in Kubernetes.
> All validation criteria below apply to the TF-IDF+LogReg production model.

| Metric | Minimum | Current Baseline (v3.6.0) | Notes |
|--------|---------|--------------------------|-------|
| Accuracy | ≥ 0.78 | **0.806** | On 11.9K real financial tweets (noisy) |
| F1-macro | ≥ 0.70 | **0.748** | Guards minority negative class |
| F1-weighted | ≥ 0.78 | **0.810** | Overall system performance |
| Inference time (prod) | <50ms | ~5ms | TF-IDF path, in-pod |

**Dataset**: Twitter Financial News Sentiment (11,931 real tweets) — 3 classes:
58.0% neutral, 26.9% positive, 15.1% negative. NOT the curated Financial PhraseBank
(which would yield artificially high metrics ~97%). Honest benchmark.

**If using FinBERT (GPU, optional)**: ~85–88% accuracy expected per benchmarks —
do not compare against TF-IDF baseline directly.

---

### ChicagoTaxi-Demand-Pipeline (Regression — LightGBM + PySpark ETL)

| Metric | Minimum | Current Baseline (v3.6.0) | Notes |
|--------|---------|--------------------------|-------|
| R² | ≥ 0.93 | **0.96** | After data leakage fix |
| RMSE | ≤ 10.0 | **7.87** | trips/hour |
| MAE | report only | — | Complementary metric |

**Data integrity — CRITICAL (ADR-009 data leakage fix)**:
- MUST use lag features only: `trip_count_lag_1h`, `_lag_24h`, `_lag_168h`, `_rolling_24h`
- MUST use temporal train/test split (not random split)
- MUST NOT use same-period aggregates (`avg_fare`, `avg_distance_miles`, `avg_speed_mph`)
  → these caused inflated pre-fix R² of 0.905 before temporal features replaced them
- R² 0.96 is with HONEST features — do not mistake this for the pre-fix value

---

## Rejection Procedure

If new model fails validation:
1. Log failure reason, metrics, and data snapshot in MLflow run
2. Keep current production model active — DO NOT deploy failing model
3. Investigate root cause: data quality? feature drift? hyperparameter regression?
4. Document findings in drift detection log
5. Re-attempt with corrective action before next deployment window