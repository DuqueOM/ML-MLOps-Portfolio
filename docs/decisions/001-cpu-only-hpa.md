<div class="portfolio-page" markdown="1">

# ADR-001: CPU-Only HPA for ML Inference Services

- **Status**: Accepted
- **Date**: 2026-02-20
- **Authors**: Duque Ortega Mutis
- **Updated**: 2026-03-18 (thresholds refined by ADR-014)

> **TL;DR**: Removed memory from HPA metrics because ML models hold a fixed RAM footprint that never decreases — making memory-based autoscaling mathematically unable to scale down. CPU-only HPA reduced idle cost by scaling BankChurn 3 → 1 pods in 8 minutes.

---

## Context

All three ML services (BankChurn, NLPInsight, ChicagoTaxi) load models into RAM at startup and hold them for the pod's lifetime. Memory usage is effectively **constant** regardless of traffic:

| Service | Measured Idle Memory | Under Load Memory | Delta |
|---------|---------------------|-------------------|-------|
| BankChurn (StackingClassifier + SHAP) | 332 Mi | ~335 Mi | < 1% |
| NLPInsight (TF-IDF + LogReg) | 140 Mi | ~143 Mi | < 2% |
| ChicagoTaxi (RandomForest + cache) | 149 Mi | ~152 Mi | < 2% |

### Why Memory-Based HPA Fails for ML Inference

The HPA formula is `desiredReplicas = ceil(currentReplicas × currentUtilization / targetUtilization)`. With constant memory:

```
3 replicas × 332Mi each, limit 512Mi, target 80%
→ utilization = 332/512 = 64.8%
→ desired = ceil(3 × 64.8/80) = ceil(2.43) = 3  ← never decreases
```

In a multi-metric HPA, Kubernetes takes the **maximum** recommendation across metrics. Even when CPU says "scale to 1," memory says "keep 3" — so 3 pods run indefinitely.

**Observed**: After a load spike scaled BankChurn to 3 replicas, it never scaled down. Pods sat idle for hours.

---

## Decision

**Remove memory from all HPAs. Scale exclusively on CPU utilization.**

| Service | CPU Target | Min / Max Replicas | scaleUp Stabilization |
|---------|-----------|-------------------|----------------------|
| BankChurn | 50% | 1 / 5 | 30s |
| NLPInsight | 60% | 1 / 3 | 30s |
| ChicagoTaxi | 60% | 1 / 3 | 30s |

> Thresholds refined from 70-75% to 50-60% by [ADR-014](014-single-worker-pod-ml-inference.md) for faster scale-out under the single-worker pattern.

---

## Alternatives Considered

| Option | Verdict | Rationale |
|--------|---------|-----------|
| CPU + Memory HPA (original) | **Rejected** | Never scales down for fixed-footprint models |
| **CPU-only HPA** | **Selected** ✅ | Accurate signal for inference traffic |
| Custom metrics (p95 latency via Prometheus Adapter) | Deferred | Best signal, but requires Prometheus Adapter CRD; planned for future |
| KEDA (event-driven) | Deferred | Scale-to-zero capability; overkill for HTTP services at current scale |

---

## Verification

After removing the memory metric:
- BankChurn correctly scaled **3 → 2 → 1** in ~8 minutes during low traffic
- Scale-up still triggered correctly under load (CPU-driven)
- No OOM kills observed — `resources.limits.memory` provides hard protection independently of HPA

---

## Consequences

- **Positive**: Correct scale-down behavior — idle pods are reclaimed within minutes
- **Positive**: Cost savings during off-peak hours (fewer pods running)
- **Positive**: HPA signal is clean and predictable (CPU correlates with request volume)
- **Negative**: No memory-based OOM protection via HPA (mitigated by `resources.limits.memory`)

## Revisit When

- Memory usage becomes variable (e.g., dynamic model loading, batch inference with variable-size inputs)
- Custom metrics HPA (request latency) is implemented — would replace CPU as the scaling signal
- KEDA adoption for scale-to-zero during extended idle periods

---

## References

- [ADR-014: Single-Worker Pod Pattern](014-single-worker-pod-ml-inference.md) — refined HPA thresholds
- [Kubernetes HPA Algorithm](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/#algorithm-details)
- [Multi-Cloud Comparison — Resource Usage](../MULTI_CLOUD_COMPARISON.md)

</div>
