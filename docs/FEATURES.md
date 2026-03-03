# Features

## Performance (v3.3.0, March 2026)

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
| BankChurn:predict | 180ms | 360ms | 520ms | 278 | 0% |
| CarVision:predict | 110ms | 170ms | 320ms | 257 | 0% |
| NLPInsight:predict | 220ms | 540ms | 1100ms | 194 | 0% |
| **Aggregated** | **170ms** | **500ms** | **910ms** | **967** | **0%** |

**SLA**: Error rate 0% < 1% ✅ · P95 500ms ≤ 500ms ✅ · P99 910ms < 1000ms ✅

## Key Capabilities

- **SHAP Explainability** (BankChurn) — CPU-only, lazy evaluation via `?explain=true`
- **Redis Caching** — `common_utils/redis_cache.py` with TTL and graceful fallback
- **MLflow Registry Automation** — `scripts/mlflow_registry_automation.py`
- **Grafana Dashboards** — Auto-provisioned 10-panel monitoring dashboard
- **Pydantic Config** — Type-safe YAML config validation across all projects
- **Multi-Cloud** — GCP (GKE) + AWS (EKS) parity with Terraform IaC
- **Locust Load Testing** — Port-forward + Ingress IP modes

## Responsible AI (v3.3.0)

- **Fairness Audits** — All 3 projects: disparate impact (BankChurn), error ratio (CarVision), F1 parity (NLPInsight)
- **Drift Detection** — KS + PSI + Evidently in all 3 projects, vocabulary drift for NLP
- **Data Validation** — Pandera schemas for all projects (raw + inference)
- **OpenTelemetry** — Distributed tracing in all 3 FastAPI apps (graceful no-op fallback)

## Planned

- Feature Store integration (Feast)
- Drift-based auto-retraining (Evidently PSI/KS triggers)
- Canary deployments with traffic splitting

---

*Last Updated: March 2026 — v3.3.0*
