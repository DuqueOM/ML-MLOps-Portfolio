# ADR-007: Feature Store — Deferred with Design Document

- **Status**: Accepted — Intentionally deferred
- **Date**: 2026-03-05
- **Authors**: Duque Ortega Mutis

> **TL;DR**: Evaluated Feast, Tecton, and Hopsworks for feature management. Deferred adoption because the portfolio's 3 services have no feature-sharing needs — each uses independent, domain-specific features. Documented the design for when feature reuse across 5+ models justifies the operational overhead.

---

## Context

Feature stores (Feast, Hopsworks, Tecton) are a recognized gap in this portfolio. A senior reviewer might ask: "You have three ML services — why no feature store?" This ADR documents the deliberate decision to not implement one, the conditions under which that decision would change, and what the design would look like.

---

## Why a Feature Store Solves a Real Problem

In large-scale production ML, feature stores address three specific failure modes:

1. **Training-serving skew**: Feature logic computed differently at training time vs. inference time → model sees different distributions in production
2. **Feature duplication**: Ten teams each computing "customer 30-day spend" differently → divergent models, divergent numbers
3. **Online/offline latency mismatch**: A feature requiring a 30-day aggregation window can't be computed at request time → needs pre-materialized values

---

## Why This Portfolio Doesn't Need One (Yet)

### Reason 1: All three models use batch-computed, request-time features

| Project | Feature source at inference time | Requires pre-materialization? |
|---------|----------------------------------|-------------------------------|
| **BankChurn** | All features in the request payload (CreditScore, Age, Balance, etc.) | ❌ No — caller provides all inputs |
| **NLPInsight** | Raw text in the request | ❌ No — tokenized at inference time |

None of the three models require **pre-materialized aggregations** (e.g., "this customer's average spend over 90 days"). All features are either directly in the request or derived on the fly by `FeatureEngineer` within the same pipeline. Training-serving skew is prevented by a different mechanism: the `FeatureEngineer` and `ColumnTransformer` are serialized inside the single `model.joblib` artifact and applied identically at both training and inference time.

### Reason 2: A poorly-scoped feature store creates more problems than it solves

Adding Feast or Hopsworks to a portfolio that doesn't have:
- Multi-team feature sharing requirements
- Time-series aggregation windows
- Feature freshness SLAs below 1-hour

...would mean running a complex distributed system (Redis/DynamoDB online store + Parquet/BigQuery offline store + feature registry + materialization jobs) to serve features that could be computed in 2ms inside the request handler. This is over-engineering that a senior reviewer would recognize as cargo-culting.

---

## When This Decision Should Be Revisited

A feature store becomes necessary when **any** of the following conditions are met:

| Condition | Example |
|-----------|---------|
| Features require time-window aggregations | "Customer's average transaction value over 30 days" — requires streaming or batch materialization |
| Features must be shared across >2 models | Both churn model AND credit risk model use "days since last login" — must compute once, serve consistently |
| Feature freshness SLA < 5 minutes | Fraud detection needs real-time feature updates — Redis online store required |
| Feature computation costs are significant | Running a 1B-row aggregation at every inference call is untenable |
| >5 data scientists are writing feature code | Without a registry, feature definitions diverge across teams |

---

## What the Design Would Look Like at Scale

If BankChurn were extended to use behavioral data (the missing feature set that would push AUC from 0.87 toward 0.92+), the architecture would be:

```
                    ┌─────────────────────────────────────┐
                    │         Feature Pipeline             │
                    │  (runs daily via K8s CronJob / DAG)  │
                    │                                      │
  Raw Data (GCS) ──→│  Spark / Pandas aggregation job      │
                    │  - 30d avg balance change            │
                    │  - Support ticket count (90d)        │
                    │  - Login frequency trend             │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │         Feast Feature Store          │
                    │                                      │
                    │  Offline Store: BigQuery / GCS       │──→ Training jobs
                    │  Online Store:  Redis (GKE pod)      │──→ Inference requests
                    │  Registry:      GCS (feature defs)   │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │     BankChurn FastAPI Inference      │
                    │                                      │
                    │  1. Receive request (customer_id)    │
                    │  2. feast.get_online_features()      │──→ Redis lookup (<5ms)
                    │  3. Merge with request payload       │
                    │  4. model.predict(features)          │
                    └─────────────────────────────────────┘
```

**Key interface**: `feast.get_online_features(entity_rows=[{"customer_id": "C123"}])` returns a `pd.DataFrame` compatible with the existing `ColumnTransformer` pipeline. The `FeatureEngineer` class would be split: time-window features are pre-materialized; request-time features (derived ratios, bins) remain in the pipeline.

---

## Trade-offs of Deferring

| What's lost by not having a feature store | Actual impact on current portfolio |
|-------------------------------------------|------------------------------------|
| Cannot use time-window features | BankChurn achieves AUC 0.87 without them; gap to ~0.92 is real but not urgent for demo |
| No central feature registry | 3 models × 1 team = low coordination overhead |
| Training-serving consistency enforced manually | Enforced structurally by `model.joblib` serialization; not manual at all |

---

## References

- [ADR-006: Drift-Triggered Retraining](006-drift-triggered-retraining.md)
- [ADR-003: StackingClassifier for BankChurn](003-stacking-classifier-bankchurn.md)
- [Feast documentation](https://docs.feast.dev/)
- [Feature Store Patterns — Chip Huyen, Designing ML Systems (2022), Chapter 5]
