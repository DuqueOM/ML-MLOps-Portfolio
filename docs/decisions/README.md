# Architectural Decision Records (ADRs)

> Structured documentation of every significant technical decision in the ML-MLOps Portfolio, including context, alternatives evaluated, trade-offs accepted, and conditions for revisiting.

## Why ADRs?

ADRs capture the **reasoning behind decisions**, not just the outcome. Six months from now, when someone asks "why didn't you use Airflow?" or "why is memory excluded from HPA?", the answer is documented with data, alternatives, and trade-offs — not buried in a Slack thread.

---

## Index

| ADR | Decision | Category | Status |
|-----|----------|----------|--------|
| [001](001-cpu-only-hpa.md) | CPU-Only HPA for ML Inference Services | Infrastructure | Accepted |
| [002](002-emptydir-model-storage.md) | emptyDir + Init Container for Model Storage | Infrastructure | Accepted |
| [003](003-stacking-classifier-bankchurn.md) | StackingClassifier for BankChurn | ML Modeling | Accepted |
| [004](004-opentelemetry-graceful-fallback.md) | OpenTelemetry with Graceful No-Op Fallback | Observability | Accepted |
| [005](005-compatible-release-pinning.md) | Compatible Release Pinning (~=) for Dependencies | DevOps | Accepted |
| [006](006-drift-triggered-retraining.md) | Drift-Triggered Retraining Architecture | MLOps | Accepted (stub) |
| [007](007-feature-store-decision.md) | Feature Store — Deferred with Design Document | MLOps | Deferred |
| [008](008-argo-rollouts-canary.md) | Canary Deployments with Argo Rollouts | Infrastructure | Accepted |
| [009](009-simplification-when-not-to-build.md) | Simplification — Knowing When Not to Build | Architecture | Accepted |
| [010](010-shap-kernelexplainer-bankchurn.md) | SHAP KernelExplainer for StackingClassifier | ML Explainability | Accepted |
| [011](011-gradio-exclusion.md) | Gradio Demo — Not Deployed to Production | Architecture | Accepted |
| [012](012-security-scanner-staging-policy.md) | Security Scanner Staging vs Production Policy | Security | Accepted |
| [013](013-multicloud-parity-policy.md) | Multi-Cloud Parity Policy (GKE vs EKS) | Infrastructure | Accepted |
| [014](014-single-worker-pod-ml-inference.md) | Single-Worker Pod Pattern for ML Inference | Infrastructure | Accepted |
| [015](015-async-inference-threadpool.md) | Async Inference via ThreadPoolExecutor | Performance | Accepted |
| [016](016-gcp-aws-performance-parity.md) | GCP vs AWS Performance — Cost vs Latency Trade-off | Infrastructure | Accepted |
| [017](017-custom-vs-managed-ml-platforms.md) | Custom FastAPI + K8s vs Managed ML Platforms (SageMaker/Vertex AI) | Architecture | Accepted |

---

## Decision Flow

Many ADRs form a decision chain where one decision creates the context for the next:

```
ADR-003 (StackingClassifier)
  ├── ADR-010 (SHAP KernelExplainer — TreeExplainer incompatible)
  ├── ADR-015 (Async inference — CPU-bound predict blocks event loop)
  │     └── ADR-016 (GCP vs AWS latency — CPU-bound = cloud-sensitive)
  └── ADR-009 (Simplification — justified keeping despite complexity)

ADR-001 (CPU-only HPA)
  └── ADR-014 (Single-worker pod — refined HPA thresholds)
        └── ADR-015 (Async inference — eliminated 2-worker exception)

ADR-006 (Drift-triggered retraining)
  └── ADR-008 (Canary deployments — safe model promotion after retraining)

ADR-002 (emptyDir model storage)
  └── ADR-006 (Retraining writes new model → ConfigMap update → rollout)

ADR-012 (Security scanner policy)
  └── ADR-013 (Multi-cloud parity — security posture matches per cloud)

ADR-017 (Custom vs Managed ML Platforms)
  ├── ADR-003 (StackingClassifier — SHAP middleware justifies custom serving)
  ├── ADR-013 (Multi-cloud parity — SageMaker is AWS-only, custom is portable)
  └── ADR-009 (Simplification — SageMaker complement, not replacement)
```

---

## Format

Every ADR follows a consistent structure:

1. **TL;DR** — One-sentence impact summary
2. **Context** — Problem statement with evidence/data
3. **Decision** — What was decided
4. **Alternatives Considered** — What else was evaluated and why rejected
5. **Consequences** — Positive and negative outcomes
6. **Revisit When** — Conditions that would change the decision
7. **References** — Related ADRs and external documentation

---

## Reading Guide

- **Recruiters/Hiring Managers**: Read the TL;DR of each ADR for a quick overview of technical depth. ADR-009 (Simplification), ADR-015 (Async Inference), and ADR-016 (Cost vs Performance) are recommended for understanding engineering judgment.
- **ML Engineers**: Start with ADR-003 (model choice), ADR-010 (explainability), ADR-006 (drift retraining).
- **Platform/DevOps Engineers**: Start with ADR-001 (HPA), ADR-014 (single-worker), ADR-002 (model storage), ADR-008 (canary).
- **Security Engineers**: ADR-012 (scanner policy), ADR-005 (dependency pinning).
- **Hiring Managers (enterprise focus)**: ADR-017 (custom vs managed platforms) — demonstrates ability to articulate build-vs-buy trade-offs.
