<div class="portfolio-page" markdown="1">

# ADR-005: Compatible Release Pinning (~=) for Python Dependencies

- **Status**: Accepted, amended 2026-10-23 (the numpy incident's root cause, measured — see the amendment at the end)
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

---

## Amendment, 2026-10-23 — the rule stands; two of its statements did not

**The decision stands.** Compatible-release pins keep a major — of numpy or of
anything else — from arriving without someone choosing to take it. Nothing
below weakens that.

**The pins in "Decision" stopped being true two days after this record was
accepted.** v3.5.0 (`6b47d16`, 2026-03-05, "fix Docker numpy 2.x compat")
moved the services to `numpy~=2.2.0`, `scikit-learn~=1.8.0`, `pandas~=2.3.0`
and `scipy~=1.14.0`, and redeployed all three. That was a deliberate crossing,
taken with `~=` pins on both sides, which is the process this ADR describes.
The table above is the state on 2026-03-03, not a description of the services.

**The incident's root cause was written as a fact and is not one.** "Context"
says numpy's dtype layout changed in 2.0, so joblib-deserialised models
produced different results silently. Measured with numpy as the **only**
variable:

| Artifact saved with | Loaded with | Result |
| --- | --- | --- |
| numpy 1.26.4 | numpy 2.0.2 | Loads. `predict_proba` on 1,000 rows differs by at most **2.2e-16** — one unit in the last place |
| numpy 1.26.4 | numpy 2.2.6 | Loads. Max difference **2.2e-16**. scikit-learn raises no warning |
| numpy 2.2.6 | numpy 1.26.4 | **Fails loudly**: `ValueError: <class 'numpy.random._mt19937.MT19937'> is not a known BitGenerator module` |

Model: a `Pipeline` with a `ColumnTransformer` (`StandardScaler`,
`OneHotEncoder`) and a `StackingClassifier` of RandomForest, GradientBoosting
and XGBoost under a LogisticRegression meta-learner, the shape of
BankChurn's, fitted on 4,000 synthetic rows. Every environment: Python
3.11.15, scikit-learn 1.6.1, scipy 1.14.1, joblib 1.4.2, xgboost 2.1.4,
pandas 2.2.3 — only numpy differs.

So, in the direction the incident describes, numpy alone does not move a
probability from 0.4067 to 0.3891; a difference of 0.018 is about fourteen
orders of magnitude above what it produced. The original environment is not
recoverable, so what did move it is a **hypothesis**: a `pip install
--upgrade` moves every package it can, and scikit-learn or xgboost changing in
the same upgrade can shift predictions of a re-loaded or re-fitted ensemble.
The real numpy hazard measured here is the opposite direction — an artifact
written under numpy 2 cannot be read under numpy 1 at all — and it is loud,
not silent.

What this changes:
- `~=` is still right, for the reason in the first paragraph rather than the
  one in "Context".
- A crossing of numpy's major needs an artifact compatibility check in the
  direction the deployment actually runs: the training environment must not
  be newer than the serving one.
- The same claim travels in the sibling repositories — ml-service-template's
  D-05 and the platform that consumes it. It is raised there separately; this
  record corrects only its own statement.

<details>
<summary>Reproduce</summary>

```bash
for v in 1.26.4 2.0.2 2.2.6; do
  uv venv -p 3.11 env-$v
  VIRTUAL_ENV=env-$v uv pip install "numpy==$v" scikit-learn==1.6.1 scipy==1.14.1 \
    joblib==1.4.2 xgboost==2.1.4 pandas==2.2.3
done
env-1.26.4/bin/python train.py a126.joblib p126.npy    # fit, dump, save predict_proba
env-2.2.6/bin/python  load.py  a126.joblib p126.npy    # load, compare: max |diff|
env-2.2.6/bin/python  train.py a222.joblib p222.npy
env-1.26.4/bin/python load.py  a222.joblib p222.npy    # ValueError: … BitGenerator
```

`train.py` fits the pipeline above with fixed seeds and saves the artifact
with 1,000 held-out rows and their probabilities; `load.py` loads it, predicts
on the same rows, and prints `np.array_equal` and the maximum absolute
difference.

</details>

</div>
