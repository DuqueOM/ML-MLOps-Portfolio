<div class="portfolio-page" markdown="1">

# ADR-016: GCP vs AWS Performance Parity — Cost vs Performance Trade-off

- **Status**: Accepted
- **Date**: 2026-03-18
- **Authors**: Duque Ortega Mutis
- **Related**: [ADR-015](015-async-inference-threadpool.md) (async inference), [ADR-013](013-multicloud-parity-policy.md) (parity policy)

> **TL;DR**: BankChurn shows 2-3× higher latency on GCP under load due to `e2-medium` shared CPU vs AWS `t3.medium` burstable credits. Accepted the difference as a documented cost vs performance trade-off ($24/mo vs $145/mo for parity). Both clouds meet the <500ms idle SLA with 0% errors under 100 concurrent users.

---

## Context

After implementing async inference (ADR-015), load testing revealed significant performance differences between GCP and AWS for BankChurn:

| Environment | Idle p50 | Load p50 (50 users) | Stress p50 (100 users) |
|-------------|----------|---------------------|------------------------|
| **GCP (GKE)** | 200ms | 3100ms | 8200ms |
| **AWS (EKS)** | 110ms | 120ms | 130ms |

NLPInsight and ChicagoTaxi show comparable performance on both clouds (78-100ms).

### Root Cause Analysis

**BankChurn is CPU-bound** — `StackingClassifier` (5 base learners + meta-learner) consumes ~100ms of pure CPU time per prediction.

**Infrastructure differences:**

| Factor | GCP (current) | AWS (current) | Impact on BankChurn |
|--------|---------------|---------------|---------------------|
| Instance type | `e2-medium` | `t3.medium` | High |
| vCPU allocation | 2 shared (burstable) | 2 burstable (better credits) | High |
| CPU frequency | AMD EPYC Rome 2.2 GHz | Intel Xeon Platinum 2.5-3.1 GHz | Critical |
| Network | NGINX Ingress (L7) | NLB (L4) | Moderate |
| Node count | 1 (all 6 pods) | 1-2 (auto-scaled) | Moderate |

**Why NLPInsight/ChicagoTaxi don't improve on AWS:**
- NLPInsight: I/O-bound (tokenizer), not CPU-saturated
- ChicagoTaxi: Lightweight RandomForest (~5ms CPU), not CPU-saturated

---

## Decision

**Accept the performance difference as a documented cost vs performance trade-off.**

Do NOT upgrade GCP instance types to match AWS performance.

### Rationale

1. **BankChurn 200ms idle latency is acceptable** for a bank churn prediction tool (analyst-facing, not real-time payments)
2. **0% error rate under 100 concurrent users** on both clouds — production-ready
3. **Cost efficiency**: `e2-medium` at $24/mo vs `n2-highcpu-2` at $51/mo (+$27/mo for marginal latency improvement)
4. **Portfolio value**: Demonstrating multi-cloud trade-off analysis is more valuable than spending $100+/mo to hide infrastructure differences

### Performance Targets Met

| Service | SLA | GCP p50 | AWS p50 | Status |
|---------|-----|---------|---------|--------|
| BankChurn | < 500ms idle | 200ms | 110ms | ✅ Both pass |
| NLPInsight | < 200ms idle | 78ms | 100ms | ✅ Both pass |
| ChicagoTaxi | < 200ms idle | 100ms | 120ms | ✅ Both pass |
| All services | < 1% errors under load | 0-0.02% | 0% | ✅ Both pass |

---

## Consequences

### Positive
- **Cost-effective**: $24/mo GCP vs potential $145/mo for `c2-standard-4`
- **Educational**: Portfolio demonstrates understanding of cloud trade-offs, not just "make everything fast"
- **Realistic**: Production systems balance cost vs performance, not maximize performance at any cost
- **Documented**: ADR explains the difference instead of hiding it

### Negative
- GCP BankChurn latency is 2-3x higher than AWS under concurrent load
- May raise questions from recruiters unfamiliar with cloud instance differences

### Mitigation
- Document the difference in `docs/MULTI_CLOUD_COMPARISON.md` with root cause analysis
- Include this ADR in portfolio navigation
- Prepare interview talking points: "I chose to optimize for cost efficiency while meeting SLAs rather than over-provisioning for vanity metrics"

---

## Alternatives Considered

### 1. Upgrade GCP to `n2-highcpu-2` (2 dedicated vCPU, 2.8 GHz)
- **Cost**: +$27/mo
- **Expected improvement**: 200ms → ~120-150ms
- **Rejected**: Marginal improvement, doubles infrastructure cost

### 2. Upgrade GCP to `c2-standard-4` (4 dedicated vCPU, 3.8 GHz)
- **Cost**: +$121/mo
- **Expected improvement**: 200ms → <100ms (would beat AWS)
- **Rejected**: 6x cost increase for a portfolio project, unsustainable

### 3. Increase `min_node_count` to 2 (distribute load)
- **Cost**: +$24/mo
- **Expected improvement**: 200ms → ~150ms (moderate)
- **Rejected**: Still doesn't achieve parity, adds complexity

### 4. Node affinity for BankChurn on dedicated `c2` node pool
- **Cost**: +$145/mo for dedicated node
- **Expected improvement**: Best performance, but highest cost
- **Rejected**: Over-engineering for a 3-service portfolio

---

## Implementation

No code changes required. Document the performance difference in:
- `docs/MULTI_CLOUD_COMPARISON.md` — add root cause analysis
- `docs/load-test-results.md` — already includes GCP vs AWS comparison
- Portfolio README — mention cost-optimized infrastructure

### Interview Talking Points

> "BankChurn shows 2-3x higher latency on GCP under load because I'm using cost-optimized `e2-medium` instances ($24/mo) versus AWS `t3.medium`. The difference is CPU frequency and allocation — BankChurn's StackingClassifier is CPU-bound, while NLPInsight and ChicagoTaxi aren't, so they perform identically on both clouds.
>
> I could upgrade to `c2-standard-4` for <100ms latency, but that's $145/mo — 6x the cost — for a portfolio project. Instead, I documented the trade-off in ADR-016. In production, I'd make this decision based on actual SLAs and business requirements, not vanity metrics. Both clouds meet the <500ms SLA with 0% errors under 100 concurrent users."

---

## References

- [ADR-015: Async Inference via ThreadPoolExecutor](015-async-inference-threadpool.md)
- [Load Test Results](../load-test-results.md)
- [Multi-Cloud Comparison](../MULTI_CLOUD_COMPARISON.md)
- [GCP Machine Types Pricing](https://cloud.google.com/compute/vm-instance-pricing)
- [AWS EC2 Instance Types](https://aws.amazon.com/ec2/instance-types/)

</div>
