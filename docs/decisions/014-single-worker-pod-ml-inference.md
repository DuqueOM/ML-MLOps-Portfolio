# ADR-014: Single-Worker Pod Pattern for ML Inference Under Kubernetes

- **Status**: Accepted (updated by ADR-015 — BankChurn exception removed)
- **Date**: 2026-03-18
- **Authors**: Duque Ortega Mutis
- **Related**: [ADR-015](015-async-inference-threadpool.md) (async fix), [ADR-001](001-cpu-only-hpa.md) (HPA thresholds)
- **Discovered via**: Locust load test — GCP production (50 users, 1 min)

> **TL;DR**: `uvicorn --workers N` is an anti-pattern under Kubernetes. Multiple workers share a single CPU budget, causing thrashing instead of parallelism. Switched all services to 1 worker per pod + HPA horizontal scaling. BankChurn p50 dropped from 1700ms to 200ms. ADR-015 later eliminated the last multi-worker exception via async inference.

---

## Context

During load testing against GCP production (GKE), BankChurn showed severely degraded latency under concurrent load:

| Metric | Expected (idle) | Observed (50 users) |
|--------|-----------------|---------------------|
| BankChurn p50 | ~103ms | **1700ms** |
| BankChurn p95 | ~300ms | **3200ms** |
| NLPInsight p50 | ~5ms | 170ms ✅ |
| ChicagoTaxi p50 | ~75ms | 220ms ✅ |

Root cause: all 3 services used `uvicorn --workers 2` with CPU limits insufficient for 2 concurrent inference processes.

### Root Cause: Multi-Worker Anti-Pattern Under Kubernetes

`uvicorn --workers N` creates N OS processes via `fork`. Each process:

1. Loads the full ML model independently → 2× memory footprint with no benefit
2. Competes for the **same CPU budget** enforced by `resources.limits.cpu`
3. Does not give Kubernetes per-worker CPU visibility → HPA cannot respond accurately

For CPU-bound ML inference — BankChurn uses `StackingClassifier` (5 base estimators + LR meta-learner) — multiple workers under a shared CPU limit cause **CPU thrashing**, not parallelism. Under 50 concurrent users at ~15 req/s, BankChurn needed ~1.05 CPU for inference alone. With 1 CPU limit split across 2 workers, requests queued and p50 jumped to 1700ms.

**ChicagoTaxi** was the most critical: 2 workers sharing only **500m CPU** (effectively 250m each) — below minimum viable inference budget.

Additionally, `uvicorn --workers` with `fork` can cause issues with objects loaded at startup (SHAP `KernelExplainer` background data, FinBERT tokenizer), where forked child processes inherit inconsistent state.

### Previous Configuration (All Services — GCP and AWS)

| Service | Workers | CPU Limit | HPA Threshold | scaleUp Stabilization | Issue |
|---------|---------|-----------|---------------|-----------------------|-------|
| BankChurn | 2 | 1000m | 70% | 60s | p50 1700ms under load |
| NLPInsight | 2 | 1000m | 75% | 60s | Redundant workers |
| ChicagoTaxi | 2 | **500m** | 70% | **missing** | CPU critically underprovisioned |

---

## Decision

**Remove `uvicorn --workers` from all service deployments. Use 1 process per pod and scale horizontally via Kubernetes HPA.**

Scale-out strategy: Kubernetes pod replication (horizontal), not OS process replication (vertical).

### New Configuration (GCP and AWS)

| Service | Workers | CPU Limit | HPA Threshold | scaleUp Stabilization | Reason |
|---------|---------|-----------|---------------|-----------------------|--------|
| BankChurn | **1** | **1000m** | **50%** | **30s** | Async inference via `run_in_executor` (ADR-015) |
| NLPInsight | 1 | 1000m | **60%** | **30s** | I/O-bound FinBERT — single worker sufficient |
| ChicagoTaxi | 1 | **750m** | **60%** | **30s** + added `behavior` | Lightweight LightGBM — single worker sufficient |

### BankChurn: Async Inference (ADR-015 Implemented)

Initial load testing revealed BankChurn required 2 workers due to synchronous inference blocking the event loop. **ADR-015 resolved this** by implementing `asyncio.run_in_executor(ThreadPoolExecutor)` for all prediction endpoints.

- `StackingClassifier.predict()` now runs in a 4-thread pool, freeing the uvicorn event loop
- sklearn/XGBoost/LightGBM release the GIL during C extensions → real parallelism
- Single worker handles 100 concurrent users with **0% errors** (was 81% pre-fix)
- CPU reduced from 2000m to 1000m (single process, no contention)

See **ADR-015** for full details on the async inference pattern.

### Files Changed

