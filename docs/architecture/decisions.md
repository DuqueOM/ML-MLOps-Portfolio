# Architectural Decision Records

**17 documented decisions** covering every non-trivial choice in this portfolio. These are not explanations of what was built — they are records of what was evaluated, what was rejected, and why.

**Last Updated**: April 2026 | **Portfolio Version**: 3.6.0

> **Full ADR Library**: See [`docs/decisions/`](../decisions/README.md) for detailed per-decision records with context, alternatives considered, consequences, and verification evidence.

---

## Why ADRs Matter

Most portfolios show tools used. This one shows **decisions made** — the trade-offs, the alternatives rejected, the incidents that forced a rethink. ADRs are the engineering artifact that separates "I deployed X" from "I chose X over Y because of Z, and here's the measured result."

---

## Decision Summary

### Infrastructure & Scaling

| ADR | Decision | Choice | Key Rationale | Revisit When |
|-----|----------|--------|---------------|--------------|
| [001](../decisions/001-cpu-only-hpa.md) | HPA Metric Selection | **CPU-only HPA** | Memory-based HPA mathematically cannot scale down ML pods (fixed model RAM footprint). Proved with `ceil(replicas × usage/target)` formula | Custom metrics HPA (latency-based) needed |
| [002](../decisions/002-emptydir-model-storage.md) | Model Storage | **emptyDir + Init Container** | Models downloaded from GCS/S3 at pod startup. Decouples model versioning from Docker images. Zero persistent storage cost | Models >1GB or startup time >30s |
| [013](../decisions/013-multicloud-parity-policy.md) | Multi-Cloud Parity | **Functional parity, not identical infra** | ML workloads identical across GKE/EKS. Node counts, instance types intentionally differ (autoscaler-managed) | Regulatory requirement for identical infra |
| [014](../decisions/014-single-worker-pod-ml-inference.md) | Uvicorn Workers | **Single-worker pod pattern** | `uvicorn --workers N` under K8s is an anti-pattern: shared CPU budget → thrashing, diluted HPA signal. 1 worker + HPA = correct scaling | N/A — this is the K8s-native pattern |
| [016](../decisions/016-gcp-aws-performance-parity.md) | GCP vs AWS Performance | **Accept 2-3× GCP latency under load** | `e2-medium` shared CPU ($24/mo) vs `t3.medium` burstable ($~145/mo). Both meet <500ms SLA with 0% errors. FinOps decision, not performance bug | SLA requires <200ms p95 on GCP |

### ML Model & Inference

| ADR | Decision | Choice | Key Rationale | Revisit When |
|-----|----------|--------|---------------|--------------|
| [003](../decisions/003-stacking-classifier-bankchurn.md) | BankChurn Model | **StackingClassifier (5 models)** | AUC 0.87 vs 0.85 single model. Documented that single LightGBM might be better in production (simpler, faster). Kept for engineering depth | Latency budget <50ms |
| [005](../decisions/005-compatible-release-pinning.md) | Dependency Pinning | **Compatible release (`~=`)** | numpy 2.x silently corrupted joblib-serialized models — worst category of bug (no error, wrong predictions). `~=` blocks major/minor, receives patches | Adopt lockfile-based approach |
| [010](../decisions/010-shap-kernelexplainer-bankchurn.md) | SHAP Explainability | **KernelExplainer fallback** | TreeExplainer incompatible with StackingClassifier → all-zero SHAP in production. KernelExplainer computes in original 10-feature space for business interpretability. ~4.5s latency accepted (opt-in) | Pre-computed SHAP at training time |
| [015](../decisions/015-async-inference-threadpool.md) | Async Inference | **ThreadPoolExecutor (4 threads)** | sklearn/XGBoost/LightGBM release GIL during C extensions → real threading parallelism. Resolved 81% error rate under load. CPU halved (2000m → 1000m) | GPU inference (different concurrency model) |
| [017](../decisions/017-custom-vs-managed-ml-platforms.md) | ML Serving Platform | **Custom FastAPI + K8s primary, SageMaker complement** | Custom = full control (SHAP middleware, Prometheus metrics, multi-cloud). SageMaker = managed complement for versatility demonstration | Team >5 engineers or >10 models |

### MLOps Pipeline

