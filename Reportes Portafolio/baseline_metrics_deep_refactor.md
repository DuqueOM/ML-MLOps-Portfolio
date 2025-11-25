# Baseline Metrics for Deep Refactor

**Date**: 2025-11-25  
**Branch**: `refactor/deep-20251125`  
**Baseline Source**: `reports/` and `Reportes Portafolio/` from V1.0.0 tag

---

## 1. Coverage Baseline

| Project | Coverage | Tests | Status |
|---------|----------|-------|--------|
| TelecomAI-Customer-Intelligence | 87% | 54 | Tier-1 |
| CarVision-Market-Intelligence | 81% | 13 | Tier-1 |
| BankChurn-Predictor | 68% | 107 | Tier-1 |

**Threshold**: Coverage must not regress more than 2%.

---

## 2. Complexity Baseline (Radon CC)

### High Priority - Complexity C (11-20)

| File | Function | CC | Target |
|------|----------|----|----|
| `CarVision/data.py` | `infer_feature_types` | C (14) | Reduce to B |
| `CarVision/analysis.py` | `generate_executive_summary` | C (13) | Reduce to B |
| `BankChurn/prediction.py` | `ChurnPredictor.predict` | C (13) | Reduce to B |
| `BankChurn/training.py` | `ChurnTrainer.build_preprocessor` | C (11) | Reduce to B |

### Medium Priority - Complexity B (8-10)

| File | Function | CC | Target |
|------|----------|----|----|
| `BankChurn/evaluation.py` | `compute_fairness_metrics` | B (10) | Maintain or reduce |
| `CarVision/visualization.py` | `create_price_distribution_chart` | B (10) | Maintain or reduce |
| `CarVision/visualization.py` | `create_market_analysis_dashboard` | B (10) | Maintain or reduce |
| `BankChurn/models.py` | `ResampleClassifier._apply_resampling` | B (9) | Maintain |
| `BankChurn/evaluation.py` | `ModelEvaluator.evaluate` | B (9) | Maintain |

---

## 3. Dead Code Baseline (Vulture)

**Result**: No dead code detected at 80% confidence.

---

## 4. Security Baseline (Gitleaks)

**Result**: 26 findings analyzed as false positives (internal plotly/matplotlib IDs).  
**Status**: Clean - no real secrets.

---

## 5. Refactor Task Backlog

### Child Branches to Create

| # | Branch Name | Target Function | Priority |
|---|-------------|-----------------|----------|
| 1 | `refactor/deep/infer-feature-types-01` | `infer_feature_types` | High |
| 2 | `refactor/deep/generate-summary-02` | `generate_executive_summary` | High |
| 3 | `refactor/deep/predict-method-03` | `ChurnPredictor.predict` | High |
| 4 | `refactor/deep/build-preprocessor-04` | `ChurnTrainer.build_preprocessor` | High |

---

## 6. Success Criteria

- [ ] All CI jobs pass (tests, linters, security scans)
- [ ] Coverage not regressed more than 2%
- [ ] Radon complexity reduced for targeted functions
- [ ] Vulture shows no unexpected dead-code increases
- [ ] No new secrets introduced (gitleaks clean)
- [ ] All child branches removed after merge
- [ ] Final pedagogical audit files created in English

---

## 7. Post-Refactor Metrics (COMPLETED)

| Metric | Baseline | Post-Refactor | Delta |
|--------|----------|---------------|-------|
| BankChurn Coverage | 68% | 78% | **+10%** ✅ |
| CarVision Coverage | 81% | 96% | **+15%** ✅ |
| TelecomAI Coverage | 87% | 96% | **+9%** ✅ |
| High-CC Functions (C+) | 4 | 0 | **-4** ✅ |
| Dead Code Items | 0 | 0 | 0 ✅ |
| Security Issues | 0 | 0 | 0 ✅ |

### Refactored Functions Summary

| Function | Before | After | Reduction |
|----------|--------|-------|-----------|
| `infer_feature_types` | C (14) | A (4) | -10 |
| `generate_executive_summary` | C (13) | A (1) | -12 |
| `ChurnPredictor.predict` | C (13) | A (2) | -11 |
| `ChurnTrainer.build_preprocessor` | C (11) | A (3) | -8 |

### Child PRs Merged

| PR | Title | Status |
|----|-------|--------|
| #16 | refactor: reduce infer_feature_types complexity | ✅ Merged |
| #17 | refactor: reduce generate_executive_summary complexity | ✅ Merged |
| #18 | refactor: reduce ChurnPredictor.predict complexity | ✅ Merged |
| #19 | refactor: reduce build_preprocessor complexity | ✅ Merged |
