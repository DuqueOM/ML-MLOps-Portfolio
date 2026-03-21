# ADR-008: Canary Deployments with Argo Rollouts

- **Status**: Accepted — Manifests validated, deployment script ready, pending production execution
- **Date**: 2026-03-08
- **Authors**: Duque Ortega Mutis
- **Related**: [ADR-006](006-drift-triggered-retraining.md) (retraining triggers canary promotion)

> **TL;DR**: Adopted Argo Rollouts for canary deployments with Prometheus-based analysis templates. New model versions receive 20% → 50% → 100% traffic over 10 minutes, with automatic rollback if error rate or latency exceeds thresholds. Replaces Kubernetes' all-or-nothing RollingUpdate for ML services where a bad model can silently degrade predictions.

## Context

Standard Kubernetes `Deployment` objects use `RollingUpdate` strategy, which replaces all pods
simultaneously. For ML services, a bad model version (regression in accuracy, latency spike,
prediction drift) can impact 100% of traffic instantly. We needed a progressive delivery
mechanism that:

1. Routes a small percentage of traffic to the new version first
2. Validates health metrics (error rate, latency, prediction stability) automatically
3. Rolls back without human intervention if thresholds are violated
4. Promotes to full traffic only after sustained validation

## Decision

Use **Argo Rollouts** with Prometheus-based `AnalysisTemplates` for automated canary deployments
of all 3 ML services.

### Architecture

```
                    ┌──────────────┐
                    │   Ingress    │
                    │  (nginx)     │
                    └──────┬───────┘
                           │
              ┌────────────┴────────────┐
              │                         │
    ┌─────────▼──────────┐   ┌─────────▼──────────┐
    │   Stable Service   │   │   Canary Service    │
    │   (80% traffic)    │   │   (20% traffic)     │
    └─────────┬──────────┘   └─────────┬──────────┘
              │                         │
    ┌─────────▼──────────┐   ┌─────────▼──────────┐
    │  Stable ReplicaSet │   │  Canary ReplicaSet  │
    │  (current version) │   │  (new version)      │
    └────────────────────┘   └────────────────────┘
                                       │
                              ┌────────▼────────┐
                              │ AnalysisRun     │
                              │ (Prometheus)    │
                              │ - error rate    │
                              │ - p95 latency   │
                              │ - pred stability│
                              └─────────────────┘
```

### Canary Steps

| Step | Weight | Duration | Action |
|------|--------|----------|--------|
| 1 | 20% | 60s | Smoke test window — catch startup failures |
| 2 | — | — | Prometheus analysis: error rate <5%, p95 <500ms |
| 3 | 50% | 120s | Validation window — catch load-dependent issues |
| 4 | — | — | Second Prometheus analysis |
| 5 | 100% | — | Full promotion |

NLPInsight uses a more conservative profile (10%→40%→100%) with longer pauses due to
transformer inference latency.

### Analysis Templates

Two templates defined in `k8s/argo-rollouts/analysis-templates.yaml`:

1. **canary-health-check** — Standard canary validation:
   - Error rate < 5% (3 measurements at 30s intervals, 2 failures → rollback)
   - p95 latency < 500ms
   - Prediction distribution stability (drift detection)

2. **bluegreen-validation** — Stricter template for major model version changes:
   - Error rate < 2% (5 measurements at 60s intervals, 1 failure → rollback)
   - p99 latency < 1s

### Rollback Triggers

Automatic rollback occurs when:
- HTTP 5xx error rate exceeds 5% over a 2-minute window
- p95 request latency exceeds 500ms
- Prediction distribution shifts significantly (>0.3 deviation from baseline)

## Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| **RollingUpdate (K8s native)** | No extra tooling | No traffic splitting, no analysis |
| **Istio + VirtualService** | Full service mesh | Heavy overhead for 3 services |
| **Flagger** | Lighter than Istio | Less mature, smaller community |
| **Argo Rollouts** ✅ | Progressive delivery, Prometheus integration, active community | Requires CRD installation |

## Consequences

### Positive
- Zero-downtime deployments with automated quality gates
- Model regression detected before full traffic exposure
- Documented rollback procedure (`scripts/deploy-canary.sh --rollback`)
- Prometheus analysis reuses existing monitoring infrastructure

### Negative
- Requires Argo Rollouts CRD (additional cluster component)
- Rollout objects replace Deployment objects (cannot use both)
- NGINX Ingress required for traffic splitting (NodePort not sufficient)

### When to Revisit
- If adopting a full service mesh (Istio/Linkerd), traffic splitting moves there
- If Argo Rollouts maintenance becomes a burden, consider Flagger
- If adding A/B testing, extend analysis templates with business metrics

## Files

- `k8s/argo-rollouts/bankchurn-rollout.yaml` — BankChurn canary Rollout
- `k8s/argo-rollouts/chicagotaxi-rollout.yaml` — ChicagoTaxi canary Rollout
- `k8s/argo-rollouts/nlpinsight-rollout.yaml` — NLPInsight canary Rollout
- `k8s/argo-rollouts/analysis-templates.yaml` — Prometheus analysis templates
- `scripts/deploy-canary.sh` — Operational deployment script

## Usage

```bash
# Deploy canary
./scripts/deploy-canary.sh bankchurn v3.2.0

# Monitor
kubectl argo rollouts get rollout bankchurn-predictor -n ml-portfolio --watch

# Force promote (skip remaining analysis)
./scripts/deploy-canary.sh bankchurn --promote

# Force rollback
./scripts/deploy-canary.sh bankchurn --rollback

# Deploy all services
./scripts/deploy-canary.sh all v3.2.0
```
