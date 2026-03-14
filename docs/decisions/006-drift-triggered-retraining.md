# ADR-006: Drift-Triggered Retraining Architecture

**Status**: Accepted — Stub implemented, full orchestration deferred  
**Date**: March 2026  
**Authors**: Duque Ortega Mutis

---

## Context

The portfolio deploys three ML models (BankChurn, NLPInsight) on GKE with Evidently AI running weekly drift checks (PSI + KS statistics). When drift is detected, the current response is **manual**: a Prometheus alert fires, an on-call engineer investigates, and retraining is triggered by hand.

The question "how do you trigger retraining when you detect drift?" is one of the most common MLOps interview questions. This ADR documents the architectural decision for automated retraining, the trade-offs evaluated, and the lightweight implementation currently in place.

---

## Problem Statement

Drift detection without automated response creates a gap:

```
Evidently detects drift
        ↓
Prometheus alert fires
        ↓
Engineer manually triggers retraining  ← bottleneck, human latency
        ↓
New model validated and promoted
```

In production, this manual step introduces latency (hours to days) during which a degraded model serves live traffic.

---

## Options Evaluated

### Option A: Airflow / Prefect / Kubeflow Pipelines

Full orchestration DAGs that manage data ingestion, feature engineering, training, evaluation, and promotion.

**Pros**: Industry standard, rich UI, retry logic, DAG versioning, parallel execution  
**Cons**: Significant operational overhead (Airflow needs its own DB, scheduler, workers); adds 3–5 pods to cluster; overkill for 3-model portfolio; ~2 weeks to implement correctly

**Decision**: Deferred. The operational cost exceeds the value for a 3-service portfolio. The *design* is documented here; the *plumbing* would be added when the number of models or retraining frequency justifies it.

### Option B: K8s CronJob + GitHub Actions webhook

A Kubernetes CronJob periodically checks drift scores via the Prometheus API. If any model's PSI score exceeds the threshold, it triggers a GitHub Actions `workflow_dispatch` event, which runs the full training + evaluation + push CI pipeline.

**Pros**: No new infrastructure; reuses existing CI/CD; auditable (GitHub Actions logs); model promotion through the same pipeline as new releases  
**Cons**: Polling-based (not event-driven); minimum granularity = CronJob schedule  

**Decision**: ✅ **Selected** — implemented as the current lightweight solution.

### Option C: Evidently + Webhook callback

Evidently's monitoring server can POST to a webhook when a drift report exceeds a threshold.

**Pros**: Event-driven (no polling latency)  
**Cons**: Requires Evidently Cloud or self-hosted Evidently UI server; adds another managed service  

**Decision**: Deferred to future v4.0 when Evidently UI server is added.

---

## Decision

Implement a **K8s CronJob** that:
1. Queries Prometheus for drift metrics (`bankchurn_psi_score`, `_psi_score`, `nlpinsight_distribution_shift`)
2. Compares against thresholds (PSI > 0.2 = significant drift; PSI > 0.25 = critical)
3. If threshold exceeded, calls the GitHub API to trigger `workflow_dispatch` on the training pipeline
4. Logs the decision (triggered/skipped) to stdout for Prometheus scraping

The retraining pipeline itself runs in GitHub Actions (same as the CI pipeline), producing a new model artifact, running evaluation, and requiring AUC/R²/F1 not to regress before promoting to GCS.

---

## Implementation

### Drift Check CronJob

See `k8s/base/drift-retraining-cronjob.yaml` — runs daily at 02:00 UTC.

### Thresholds

| Model | Metric | Warning | Critical (triggers retrain) |
|-------|--------|---------|----------------------------|
| BankChurn | PSI (feature distribution) | > 0.10 | > 0.20 |
| BankChurn | AUC degradation (rolling holdout) | < 0.80 | < 0.75 |
| NLPInsight | Sentiment distribution shift | > ±15% | > ±25% |
| NLPInsight | F1-macro degradation | < 0.85 | < 0.80 |

### Retraining Pipeline Gates (prevents bad models from promoting)

A retrained model is only promoted to GCS (and deployed) if:
1. Primary metric does not regress beyond 5% from the current production model
2. Per-class F1 ≥ 0.70 (NLPInsight: no class abandoned)
3. P95 latency does not increase beyond 20% from baseline
4. No new Bandit HIGH severity findings in retrained code

If any gate fails, the pipeline opens a GitHub Issue with the evaluation diff and halts promotion.

---

## Trade-offs Accepted

| Trade-off | Rationale |
|-----------|-----------|
| Polling vs. event-driven | Polling adds up to 24h lag vs. event-driven. Acceptable: model quality doesn't degrade catastrophically in 24h for these use cases |
| GitHub Actions as retraining executor | Ties retraining to CI minutes quota. Acceptable for portfolio scale; would move to dedicated training cluster at production scale |
| No A/B traffic splitting during promotion | Blue/green promotion via Argo Rollouts (already configured) provides rollback safety without full A/B |

---

## Future State (v4.0)

At scale (10+ models, daily retraining), this design would evolve to:

```
Evidently UI Server → Webhook → Prefect Cloud
                                    ↓
                            Feature pipeline (DVC)
                                    ↓
                            Training job (K8s Job / Vertex AI)
                                    ↓
                            MLflow Model Registry (Staging)
                                    ↓
                            Automated evaluation gates
                                    ↓
                            Argo Rollouts promotion (canary)
```

The interfaces between components (Evidently → webhook, MLflow registry → deployment) are the same; only the executors change from GitHub Actions to Prefect.

---

## References

- [ADR-001: CPU-Only HPA](001-cpu-only-hpa.md)
- [K8s CronJob manifest](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/k8s/base/drift-retraining-cronjob.yaml)
- [Prometheus alert rules](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/infra/prometheus-rules.yaml)
- [Evidently drift configuration](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/BankChurn-Predictor/configs/config.yaml)
