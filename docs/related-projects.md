<div class="portfolio-page" markdown="1">

# Related Projects

## ML-MLOps Production Template

[**github.com/DuqueOM/ML-MLOps-Production-Template** →](https://github.com/DuqueOM/ML-MLOps-Production-Template)

This portfolio is the **reference implementation** from which a reusable,
opinionated **production template** was extracted. The template encodes the
operational patterns, ADR-driven conventions, and agentic development workflows
distilled from building this portfolio end-to-end — then hardened further
against NIST AI RMF, ISO/IEC 42001, the EU AI Act and frontier open-source
scaffolds (Kubeflow, ZenML, LangGraph) in a later benchmarking pass.

### What's in the template (latest, `v0.20.0` and later on `main`)

- **Vendor-neutral agentic canon, 4 IDE surfaces** — rules, skills and
  workflows live once in `agentic/` (17 rules / 21 skills / 17 workflows)
  and are regenerated, never hand-edited, into Devin (full-body mirror),
  Cursor, Claude Code and Codex (pointer files). A manifest cross-indexes
  every surface so the mapping is validated, not trusted by memory.
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
  resources. Deploy chain pins images by digest BEFORE `kubectl apply`
  so the Kyverno digest gate has compliant manifests.
- **Supply chain — closed loop end-to-end**: gitleaks + Trivy + Syft
  SBOM (CycloneDX + SPDX) + Cosign keyless signing (GitHub OIDC) +
  Kyverno admission policy that rejects unsigned or non-digest images
  in prod. SLSA Level 2 targeted. Every GitHub Action across every
  workflow — root and vendored — is pinned by commit SHA rather than a
  mutable tag, and a dedicated OpenSSF Scorecard workflow scores the
  repo on every push.
- **CI-Green Verification Gate (D-36)** — separates "check whether CI is
  green" (AUTO, read-only, always allowed) from "proceed despite red or
  missing CI" (STOP, an explicit human approval logged to the audit
  trail). Wired as a hard precondition into `/release` and into
  staging/prod deploy — the same read-vs-override split GitHub branch
  protection already uses, made explicit for agents.
- **Compliance mapping (ADR-038)** — `docs/COMPLIANCE_MAPPING.md` traces
  artifacts the template already produces (quality gates, fairness DIR
  floor, audit trail, human-in-the-loop approval) to NIST AI RMF,
  ISO/IEC 42001 and EU AI Act Arts. 9–15 control questions. Explicitly
  descriptive, not certifying — no framework certifies a template, only
  a deployed system.
- **Portability, not lock-in** — a documented swap matrix
  (`docs/ADOPTION.md`) for cloud, experiment tracking, serving backend,
  model framework, data validation, drift detection, scaffolding engine
  and IaC tool, so "agnostic to technologies" is verifiable rather than
  a slogan.
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
  hooks.
- **Audit trail wired into CI** — `scripts/audit_record.py` CLI wrapper
  appends `ops/audit.jsonl` and mirrors a markdown summary to the
  GitHub Actions step summary. `deploy-common.yml` calls it on every
  deploy (success AND failure via `if: always()`).
- **Golden Path E2E workflow** — `.github/workflows/golden-path.yml`
  validates the full chain in CI: scaffold → build + sign by digest →
  kind cluster + Kyverno admit + smoke → audit trail. Trust anchor
  for every PR.
- **36 encoded anti-patterns (D-01 → D-36)** — runtime, training,
  EDA, security, closed-loop, lifecycle (warm-up, PDB, PSS), delivery
  (env gates, API contracts, SBOM, digest pin), Copier scaffolding,
  local-first adoption safety, and CI-green release safety.
- **Self-auditing documentation** (ADR-031) — one deterministic CI gate
  enforces a single source of truth for release version, anti-pattern
  count, agentic-surface counts and ADR numbering across every document
  in the repo — a gate, not a suggestion.
- **Typed inter-agent handoffs** — frozen dataclasses (`EDAHandoff`,
  `TrainingArtifact`, `BuildArtifact`, `SecurityAuditResult`,
  `DeploymentRequest`) that validate invariants at construction.
  `DeploymentRequest` refuses to construct when `env=production` AND
  `audit.passed=False`; `SecurityAuditResult` blocks any `trivy_high`
  finding regardless of caller intent.
- **Copier-based scaffolding + local-first profiles** — `copier update`
  can pull template improvements into an already-adopted service;
  `local` / `staging` / `prod` stack profiles let a reviewer run the
  full train → serve → drift loop without provisioning a cluster, with
  `local` structurally refused any cloud credential or cluster target.
