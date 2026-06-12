<div class="portfolio-page" markdown="1">

# ADR-003: StackingClassifier for BankChurn Churn Prediction

- **Status**: Accepted
- **Date**: 2026-02-28
- **Authors**: Duque Ortega Mutis
- **Related**: [ADR-009](009-simplification-when-not-to-build.md) (complexity justification), [ADR-010](010-shap-kernelexplainer-bankchurn.md) (SHAP compatibility)

> **TL;DR**: Chose a 4-model StackingClassifier (AUC 0.87) over a single LightGBM (AUC 0.86) because the ensemble demonstrates advanced ML methodology while achieving measurably better generalization on imbalanced churn data. The 1% AUC gap is modest, but CV variance of ±0.006 confirms the gain is real, not noise.

---

## Context

BankChurn predicts binary customer churn on a 10K-row dataset with 20% positive class imbalance. The model serves as a risk-scoring tool for retention analysts — AUC (ranking quality) matters more than raw accuracy.

### Model Comparison (5-fold CV)

| Model | AUC | F1 (churn) | CV Std | Training Time | Artifact Size |
|-------|-----|-----------|--------|---------------|---------------|
| LogisticRegression | 0.78 | 0.48 | ±0.008 | <1 min | <1 MB |
| RandomForest | 0.84 | 0.58 | ±0.010 | 3 min | 2 MB |
| XGBoost | 0.85 | 0.60 | ±0.007 | 4 min | 1.5 MB |
| LightGBM | 0.86 | 0.61 | ±0.006 | 2 min | 1 MB |
| VotingClassifier (soft) | 0.86 | 0.61 | ±0.007 | 8 min | 3 MB |
| **StackingClassifier** ✅ | **0.87** | **0.62** | **±0.006** | 20 min | 4.1 MB |
| PyTorch MLP | 0.83 | 0.55 | ±0.015 | 15 min | 8 MB |

---

## Decision

**Use StackingClassifier** with 4 diverse base learners and a LogisticRegression meta-learner:

```
Pipeline: [ChurnFeatureEngineer] → [ColumnTransformer] → [StackingClassifier]
                                                              ├─ RandomForest (bagging)
                                                              ├─ GradientBoosting (sequential boosting)
                                                              ├─ XGBoost (regularized boosting)
                                                              ├─ LightGBM (leaf-wise boosting)
                                                              └─ LogisticRegression (meta-learner, 5-fold CV)
```

### Why Diverse Base Learners?

Each base learner captures different signal patterns:
- **RandomForest**: Robust to outliers via bagging; captures non-linear interactions
- **GradientBoosting**: Sequential error correction; strong on residual patterns
- **XGBoost**: L1/L2 regularization prevents overfitting on small datasets
- **LightGBM**: Leaf-wise growth finds deep interactions; fastest individual model

The meta-learner (LogReg) learns **optimal combination weights** from 5-fold out-of-fold predictions — it cannot overfit to training data because it only sees held-out predictions.

---

## Alternatives Considered

| Option | AUC | Verdict | Rationale |
|--------|-----|---------|-----------|
| Single LightGBM | 0.86 | Viable | Simpler, faster; 1% AUC gap is small but real on imbalanced data |
| VotingClassifier | 0.86 | Rejected | No learned combination weights — just averaging; same complexity, less benefit |
| PyTorch MLP | 0.83 | Rejected | Worse performance on tabular data; adds PyTorch dependency for no gain |
| **StackingClassifier** | **0.87** | **Selected** ✅ | Best AUC, lowest CV variance, demonstrates ensemble methodology |

### Honest Trade-off (see ADR-009)

The 0.01 AUC improvement over single LightGBM is modest. In a production system with strict latency/cost constraints, the simpler model would likely win. This portfolio keeps StackingClassifier to **demonstrate ensemble methodology** — the engineering challenge of serving a complex model (async inference, SHAP compatibility) is part of the learning objective.

---

## Consequences

- **Positive**: Best AUC (0.87) with robust generalization (CV ±0.006)
- **Positive**: Demonstrates advanced ensemble methods and sklearn Pipeline integration
- **Positive**: Meta-learner weights are interpretable — shows which base learner contributes most
- **Negative**: 4× training time vs single model (~20 min vs ~5 min)
- **Negative**: 4× model artifact size (4.1 MB vs ~1 MB)
- **Negative**: Requires KernelExplainer for SHAP (TreeExplainer incompatible) — adds ~4.5s per explanation ([ADR-010](010-shap-kernelexplainer-bankchurn.md))
- **Negative**: CPU-bound inference requires async thread pool to avoid event loop blocking ([ADR-015](015-async-inference-threadpool.md))

## Revisit When

- Training data grows >100K rows — consider online learning or incremental models
- Inference latency SLA drops below 50ms — single LightGBM with TreeExplainer would be faster
- SHAP adds native StackingClassifier support — would remove the KernelExplainer overhead

---

## References

- [ADR-009: Simplification — When Not to Build](009-simplification-when-not-to-build.md) — justifies keeping StackingClassifier
- [ADR-010: SHAP KernelExplainer](010-shap-kernelexplainer-bankchurn.md) — SHAP compatibility consequence
- [ADR-015: Async Inference](015-async-inference-threadpool.md) — inference performance consequence
- [Wolpert, D.H. (1992). Stacked Generalization. Neural Networks, 5(2), 241-259](https://doi.org/10.1016/S0893-6080(05)80023-1)

</div>
