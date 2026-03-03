# Features

## Performance (v3.0.0, March 2026)

| Feature | Impact |
|---------|--------|
| **Inference optimization** | 0% errors, p95 <250ms, lazy SHAP |
| **Uvicorn 2 workers** | Doubled throughput under concurrency |
| **Joblib compression** | 77% smaller model files |
| **Pandas dtype optimization** | 93% memory reduction |
| **NumPy vectorization** | 1.6× speedup |
| **sklearn parallelization** | `n_jobs=-1` across all transformers |

## Load Test Results (10 users, Locust, GKE)

| Service | Avg | p95 | p99 | Errors |
|---------|-----|-----|-----|--------|
| BankChurn | 130ms | 240ms | 330ms | 0% |
| CarVision | 103ms | 150ms | 290ms | 0% |
| NLPInsight | 87ms | 220ms | 460ms | 0% |

**SLA**: Error rate 0% < 1% ✅ · p95 < 500ms ✅

## Key Capabilities

- **SHAP Explainability** (BankChurn) — CPU-only, lazy evaluation via `?explain=true`
- **Redis Caching** — `common_utils/redis_cache.py` with TTL and graceful fallback
- **MLflow Registry Automation** — `scripts/mlflow_registry_automation.py`
- **Grafana Dashboards** — Auto-provisioned 10-panel monitoring dashboard
- **Pydantic Config** — Type-safe YAML config validation across all projects
- **Multi-Cloud** — GCP (GKE) + AWS (EKS) parity with Terraform IaC
- **Locust Load Testing** — Port-forward + Ingress IP modes

## Responsible AI (v3.2.0)

- **Fairness Audits** — All 3 projects: disparate impact (BankChurn), error ratio (CarVision), F1 parity (NLPInsight)
- **Drift Detection** — KS + PSI + Evidently in all 3 projects, vocabulary drift for NLP
- **Data Validation** — Pandera schemas for all projects (raw + inference)
- **OpenTelemetry** — Distributed tracing in all 3 FastAPI apps (graceful no-op fallback)

## Planned

- Feature Store integration (Feast)
- Drift-based auto-retraining (Evidently PSI/KS triggers)
- Canary deployments with traffic splitting

---

*Last Updated: March 2026 — v3.2.0*
