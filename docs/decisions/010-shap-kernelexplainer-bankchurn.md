# ADR-010: SHAP KernelExplainer for BankChurn StackingClassifier

- **Status**: Accepted
- **Date**: 2026-03-10
- **Authors**: Duque Ortega Mutis
- **Related**: [ADR-003](003-stacking-classifier-bankchurn.md) (model choice), [ADR-015](015-async-inference-threadpool.md) (async inference)

> **TL;DR**: `TreeExplainer` does not support `StackingClassifier`. Implemented `KernelExplainer` as a model-agnostic fallback that computes SHAP values in the original 10-feature space (interpretable by business stakeholders). The ~4.5s latency is acceptable because explanations are opt-in (`?explain=true`) and only triggered for high-risk predictions.

---

## Context

BankChurn v3.0.0 uses a `StackingClassifier` (RF + GradientBoosting + XGBoost + LightGBM → LogisticRegression meta-learner) inside a sklearn `Pipeline` with three steps:

```
Pipeline: [ChurnFeatureEngineer] → [ColumnTransformer] → [StackingClassifier]
```

The `/predict?explain=true` endpoint is designed to return per-feature SHAP values for individual predictions, enabling business stakeholders to understand *why* a customer is flagged as high-risk.

**Problem**: The initial implementation returned all-zero feature contributions in production because:
1. `shap` was missing from `requirements-prod.txt` (only in dev requirements)
2. When SHAP was added, `shap.TreeExplainer` raised: *"Model type not yet supported: `StackingClassifier`"*

`TreeExplainer` works with single tree-based models (RandomForest, XGBoost, LightGBM, GradientBoosting) but **does not support ensemble wrappers** like `StackingClassifier` because it cannot trace prediction paths through the meta-learner combination logic.

---

## Decision

Use **`shap.KernelExplainer`** as the SHAP backend for BankChurn, with a `TreeExplainer` attempt first (for forward-compatibility if the model changes to a single tree model).

**Implementation**:
```python
# _initialize_explainer() — simplified
try:
    inner = self._unwrap_classifier(classifier)  # extract estimator from pipeline
    self.explainer = shap.TreeExplainer(inner)   # fast, but fails for StackingClassifier
    self._uses_kernel_explainer = False
    return
except Exception:
    pass  # fall through to KernelExplainer

# KernelExplainer: model-agnostic, works with any black-box
def predict_proba_wrapper(X_array):
    X_df = pd.DataFrame(X_array, columns=self.feature_names)  # restore column names
    return self.model.predict_proba(X_df)[:, 1]               # full pipeline (features + preprocessor + classifier)

self.explainer = shap.KernelExplainer(predict_proba_wrapper, X_background.values[:50])
self._uses_kernel_explainer = True
```

**Key design choices**:
- The `predict_proba_wrapper` receives **raw features** (10 columns) and calls `self.model.predict_proba`, which internally applies the full pipeline (ChurnFeatureEngineer → ColumnTransformer → StackingClassifier)
- SHAP values are therefore computed **in the original feature space** (10 interpretable business features), not in the expanded transformed space (38+ encoded columns)
- Background data: 50 samples from `Churn.csv` raw features, representative of the training distribution

---

## Alternatives Considered

### 1. TreeExplainer on individual base learners
Apply SHAP separately to each of RF, GB, XGB, LGB, then aggregate.

- **Rejected**: Produces 4 separate SHAP explanations that are not directly comparable. The meta-learner (LogisticRegression) applies learned weights to base learner outputs — not captured by individual explanations. Would require a custom aggregation strategy with no standard interpretation.

### 2. LinearExplainer on the meta-learner
Explain only the LogisticRegression meta-learner using base learner out-of-fold predictions as features.

- **Rejected**: Explains the combination weights between models (e.g., "XGBoost contributed +0.3"), not the business features (e.g., "Age contributed +0.05"). Useless for non-technical stakeholders who need feature-level attribution.

### 3. Remove SHAP from production
Remove explainability entirely or only provide it in development.

