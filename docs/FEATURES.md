# Features

## Performance (v3.5.0, March 2026)

| Feature | Impact |
|---------|--------|
| **Inference optimization** | 0% errors, in-pod p95: 111ms (BankChurn), 15ms (NLPInsight), 460ms (ChicagoTaxi) |
| **Uvicorn 2 workers** | Doubled throughput under concurrency |
| **Joblib compression** | 77% smaller model files |
| **Pandas dtype optimization** | 93% memory reduction |
| **NumPy vectorization** | 1.6× speedup |
| **sklearn parallelization** | `n_jobs=-1` across all transformers |

## Load Test Results (10 users, 90s, Locust, via LoadBalancer Ingress)

| Service | GCP p50 | GCP p95 | AWS p50 | AWS p95 | Errors |
|---------|---------|---------|---------|---------|--------|
| BankChurn `/predict` | 110ms | 240ms | 110ms | 230ms | **0%** |
| NLPInsight `/predict` | 99ms | 220ms | 98ms | 200ms | **0%** |
| ChicagoTaxi `/demand` | 75ms | 180ms | 240ms | 560ms | **0%** |

**SLA**: Error rate 0% < 1% ✅ · BankChurn/NLPInsight P95 < 500ms ✅ · Multi-cloud parity confirmed ✅

## In-Pod Latency (measured inside container, zero network overhead)

| Service | Endpoint | P50 | P95 |
|---------|----------|-----|-----|
| BankChurn | `/predict` | 103ms | 111ms |
| BankChurn | `/predict?explain=true` | 196ms | — |
| NLPInsight | `/predict` | 5ms | 15ms |
| ChicagoTaxi | `/demand` | 75ms | 460ms |
| ChicagoTaxi | `/areas` | 187ms | — |

## Key Capabilities

- **SHAP Explainability** (BankChurn) — CPU-only, lazy evaluation via `?explain=true`
- **Redis Caching** — `common_utils/redis_cache.py` with TTL and graceful fallback
- **MLflow Registry Automation** — `scripts/mlflow_registry_automation.py`
- **Grafana Dashboards** — 2 auto-provisioned dashboards (25 panels total: ML Performance + ML Portfolio Production)
- **Pydantic Config** — Type-safe YAML config validation across all projects
- **Multi-Cloud** — GCP (GKE) + AWS (EKS) parity with Terraform IaC
- **Locust Load Testing** — Port-forward + Ingress IP modes

## Responsible AI (v3.5.0)

- **Fairness Audits** — BankChurn (disparate impact), NLPInsight (F1 parity)
- **Drift Detection** — KS + PSI + Evidently, vocabulary drift for NLP
- **Data Validation** — Pandera schemas for all projects (raw + inference)
- **OpenTelemetry** — Distributed tracing in all 3 FastAPI apps (graceful no-op fallback)

## Planned

- Feature Store integration — deferred; see [ADR-007](decisions/007-feature-store-decision.md) for rationale and design
- Canary deployments with traffic splitting (Argo Rollouts manifests exist; not yet exercised)

## Recently Addressed

- **Drift-triggered retraining** — K8s CronJob + GitHub Actions dispatch; see [ADR-006](decisions/006-drift-triggered-retraining.md)
- **Metric rationale** — all 3 model cards now explain *why* each metric was chosen and what was sacrificed

## Visual Evidence

| Demo GIF | HPA Autoscaling | Fairness Audit |
|:---:|:---:|:---:|
| ![Demo](media/gifs/01-demo-prediccion.gif) | ![HPA](media/gifs/02-hpa-autoscaling.gif) | ![Fairness](media/gifs/03-fairness-audit.gif) |

---

*Last Updated: March 2026 — v3.5.3*
