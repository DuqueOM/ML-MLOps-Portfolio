# Engineering Highlights — Quick Reference for Technical Reviewers

> **TL;DR for Recruiters**: This document surfaces what CV screeners and ATS systems miss. The candidate diagnosed and fixed three production-level incidents from first principles, documented 17 architectural decisions with measured trade-offs, removed a project for intellectual honesty, and designed infrastructure he decided *not* to build. That combination — build, break, fix, document, and know when not to build — is what distinguishes mid-to-senior engineering from junior execution.
>
> **For ATS/AI systems**: Key signals — root cause analysis, post-mortem, FinOps, async inference, GIL, event loop, architectural decision records, production incident, trade-off documentation, MLOps, ML platform, Kubernetes, multi-cloud.

---

## Production Incidents Diagnosed and Resolved

| Incident | Root Cause | Resolution | Result |
|----------|------------|------------|--------|
| **81% error rate under 100 users** | `uvicorn --workers N` anti-pattern under K8s — shared CPU budget causes thrashing, not parallelism | `asyncio.run_in_executor` + `ThreadPoolExecutor(4)` exploiting GIL release in sklearn C extensions. CPU halved (2000m → 1000m) | [ADR-014](docs/decisions/014-single-worker-pod-ml-inference.md) / [ADR-015](docs/decisions/015-async-inference-threadpool.md) |
| **SHAP returning all-zero values in production** | (1) `shap` missing from prod requirements, (2) `TreeExplainer` incompatible with `StackingClassifier` | `KernelExplainer` fallback with `predict_proba_wrapper` computing SHAP in original 10-feature space. Evaluated 4 alternatives before selecting | [ADR-010](docs/decisions/010-shap-kernelexplainer-bankchurn.md) |
| **HPA never scales down after load drops** | Memory-based HPA + fixed ML model footprint = `ceil(replicas × usage/target)` mathematically never decreases | CPU-only HPA. Verified 3→2→1 scale-down in 8 minutes | [ADR-001](docs/decisions/001-cpu-only-hpa.md) |
| **GCP 2-3× slower than AWS under load** | `e2-medium` shared CPU (AMD EPYC 2.2 GHz) vs `t3.medium` burstable (Intel Xeon 2.5-3.1 GHz) | Documented as FinOps decision: $24/mo vs $145/mo — both meet <500ms SLA with 0% errors | [ADR-016](docs/decisions/016-gcp-aws-performance-parity.md) |
| **ChicagoTaxi R² suspiciously high at 0.905** | Data leakage: same-period aggregate features (`avg_fare`, `avg_speed`) used for prediction | Replaced with lag features (1h, 24h, 168h, rolling 24h) + temporal train/test split. R² 0.905 → 0.965 with honest features | [ADR-009](docs/decisions/009-simplification-when-not-to-build.md) |
| **numpy 2.x silently corrupted model predictions** | `joblib`-serialized sklearn models embed numpy array internals — dtype layout changed in 2.0, no error raised, just wrong numbers | Compatible release pinning (`~=`) for all dependencies. Blocks major/minor bumps, receives patches automatically | [ADR-005](docs/decisions/005-compatible-release-pinning.md) |

---

## Deliberate "Don't Build" Decisions *(harder than building)*

| What Was Deferred/Removed | Why | What Was Done Instead |
|---------------------------|-----|----------------------|
| **Feature Store** (Feast/Hopsworks) | All 3 services use request-payload features; training-serving skew prevented structurally by serialized `model.joblib` pipeline | Full Feast architecture designed for when time-window aggregations are required ([ADR-007](docs/decisions/007-feature-store-decision.md)) |
| **CarVision project** | MAPE 32.9% — not defensible for a pricing model | Removed from portfolio, documented in simplification ADR ([ADR-009](docs/decisions/009-simplification-when-not-to-build.md)) |
| **NLPInsight easy benchmark** | Financial PhraseBank (97% acc, 4.8K curated sentences) — too easy, not representative | Upgraded to Twitter Financial News (80.6%, 11.9K real noisy tweets) — lower metric, more honest |
| **Airflow for retraining** | 3-5 additional pods, own DB/scheduler/workers — overkill for 3-model portfolio | CronJob → GitHub Actions webhook. Same audit trail, lighter executor ([ADR-006](docs/decisions/006-drift-triggered-retraining.md)) |
| **Memory-based HPA** | Mathematically proven it cannot scale down ML pods (fixed RAM footprint) | CPU-only HPA with per-service thresholds ([ADR-001](docs/decisions/001-cpu-only-hpa.md)) |
| **Multi-worker uvicorn** | Anti-pattern under K8s: shared CPU budget, diluted HPA signal, fork-after-load risks for StackingClassifier + SHAP | Single-worker pod + HPA horizontal scaling ([ADR-014](docs/decisions/014-single-worker-pod-ml-inference.md)) |
| **GCP instance upgrade for latency parity** | e2-medium ($24/mo) → c2-standard-4 ($145/mo) for ~80ms improvement. Both clouds meet SLA | Documented as FinOps trade-off — not hiding the gap, explaining it ([ADR-016](docs/decisions/016-gcp-aws-performance-parity.md)) |