- **Rejected**: Explainability is a core feature for portfolio differentiation and represents responsible AI practice. The `?explain=true` opt-in pattern already ensures zero overhead for standard predictions.

### 4. Replace StackingClassifier with a single tree model
Downgrade from StackingClassifier (AUC 0.87) to a single LightGBM/XGBoost (AUC 0.84–0.86) to enable TreeExplainer.

- **Rejected**: Losing 1–3% AUC for the sole purpose of SHAP compatibility is not a sound trade-off. KernelExplainer is the correct solution.

---

## Trade-offs

| Dimension | TreeExplainer | KernelExplainer (chosen) |
|-----------|--------------|--------------------------|
| **Compatibility** | Tree models only | Any black-box model |
| **Latency** | ~5–50ms per request | **~4.5s per request** (measured in GKE) |
| **Accuracy** | Exact Shapley values | Approximate (sampling-based) |
| **Background samples** | Not required | 50 samples (used as baseline distribution) |
| **Interpretability space** | Transformed features (38 cols) | **Raw features (10 cols)** ✅ |

**The 4.5s latency for `?explain=true` is an accepted trade-off** because:
- It is an **opt-in endpoint** — standard `/predict` requests run at 200ms p50 (GCP) / 110ms p50 (AWS)
- In production, SHAP explanations would be triggered **only for high-risk predictions** (`risk_level=HIGH`), typically representing ~20% of requests
- At portfolio scale (demo load test: 6.58 RPS), this does not create backpressure

---

## Production Patterns (How This Would Scale)

At larger scale, this pattern would be extended as follows:

| Scale | Pattern |
|-------|---------|
| **<100 RPS** | Synchronous on-demand (current implementation) |
| **100–1000 RPS** | Async queue: predict sync, explain via Celery/Redis async, webhook callback |
| **>1000 RPS** | Dedicated explainability microservice with model replica + explanation cache (Redis TTL 1h for repeated inputs) |
| **Batch** | Nightly SHAP job on high-risk segment, stored in feature store |

The current synchronous implementation is appropriate for a portfolio demo and for low-traffic enterprise use cases (e.g., a retention analyst requesting explanations for flagged customers).

---

## Verification

**SHAP initialization** (pod startup log):
```
INFO: Loaded 100 background samples from /app/data/raw/Churn.csv (10 features)
INFO: Feature engineering: 10 → 25 features (+15)
INFO: Initialized KernelExplainer
INFO: Model loaded successfully
```

**Production output** (measured 2026-03-10):
```json
{
  "churn_probability": 0.4067,
  "feature_contributions": {
    "NumOfProducts":  0.1059,
    "Age":            0.0500,
    "Balance":        0.0267,
    "Gender":         0.0289,
    "CreditScore":    0.0241,
    "Tenure":         0.0168,
    "IsActiveMember": -0.0510,
    "Geography":      -0.0130,
    "EstimatedSalary": -0.0137,
    "HasCrCard":      -0.0167
  }
}
```

**Interpretation**: Single product (`NumOfProducts=1`, +0.106) and age 42 (+0.05) are the strongest churn risk factors for this customer, while active membership (-0.051) is the strongest protective factor.

---

## Consequences

- **Positive**: Real, non-zero feature contributions for all predictions with `?explain=true`
- **Positive**: SHAP values in original feature space — directly interpretable by business stakeholders
- **Positive**: Demonstrates responsible AI practice (explainable ML) in portfolio
- **Negative**: 4.5s latency for `?explain=true` (synchronous KernelExplainer)
- **Negative**: `shap~=0.46.0` adds ~150MB to Docker image (342MB → ~490MB)
- **Negative**: +30s pod startup time (KernelExplainer initialization with 100 background samples)

---

## Revisit When

- Model changes to a single tree ensemble (XGBoost/LightGBM) → switch to TreeExplainer (<50ms)
- Throughput requirement for explanations exceeds 10 RPS → move to async architecture
- `shap` 0.47+ adds native StackingClassifier support → re-evaluate TreeExplainer
