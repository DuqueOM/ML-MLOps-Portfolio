---
trigger: always_on
description: Core MLOps conventions — concise reference, full detail in AGENTS.md
---

# MLOps Production Template — Core Rules

## Stack (non-negotiable)
- Python 3.11+, scikit-learn/XGBoost/LightGBM, FastAPI, Kubernetes, Terraform
- Clouds: GCP (primary) + AWS (secondary)
- Tracking: MLflow | Monitoring: Prometheus + Grafana | Validation: Pandera

## 6 Invariants (NEVER violate)
1. `uvicorn --workers 1` only — HPA provides horizontal scale
2. HPA uses CPU only — never memory for ML pods
3. CPU-bound inference always via `run_in_executor(ThreadPoolExecutor)`
4. SHAP always in original feature space via predict_proba_wrapper; explainer cached at startup (D-24)
5. No model artifacts in Docker images — init container pattern only
6. Model warm-up runs in lifespan BEFORE `_warmed_up=True`; `/ready` gates traffic (D-23)

## Dynamic Behavior Protocol (ADR-010)

Before executing a CONSULT or AUTO operation, load the risk context
(`common_utils/risk_context.py`) and apply the escalation table:

| base_mode | signals | final_mode |
|-----------|---------|-----------|
| AUTO      | 0       | AUTO      |
| AUTO      | ≥ 1     | **CONSULT** |
| CONSULT   | 0       | CONSULT   |
| CONSULT   | ≥ 1     | **STOP**  |
| STOP      | any     | STOP (sticky) |

Signals (each counts as 1):
- `incident_active` — P1/P2 alert firing
- `drift_severe` — any PSI > 2× per-feature alert threshold
- `error_budget_exhausted` — 30-day SLO burn >= 100%
- `off_hours` — weekends or 18:00–08:00 UTC (override via `MLOPS_ON_HOURS_UTC`)
- `recent_rollback` — rollback audit entry in the last 6 h

When mcp-prometheus is unavailable, the agent falls back to the static
AGENTS.md mapping and MUST emit `risk_signals: UNAVAILABLE` in its
audit entry. Dynamic scoring can ONLY escalate — never relax.

## Dependency Pinning
Always `~=` for ML packages. Never `==` (conflicts) or bare `>=` (breaks).

## Quality Standards
- Coverage >= 90% lines, >= 80% branches
- Type hints on all public functions, Google-style docstrings
- black (120), isort (black profile), flake8, mypy
- ADR for every non-trivial decision in `docs/decisions/`

## Engineering Calibration
Match complexity to scale: CronJob not Airflow, Pandera not GE, PSI not feature store.

## When to Load Skills
- Creating a new service? → `new-service` (uses `templates/scripts/new-service.sh`)
- Debugging inference? → `debug-ml-inference`
- Drift alert fired? → `drift-detection` → `model-retrain`
- Deploying? → `deploy-gke` or `deploy-aws`
- Monthly cost review? → `cost-audit`

## Full Details
- Anti-pattern table D-01 to D-12: see `AGENTS.md`
- All invariants with reasoning: see `AGENTS.md`
- Session initialization protocol: see `AGENTS.md`
