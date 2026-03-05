# ADR-009: Simplification — Knowing When Not to Build

**Status**: Accepted  
**Date**: 2026-03-05  
**Decision Makers**: DuqueOM

## Context

Portfolio review feedback identified potential over-engineering: StackingClassifier with 4 base learners for 10K rows, Helm charts + Argo Rollouts for services without real traffic, OpenTelemetry tracing with no production traces, and Terraform for 2 clouds without an employer requirement. The concern: "Does this candidate know when *not* to build something?"

This ADR documents the deliberate evaluation of each component and the decision to simplify where complexity exceeded value.

## Decisions

### 1. StackingClassifier → Keep, but document the trade-off

**Evaluated**: Single LightGBM (AUC 0.86) vs StackingClassifier (AUC 0.87).  
**Finding**: The 0.01 AUC improvement does not justify 4× training time and 4× model size in most production scenarios. However, stacking demonstrates ensemble methodology knowledge.  
**Action**: Keep StackingClassifier but document in ADR-003 that a single LightGBM achieves comparable performance. In a production system with latency/cost constraints, we would choose the simpler model.

### 2. Helm Charts → Keep (production-standard packaging)

Helm is the de facto standard for Kubernetes application packaging. The chart adds <200 lines and enables `helm install` one-command deployment. Removing it would be deleting useful, standard infrastructure.

### 3. Argo Rollouts → Keep (canary deployment pattern)

Canary deployments are a core MLOps practice for safe model rollouts. The manifests are validated and the deploy script (`scripts/deploy-canary.sh`) is functional. Real deployment evidence is documented in `docs/DEPLOYMENT_EVIDENCE.md`.

### 4. OpenTelemetry → Keep (graceful no-op design)

The implementation uses a graceful fallback pattern: when OTel packages are not installed, all tracing calls become no-ops with zero runtime overhead. This is a **design pattern worth demonstrating** — it shows how to instrument code for observability without creating hard dependencies.

### 5. Terraform for 2 Clouds → Keep (IaC competency)

Multi-cloud Terraform demonstrates IaC skills. The configurations are minimal (<300 lines total) and serve as working templates. Cost: zero (no resources provisioned without explicit `terraform apply`).

### 6. Project → Remove from portfolio

**Evaluated**: MAPE 32.9% is not defensible for a pricing model. The Streamlit dashboard is the only unique component, but it doesn't compensate for weak model performance.  
**Action**: Moved to `Applied-ML-Projects` repository. Portfolio reduced to 3 focused projects (BankChurn, NLPInsight, ChicagoTaxi) covering classification, NLP, and time-series domains.

### 7. Data Leakage Fix (ChicagoTaxi)

**Found**: Same-period aggregate features (`avg_fare`, `avg_distance_miles`, `avg_speed_mph`) computed from the same trips that define `trip_count`. These values would not be available at prediction time.  
**Fix**: Replaced with lag features (`trip_count_lag_1h`, `_lag_24h`, `_lag_168h`, `_rolling_24h`) and switched from random to temporal train/test split.  
**Result**: R² improved from 0.905 → 0.9649 with honest, leak-free features.

## Guiding Principle

> **Build the simplest system that solves the problem. Add complexity only when the marginal value exceeds the marginal maintenance cost.**

For a portfolio, some components exist to demonstrate capability rather than solve an immediate need. Each such component is explicitly marked as "demonstration" in its documentation rather than presented as a production necessity.

## Consequences

- **Positive**: Portfolio narrative is clearer — 3 projects instead of 4, each with depth
- **Positive**: Data leakage fix improves technical credibility
- **Positive**: Infrastructure components are justified with explicit rationale
- **Negative**: None identified — no functionality was lost
