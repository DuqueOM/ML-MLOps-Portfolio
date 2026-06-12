<div class="portfolio-page" markdown="1">

# ADR-005: Compatible Release Pinning (~=) for Python Dependencies

- **Status**: Accepted
- **Date**: 2026-03-03
- **Authors**: Duque Ortega Mutis

> **TL;DR**: Pin all Python dependencies using the `~=` (compatible release) operator after `numpy 2.x` silently broke joblib-serialized models at runtime. This prevents major-version breakage while still receiving patch-level security fixes automatically.

---

## Context

### The Incident

After a routine `pip install --upgrade`, `numpy` upgraded from 1.26.4 to 2.0.0. The application started normally — no import errors, no exceptions. However, model predictions changed silently:

```
# numpy 1.26.4 — correct
predict([customer_data]) → churn_probability: 0.4067

# numpy 2.0.0 — wrong (different floating-point behavior)
predict([customer_data]) → churn_probability: 0.3891
```

**Root cause**: `joblib`-serialized sklearn models embed numpy array internals. When numpy's C-level dtype layout changed in 2.0, deserialized arrays produced different numerical results — no error, no warning, just wrong predictions.

This is a **silent correctness failure** — the worst category of production bug because monitoring doesn't catch it.

### The Broader Problem

ML projects have deep, brittle dependency graphs:

```
StackingClassifier
  ├─ scikit-learn ~= 1.5 → requires numpy >= 1.22
  ├─ xgboost ~= 2.1 → requires numpy >= 1.22
  ├─ lightgbm ~= 4.5 → requires numpy >= 1.22
  ├─ shap ~= 0.46 → requires numpy >= 1.20
  └─ pandas ~= 2.2 → requires numpy >= 1.23
```

A single numpy major bump can break serialized models, SHAP background data, and pandas internals simultaneously.

---

## Decision

**Pin all dependencies using the `~=` (compatible release) operator** in all `requirements*.txt` files.

```
# requirements-prod.txt
numpy~=1.26.4        # allows 1.26.x, blocks 2.x
scikit-learn~=1.5.2   # allows 1.5.x, blocks 1.6+
xgboost~=2.1.3        # allows 2.1.x, blocks 2.2+
lightgbm~=4.5.0       # allows 4.5.x, blocks 4.6+
pandas~=2.2.3         # allows 2.2.x, blocks 2.3+
shap~=0.46.0          # allows 0.46.x, blocks 0.47+
```

### How `~=` Works (PEP 440)

```
~=1.26.4 ≡ >=1.26.4, <1.27.0   (patch updates only)
~=1.5.2  ≡ >=1.5.2, <1.6.0     (patch updates only)
~=2.1.3  ≡ >=2.1.3, <2.2.0     (patch updates only)
```

- Receives security patches and bug fixes automatically
- Blocks minor/major version bumps that may break serialized models

---

## Alternatives Considered

| Strategy | Reproducibility | Security Patches | Maintenance | Verdict |
|----------|----------------|-----------------|-------------|---------|
| No pinning (`numpy`) | None | Auto | None | Rejected — caused the numpy 2.x incident |
| Exact pinning (`numpy==1.26.4`) | Perfect | Manual | High (every CVE requires manual bump) | Rejected — too rigid for a portfolio; larger teams use lockfiles instead |
| **Compatible release (`numpy~=1.26.4`)**  | High | Auto (patches) | Low | **Selected** — balances safety with maintainability |
| Lockfile (`pip-compile`, `poetry.lock`) | Perfect | Manual/Dependabot | Medium | Deferred — best option at scale; overkill for 3 services |

### Why Not Exact Pinning?

Exact pinning (`==`) requires manual intervention for every security patch. For a portfolio with 3 services × ~30 dependencies each, this creates a maintenance burden disproportionate to the risk. Compatible release pins achieve 95% of the safety with 10% of the maintenance.

---

## Scope

Applied consistently across all services:

| File | Purpose |
|------|---------|
| `BankChurn-Predictor/requirements-prod.txt` | Production dependencies |
| `BankChurn-Predictor/requirements-dev.txt` | Development + testing |
| `NLPInsight-Analyzer/requirements-prod.txt` | Production dependencies |
| `NLPInsight-Analyzer/requirements-dev.txt` | Development + testing |
| `ChicagoTaxi-Pipeline/requirements-prod.txt` | Production dependencies |
| `ChicagoTaxi-Pipeline/requirements-dev.txt` | Development + testing |

---

## Consequences

- **Positive**: Prevents silent model corruption from major dependency changes
- **Positive**: Reproducible builds across environments (dev, CI, GKE, EKS)
- **Positive**: Automatic patch-level security updates without manual intervention
- **Positive**: Standard PEP 440 operator — works with pip, pip-tools, Poetry, and all Python tooling
- **Negative**: Minor/major version bumps require manual review and testing
- **Negative**: Does not catch all breaking changes (rare bugs in patch releases)

## Revisit When

- Adopting `pip-compile` / `poetry.lock` for exact reproducibility with Dependabot-managed updates
- Moving to containerized model serving (e.g., Triton, BentoML) where model + runtime are versioned together
- Organization mandates a specific dependency management tool

---

## References

- [PEP 440 — Compatible Release Clause](https://peps.python.org/pep-0440/#compatible-release)
- [NumPy 2.0 Migration Guide](https://numpy.org/doc/stable/numpy_2_0_migration_guide.html)
- [sklearn Model Persistence](https://scikit-learn.org/stable/model_persistence.html)

</div>