- **Engineering calibration** — every component sized to actual
  requirements, avoiding both under- and over-engineering. ADRs
  document alternatives rejected AND measurable revisit triggers.

## agent-local — the LLM plane

[**github.com/DuqueOM/agent-local** →](https://github.com/DuqueOM/agent-local)

The template's governance philosophy generalized to a new domain: local,
multi-tier LLM agents. `agent-local` is a **sibling** of the template, not a
fork of it — a reusable platform (`core/` + thin `usecases/<name>/` domains)
that reuses the template's Terraform and Kustomize when it needs cloud, and
runs the template's day-2 maintenance lanes on its own local model tiers.
The shared plan lives in the template's
[`ACTION_PLAN_LLM_AGENT.md`](https://github.com/DuqueOM/ML-MLOps-Production-Template/blob/main/docs/audit/ACTION_PLAN_LLM_AGENT.md).

### What's distinctive about it

- **Deterministic policy gate, not model judgment** — every response is
  checked against versioned YAML policies before it reaches a user; the
  gate never trusts model-authored text as evidence.
- **Reflection isolated from evidence (ADR-009)** — a model's internal
  reflection notes go to their own channel, consumed only by the final
  response generator. They are structurally prevented from being read
  as tool evidence by the policy gate or verifier — closing a class of
  self-fabricated-evidence attack, not just discouraging it.
- **MCP/A2A evaluated and rejected, with revisit triggers (ADR-010)** —
  the trendy interoperability standard was assessed against the
  platform's fail-closed tool-capability contract and declined on a
  precise technical conflict (MCP's capability hints are explicitly
  "untrusted unless from a trusted server"; the contract requires
  registry-verified capability). The rejection is written down with the
  exact evidence that would reverse it.
- **11 adversarial evaluation sets + offline gate**, including a
  dedicated injection-containment set and full-loop tests proving a
  "successfully fooled" model still can't get a policy-violating
  response past the deterministic gate.
- **OWASP LLM Top-10 (2025) security mapping** — a dedicated security
  model document maps the platform's controls to each of the ten
  categories, from prompt injection to unbounded consumption.

### Portfolio vs. Template vs. agent-local — which should I look at?

| I want to… | Look at |
|-----------|---------|
| **Learn how MLOps is done in production** — see real code, real ADRs, real incidents | This portfolio (`ML-MLOps-Portfolio`) |
| **Start a new MLOps project from a proven foundation** | The template (`ML-MLOps-Production-Template`) |
| **See the same governance model applied to LLM agents instead of tabular ML** | `agent-local` |
| **Calibrate my own portfolio project** against a live example | This portfolio |
| **Evaluate how agentic workflows accelerate ML engineering** | All three — portfolio for "how it was used", template for "how to reuse", agent-local for "how far it generalizes" |

### Relationship

```
ML-MLOps-Portfolio (this repo)
    │
    │  Real deployments, 3 ML services, 18 ADRs,
    │  measured incidents, 395+ tests
    │
    └──▶ ML-MLOps-Production-Template
            │
            │  Extracted patterns + reusable templates:
            │  - Vendor-neutral agentic canon, 4 IDE surfaces
            │    (Devin · Cursor · Claude Code · Codex)
            │  - Behavior Protocol: AUTO / CONSULT / STOP (static + dynamic)
            │  - 36 anti-patterns D-01 → D-36
            │  - Compliance mapping: NIST AI RMF · ISO 42001 · EU AI Act
            │  - CI-Green Verification Gate (D-36) — read is AUTO,
            │    override is STOP
            │  - SLSA L2 supply chain — SHA-pinned CI, OpenSSF Scorecard,
            │    Cosign signing, Kyverno digest + signature gates,
            │    SBOM (CycloneDX + SPDX) attested by digest
            │  - Portability swap matrix — cloud, tracking, serving,
            │    IaC, scaffolding — agnostic by design, not by accident
            │  - Self-auditing documentation-coherence CI gate
            │
            └──▶ agent-local (LLM plane, sibling not a fork)
                    │
                    │  Same governance philosophy, new domain:
                    │  - Deterministic policy gate over model judgment
                    │  - Reflection isolated from verifier evidence (ADR-009)
                    │  - MCP/A2A evaluated and rejected (ADR-010)
                    │  - 11 adversarial eval sets, OWASP LLM Top-10 mapped
                    │  - Reuses the template's Terraform/Kustomize for cloud
                    │
                    └──▶ Your next MLOps or agentic project
```

The template is the **codified knowledge** from this portfolio, and
`agent-local` is the proof that the codification **generalizes** — the
portfolio is the evidence that the underlying patterns work in practice.

</div>
