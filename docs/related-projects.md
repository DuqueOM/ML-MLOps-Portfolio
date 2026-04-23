# Related Projects

## ML-MLOps Production Template

[**github.com/DuqueOM/ML-MLOps-Production-Template** →](https://github.com/DuqueOM/ML-MLOps-Production-Template)

This portfolio is the **reference implementation** from which a reusable,
opinionated **production template** was extracted. The template encodes the
operational patterns, ADR-driven conventions, and agentic development workflows
distilled from building this portfolio end-to-end.

### What's in the template

- **Agentic system** — 12 rules, 11 skills, 10 workflows that guide AI coding
  assistants (Windsurf Cascade, Claude Code, Cursor) to follow enterprise
  MLOps patterns automatically
- **Agent Behavior Protocol (AUTO / CONSULT / STOP)** — formal modes per
  operation so agents know when to execute, when to propose + wait, and when
  to refuse (e.g., `terraform apply prod` → STOP, model promotion → STOP,
  staging deploy → CONSULT)
- **EDA phase integration** — 6-phase exploratory analysis with a hard leakage
  gate and baseline distributions that feed production drift detection (no more
  disconnected data-to-training gap)
- **Supply-chain security out of the box** — gitleaks + Trivy + Syft SBOM
  (CycloneDX + SPDX) + Cosign keyless signing (GitHub OIDC) + Kyverno admission
  controller that rejects unsigned images in production. Targets SLSA Level 2.
- **Cloud-native secret management** — `common_utils/secrets.py` with
  environment-aware resolution (AWS Secrets Manager / GCP Secret Manager via
  IRSA/WI); refuses `os.environ` fallback in staging/production
- **Production templates** for every layer: EDA → training → FastAPI serving →
  Terraform (GKE + EKS) → CI/CD (GitHub Actions) → Kustomize overlays →
  monitoring (Prometheus + Grafana) → Kyverno policies
- **19 encoded anti-patterns (D-01 → D-19)** — automated detection for the most
  common ML production failures: event-loop blocking, memory-based HPA, models
  baked into images, data leakage, hardcoded credentials, static cloud keys,
  unsigned images, and more
- **Typed inter-agent handoffs** — frozen dataclasses (`EDAHandoff`,
  `TrainingArtifact`, `BuildArtifact`, `SecurityAuditResult`,
  `DeploymentRequest`) that validate invariants at construction (e.g.,
  production deploy with failed security audit raises at construction time,
  cannot be bypassed)
- **Engineering calibration** — every component sized to actual requirements,
  avoiding both under- and over-engineering

### Portfolio vs. Template — which should I use?

| I want to… | Use this |
|-----------|---------|
| **Learn how MLOps is done in production** — see real code, real ADRs, real incidents | This portfolio (`ML-MLOps-Portfolio`) |
| **Start a new MLOps project from a proven foundation** | The template (`ML-MLOps-Production-Template`) |
| **Calibrate my own portfolio project** against a live example | This portfolio |
| **Evaluate how agentic workflows accelerate ML engineering** | Both (portfolio for "how it was used", template for "how to reuse") |

### Relationship

```
ML-MLOps-Portfolio (this repo)
    │
    │  Real deployments, 3 ML services, 18 ADRs,
    │  measured incidents, 395+ tests
    │
    └──▶ ML-MLOps-Production-Template (v1.6.0)
            │
            │  Extracted patterns + reusable templates:
            │  - Agentic: 12 rules + 11 skills + 10 workflows
            │  - Behavior Protocol: AUTO / CONSULT / STOP
            │  - 19 anti-patterns (runtime, data, security)
            │  - EDA pipeline + drift detection loop
            │  - SLSA L2 supply chain (Cosign + SBOM + Kyverno)
            │  - Cloud-native secrets (IRSA / Workload Identity)
            │  - Typed inter-agent handoffs
            │
            └──▶ Your next MLOps project
```

The template is the **codified knowledge** from this portfolio — the portfolio
is the **evidence** that the template's patterns work in practice.
