# Features

## Performance (v3.4.0, March 2026)

| Feature | Impact |
|---------|--------|
| **Inference optimization** | 0% errors, p95 <250ms, lazy SHAP |
| **Uvicorn 2 workers** | Doubled throughput under concurrency |
| **Joblib compression** | 77% smaller model files |
| **Pandas dtype optimization** | 93% memory reduction |
| **NumPy vectorization** | 1.6× speedup |
| **sklearn parallelization** | `n_jobs=-1` across all transformers |

## Load Test Results (10 users, 2 min, Locust, GKE via port-forward)

| Service | p50 | p95 | p99 | Requests | Errors |
|---------|-----|-----|-----|----------|--------|
| BankChurn:predict | 170ms | 350ms | 450ms | 260 | 0% |
| CarVision:predict | 91ms | 130ms | 300ms | 265 | 0% |
| NLPInsight:predict | 180ms | 450ms | 2400ms | 184 | 0% |
| **Aggregated** | **160ms** | **480ms** | **820ms** | **973** | **0%** |

**SLA**: Error rate 0% < 1% ✅ · P95 480ms < 500ms ✅ · P99 820ms < 1000ms ✅

## Key Capabilities

- **SHAP Explainability** (BankChurn) — CPU-only, lazy evaluation via `?explain=true`
- **Redis Caching** — `common_utils/redis_cache.py` with TTL and graceful fallback
- **MLflow Registry Automation** — `scripts/mlflow_registry_automation.py`
- **Grafana Dashboards** — 2 auto-provisioned dashboards (25 panels total: ML Performance + ML Portfolio Production)
- **Pydantic Config** — Type-safe YAML config validation across all projects
- **Multi-Cloud** — GCP (GKE) + AWS (EKS) parity with Terraform IaC
- **Locust Load Testing** — Port-forward + Ingress IP modes

## Responsible AI (v3.4.0)

- **Fairness Audits** — BankChurn (disparate impact), CarVision (error ratio), NLPInsight (F1 parity)
- **Drift Detection** — KS + PSI + Evidently, vocabulary drift for NLP
- **Data Validation** — Pandera schemas for all projects (raw + inference)
- **OpenTelemetry** — Distributed tracing in all 3 FastAPI apps (graceful no-op fallback)

## Planned

- Feature Store integration — deferred; see [ADR-007](decisions/007-feature-store-decision.md) for rationale and design
- Canary deployments with traffic splitting (Argo Rollouts manifests exist; not yet exercised)

## Recently Addressed

- **Drift-triggered retraining** — K8s CronJob + GitHub Actions dispatch; see [ADR-006](decisions/006-drift-triggered-retraining.md)
- **Metric rationale** — all 3 model cards now explain *why* each metric was chosen and what was sacrificed

---

*Last Updated: March 2026 — v3.4.0*