- `k8s/overlays/gcp/bankchurn-deployment.yaml`
- `k8s/overlays/aws/bankchurn-deployment-aws.yaml`
- `k8s/overlays/gcp/nlpinsight-deployment.yaml`
- `k8s/overlays/aws/nlpinsight-deployment-aws.yaml`
- `k8s/overlays/gcp/chicagotaxi-deployment.yaml`
- `k8s/overlays/aws/chicagotaxi-deployment-aws.yaml`
- `BankChurn-Predictor/Dockerfile`

### Deployment Strategy

**No image rebuild required.** K8s `command:` overrides Dockerfile `CMD`. Applying updated manifests via `kubectl apply` triggers a rolling update:

```bash
kubectl apply -f k8s/overlays/gcp/bankchurn-deployment.yaml -n ml-portfolio
kubectl apply -f k8s/overlays/gcp/nlpinsight-deployment.yaml -n ml-portfolio
kubectl apply -f k8s/overlays/gcp/chicagotaxi-deployment.yaml -n ml-portfolio
kubectl rollout status deployment/bankchurn-predictor -n ml-portfolio
kubectl rollout status deployment/nlpinsight-analyzer -n ml-portfolio
kubectl rollout status deployment/chicagotaxi-pipeline -n ml-portfolio
```

---

## Rationale

### Why single worker per pod is K8s-native

| Concern | `--workers N` | HPA pod scaling |
|---------|---------------|-----------------|
| CPU isolation | Shared pool, thrashing | Each pod has its own budget |
| Memory | N × model size | N × model size (same, but explicit) |
| HPA signal | Diluted (N processes → averaged) | Clean (1 process = 1 pod metric) |
| Debugging | N log streams mixed | 1 log stream per pod |
| Startup safety | `fork` after model load (risky) | Fresh process per pod (safe) |
| Graceful shutdown | All workers die together | Individual pod drain |

### Why not gunicorn + uvicorn workers?

Gunicorn pre-fork workers solve the `--workers` CPU problem (each worker gets scheduled independently), but add an extra process manager layer with no benefit in K8s. HPA already provides the same capability at the infrastructure level.

### CPU Limit Rationale

- **BankChurn 1000m**: StackingClassifier inference via thread pool. Single process, no multi-worker contention.
- **ChicagoTaxi 750m**: RandomForest regression + pandas lookup; 500m was insufficient even for 1 worker.
- **NLPInsight 1000m**: FinBERT inference is GPU-bound in theory; on CPU-only nodes, 1000m is sufficient for the observed load profile.

### HPA Threshold Rationale

Lower thresholds trigger scale-out earlier, preventing latency spikes at the cost of slightly more pods. For ML inference services where latency SLAs are strict (<500ms p95), this is the correct trade-off.

---

## Consequences

### Positive
- BankChurn p50 dropped from 1700ms → **200ms idle / 120ms (AWS) under 50-user load**
- ChicagoTaxi no longer CPU-starved; HPA now has a `behavior` block for controlled scale-out
- HPA CPU signals are accurate: 1 process = clean utilization metric
- Safer startup: no `fork` after loading StackingClassifier or FinBERT

### Negative / Trade-offs
- Slightly higher cost at rest: BankChurn CPU request increased 300m → 400m
- Under sudden large spikes, a single pod absorbs more load before HPA reacts (30s stabilization window)

### Monitoring
Verify the fix with load testing and compare p95 before/after:

```bash
# Re-run load test after rolling update completes
INGRESS_HOST=http://136.111.152.72 locust -f tests/load/locustfile.py \
  --headless -u 50 -r 10 --run-time 1m --html=reports/load_test_gcp_post_fix.html
```

**Verified** (2026-03-18): BankChurn p50 200ms idle, 0% errors under 100 users on both GCP and AWS.

---

## Alternatives Considered

### 1. Gunicorn + UvicornWorker
Each worker is a separate process scheduled by the OS, avoiding shared CPU. **Rejected**: adds process manager overhead; HPA achieves the same horizontal scaling at the K8s layer without complexity.

### 2. Keep `--workers 2` + double CPU limit to 2000m
Would solve the thrashing. **Rejected**: 2× cost per pod, defeats K8s HPA-based elasticity. Better to have 2 × 1 CPU pods than 1 × 2 CPU pod.

### 3. Async workers (default uvicorn)
FastAPI is already async; uvicorn's single-process event loop handles concurrent I/O requests. CPU-bound inference (`predict()`) still blocks the event loop — addressed by HPA scaling, not more workers.

### 4. Background thread pools for inference
Run model inference in `asyncio.run_in_executor()` with a `ThreadPoolExecutor`. **Implemented in ADR-015**: unblocks the event loop and enables full concurrency within a single pod. Removed the need for the BankChurn 2-worker exception.
