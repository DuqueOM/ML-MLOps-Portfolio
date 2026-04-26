# Related Projects

## ML-MLOps Production Template

[**github.com/DuqueOM/ML-MLOps-Production-Template** →](https://github.com/DuqueOM/ML-MLOps-Production-Template)

This portfolio is the **reference implementation** from which a reusable,
opinionated **production template** was extracted. The template encodes the
operational patterns, ADR-driven conventions, and agentic development workflows
distilled from building this portfolio end-to-end.

### What's in the template (v1.10.0)

- **Agentic system across three IDEs** — Windsurf (15 rules / 16 skills /
  12 workflows), Claude Code (14 rules / 12 commands), Cursor (12 rules /
  12 commands). Same invariants, native config per assistant.
- **Two Agent Behavior Protocols**:
  - **Static** — AUTO / CONSULT / STOP per operation in `AGENTS.md`
    (e.g., `terraform apply prod` → STOP, model promotion → STOP,
    staging deploy → CONSULT)
  - **Dynamic** (ADR-010) — live-signal escalation: any of
    `incident_active`, `drift_severe`, `error_budget_exhausted`,
    `off_hours`, `recent_rollback` upgrades the mode by one step;
    Prometheus-backed with file-system fallback and explicit
    `risk_signals: UNAVAILABLE` audit when neither is reachable
- **6 environment overlays** — `gcp-{dev,staging,prod}` +
  `aws-{dev,staging,prod}`, each with its own PSS-labeled namespace
  (baseline for dev/staging, restricted for prod) and tier-scaled
  resources (D-29). Deploy chain pins images by digest BEFORE
  `kubectl apply` so the Kyverno digest gate has compliant manifests.
- **Supply chain — closed loop end-to-end**: gitleaks + Trivy + Syft
  SBOM (CycloneDX + SPDX) + Cosign keyless signing (GitHub OIDC) +
  Kyverno admission policy that rejects unsigned or non-digest images
  in prod. SLSA Level 2 targeted; signing actually installed and run
  in `deploy-{gcp,aws}.yml` (was a silent gap until v1.10.0).
- **Cloud-native secret management** — `common_utils/secrets.py`
  resolves AWS Secrets Manager or GCP Secret Manager via IRSA / WI;
  refuses `os.environ` fallback in staging/production. Two runbooks
  cover bootstrap: `docs/runbooks/gcp-wif-setup.md` +
  `docs/runbooks/aws-irsa-setup.md`.
- **Per-environment Terraform remote state** — partial backend configs
  under `templates/infra/terraform/{gcp,aws}/backend-configs/` segregate
  dev / staging / prod state buckets with the bootstrap runbook
  `docs/runbooks/terraform-state-bootstrap.md`.
- **Drift + retrain operationalized** — `templates/cicd/drift-detection.yml`
  and `retrain-service.yml` ship cloud-aware data/model adapters (GCS or
  S3 via OIDC), Prometheus Pushgateway integration, and MLflow promotion
  hooks. Was scaffolded but inert before v1.10.0.
- **Audit trail wired into CI** — `scripts/audit_record.py` CLI wrapper
  appends `ops/audit.jsonl` and mirrors a markdown summary to the
  GitHub Actions step summary. `deploy-common.yml` calls it on every
  deploy (success AND failure via `if: always()`).
- **Golden Path E2E workflow** — `.github/workflows/golden-path.yml`
  validates the full chain in CI: scaffold → build + sign by digest →
  kind cluster + Kyverno admit + smoke → audit trail. Trust anchor
  for every PR.
- **30 encoded anti-patterns (D-01 → D-30)** — runtime, training,
  EDA, security, closed-loop, lifecycle (warm-up, PDB, PSS), delivery
  (env gates, API contracts, SBOM, digest pin)
- **Typed inter-agent handoffs** — frozen dataclasses (`EDAHandoff`,
  `TrainingArtifact`, `BuildArtifact`, `SecurityAuditResult`,
  `DeploymentRequest`) that validate invariants at construction.
  `DeploymentRequest` refuses to construct when `env=production` AND
  `audit.passed=False`; `SecurityAuditResult` blocks any `trivy_high`
  finding regardless of caller intent.
- **Productization roadmap published (ADR-015)** — 3 phases / 12 PRs
  going from v1.10.0 (audit-closed) toward a self-service product:
  bootstrap/live Terraform split, IAM least-privilege defaults, EDA
  artifact contracts, real retrain loop, alert→runbook→action wiring,
  multi-environment SLO budgets, and a public reproducible demo.
- **Engineering calibration** — every component sized to actual
  requirements, avoiding both under- and over-engineering. ADRs
  document alternatives rejected AND measurable revisit triggers.

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
    └──▶ ML-MLOps-Production-Template (v1.10.0)
            │
            │  Extracted patterns + reusable templates:
            │  - Agentic, tri-IDE: Windsurf · Claude Code · Cursor
            │  - Behavior Protocol: AUTO / CONSULT / STOP (static + dynamic)
            │  - 30 anti-patterns D-01 → D-30
            │  - EDA pipeline + drift detection + retrain loop
            │    (cloud-aware GCS/S3 adapters via OIDC)
            │  - SLSA L2 supply chain — Cosign signing actually invoked
            │    in deploy chain, Kyverno digest + signature gates,
            │    SBOM (CycloneDX + SPDX) attested by digest
            │  - Cloud-native secrets (IRSA + Workload Identity) +
            │    /secret-breach incident playbook
            │  - 6 env overlays (gcp-{dev,staging,prod} + aws-…) with
            │    PSS-labeled namespaces and tier-scaled resources
            │  - Typed inter-agent handoffs that validate at construction
            │  - Audit trail (ops/audit.jsonl) wired into CI on every deploy
            │  - Golden Path E2E workflow as PR trust anchor
            │  - ADR-015 productization roadmap (3 phases / 12 PRs)
            │
            └──▶ Your next MLOps project
```

The template is the **codified knowledge** from this portfolio — the portfolio
is the **evidence** that the template's patterns work in practice.