| ADR | Decision | Choice | Key Rationale | Revisit When |
|-----|----------|--------|---------------|--------------|
| [004](../decisions/004-opentelemetry-graceful-fallback.md) | Observability | **OpenTelemetry with no-op fallback** | Production pods emit traces; dev/test/CI environments incur zero overhead. Activated via env var, no Docker image bloat | Vendor-specific APM required |
| [006](../decisions/006-drift-triggered-retraining.md) | Retraining Trigger | **K8s CronJob → GitHub Actions webhook** | No new infra (Airflow = 3-5 pods + DB). Reuses CI pipeline. PSI-based drift detection daily | >5 models or real-time drift detection |
| [007](../decisions/007-feature-store-decision.md) | Feature Store | **Deferred — not needed** | All features in request payload. Training-serving skew prevented structurally by serialized `model.joblib` pipeline. Full Feast architecture designed for when it IS needed | Time-window aggregations or shared features across models |
| [008](../decisions/008-argo-rollouts-canary.md) | Deployment Strategy | **Argo Rollouts canary (20→50→100%)** | Prometheus-based analysis templates with auto-rollback on error rate or latency. Replaces K8s all-or-nothing RollingUpdate for ML services | A/B testing with business metrics |

### Engineering Discipline

| ADR | Decision | Choice | Key Rationale | Revisit When |
|-----|----------|--------|---------------|--------------|
| [009](../decisions/009-simplification-when-not-to-build.md) | Simplification Audit | **Removed CarVision, fixed data leakage** | MAPE 32.9% isn't defensible for a pricing model. ChicagoTaxi had same-period aggregates (data leakage). Knowing when NOT to build is harder than building | N/A — ongoing discipline |
| [011](../decisions/011-gradio-exclusion.md) | Gradio in Production | **Local dev tool only** | Deploying to K8s = architectural inconsistency (1/3 services with UI), duplicates Swagger, wastes cluster resources | User-facing demo requirement |
| [012](../decisions/012-security-scanner-staging-policy.md) | Security Scanner Policy | **Tiered: acknowledge in staging, remediate in production** | Demonstrates security awareness without over-engineering for demo data. All findings have inline justifications | Production with real customer data |

---

## Production Incidents That Drove Decisions

These weren't planned features — they were problems discovered in production that forced architectural changes.

| Incident | Symptom | Root Cause | Resolution | ADR |
|----------|---------|------------|------------|-----|
| **81% failure rate** | BankChurn errors under 100 users | `uvicorn --workers N` shares CPU budget → thrashing | Single-worker + ThreadPoolExecutor (GIL release) | 014, 015 |
| **HPA stuck at 3 replicas** | Pods never scale down after load drops | Memory-based HPA + fixed ML model footprint | CPU-only HPA, verified 3→1 in 8 min | 001 |
| **SHAP all-zero values** | `?explain=true` returns zero contributions | (1) shap missing from prod reqs (2) TreeExplainer ≠ StackingClassifier | KernelExplainer in 10-feature space | 010 |
| **Silent wrong predictions** | numpy 2.x + joblib deserialization | dtype layout change in numpy 2.0, no error raised | Compatible release pinning (`~=`) | 005 |
| **Data leakage** | ChicagoTaxi R² suspiciously high | Same-period aggregates as features | Lag features + temporal split | 009 |
| **GCP 2-3× slower** | Higher latency under load vs AWS | `e2-medium` shared CPU vs `t3.medium` burstable | Documented as FinOps trade-off | 016 |

---

## Decision Flow

```
New Problem
    │
    ├─ Is there a managed service? → Evaluate cost/control trade-off (ADR-017)
    │
    ├─ Does it add >1 component? → Justify complexity or defer (ADR-006, 007, 009)
    │
    ├─ Can we prove it works with data? → Measure before/after (ADR-001, 014, 015)
    │
    └─ Document the decision → ADR with context, alternatives, consequences
```

---

## How to Read These ADRs

Each ADR follows a consistent structure:

1. **Context** — What problem or opportunity triggered the decision
2. **Decision** — What was chosen and why
3. **Alternatives Considered** — What was rejected and why (often the most valuable section)
4. **Consequences** — Positive, negative, and neutral outcomes
5. **Verification** — Measured evidence that the decision was correct

> **For technical reviewers**: Start with ADR-014/015 (async inference incident) and ADR-001 (HPA scaling) — they best demonstrate production debugging methodology.

---

*This page is part of the [ML-MLOps Portfolio](https://github.com/DuqueOM/ML-MLOps-Portfolio). See also: [Engineering Highlights](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/ENGINEERING_HIGHLIGHTS.md) for a quick reference of incidents and trade-offs.*