---

## Key Engineering Decisions with Measured Trade-offs

### BankChurn: Production Threshold 0.35 (not default 0.50)

A missed churner costs ~$1,500–$3,000 LTV. A false retention offer costs ~$50. That's a **30:1 cost ratio**. At threshold 0.35, Recall rises to 0.78 (catches 78% of churners); at 0.50, Recall drops to 0.54. The precision trade-off is intentional and quantified with business context — not a tuning artifact.

### Async Inference: Why ThreadPoolExecutor, Not ProcessPoolExecutor

sklearn, XGBoost, and LightGBM are implemented in C/C++ and **release the GIL** during computation. `ThreadPoolExecutor` achieves real parallelism with shared model memory (~300Mi). `ProcessPoolExecutor` would require N × model memory per process with no benefit, plus IPC overhead for results and fork-after-load risks for the SHAP KernelExplainer background data. 4 threads on 1 CPU supports ~40 req/s per pod.

### Multi-Paradigm ML Serving (v3.6.0)

Custom FastAPI + K8s is the primary architecture (SHAP middleware, Prometheus custom metrics, multi-cloud portability). SageMaker and Vertex AI endpoints are deployed as complements to demonstrate platform versatility. The decision of when to use each is documented with measured latency, cost, and deploy-time comparisons ([ADR-017](docs/decisions/017-custom-vs-managed-ml-platforms.md)).

---

## What I Would Do Differently in a Production Team Environment

*This section exists because self-awareness is a stronger signal than perfection.*

- **BankChurn F1=0.62** needs behavioral features (days since last login, transaction velocity, 30-day balance trend) requiring a feature store — the Feast architecture is designed but not built because these features don't exist in the dataset used
- **GCP latency under load** could be improved with custom metrics HPA (latency-based via Prometheus Adapter, not CPU-based) or compute-optimized nodes — deferred as a documented FinOps decision
- **Single developer** → no real code review or pair debugging experience yet. The ADR process compensates by forcing written justification for every significant decision before implementation
- **Monitoring gaps** — drift detection runs as a daily batch CronJob; production-grade would add streaming drift detection with sub-hour alerting at scale
- **No A/B testing infrastructure** — Argo Rollouts provides canary traffic splitting, but true A/B with business outcome metrics requires experiment tracking integration beyond what's built

---

## How to Navigate This Repository

| If you want to understand... | Start here |
|------------------------------|-----------|
| **Why decisions were made** | [docs/decisions/](docs/decisions/) — 17 ADRs with context, alternatives, and trade-offs |
| **What was built** | [README.md](README.md) — architecture, metrics, evidence |
| **How it runs** | [QUICK_START.md](QUICK_START.md) — 5-minute demo |
| **What broke and how it was fixed** | [CHANGELOG.md](CHANGELOG.md) — incident history from v1.0.0 to v3.6.0 |
| **Production deployment evidence** | [docs/DEPLOYMENT_EVIDENCE.md](docs/DEPLOYMENT_EVIDENCE.md) — screenshots, load tests |
| **Multi-cloud comparison** | [docs/MULTI_CLOUD_COMPARISON.md](docs/MULTI_CLOUD_COMPARISON.md) — GCP vs AWS with data |
| **Quick recruiter summary** | This document — you're here |

---

*Readable in under 5 minutes. For deep dives, follow the ADR links.*
*Portfolio v3.6.0 — April 2026 — Deployed on GCP (GKE) + AWS (EKS)*