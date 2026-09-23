<div class="portfolio-page" markdown="1">

# Related Projects

Four repositories, one line of work. Two of them are templates, and they are
**not the same tool**: `ml-service-template` governs **classical ML** —
scikit-learn, XGBoost, LightGBM, single team, 1–5 models — and is deliberately
small; `ml-platform` is the substrate for problem shapes it defers by decision:
deep learning, LLM/RAG and agents alongside tabular. The boundary between them is a written decision, not an accident of
history. [Jump to the side-by-side comparison](#the-two-templates-side-by-side).

## ML Service Template — classical ML, production defaults

[**github.com/DuqueOM/ml-service-template** →](https://github.com/DuqueOM/ml-service-template)

This portfolio is the **reference implementation** from which a reusable,
opinionated **production template** was extracted. The template encodes the
operational patterns, ADR-driven conventions, and agentic development workflows
distilled from building this portfolio end-to-end — then hardened further
against NIST AI RMF, ISO/IEC 42001, the EU AI Act and frontier open-source
scaffolds (Kubeflow, ZenML, LangGraph) in a later benchmarking pass.

**Its scope limit is itself a decision.** Classical ML only — scikit-learn,
XGBoost, LightGBM — single team, 1–5 models, small-team calibration — "2–3 models → CronJob, not Airflow", "in-memory
DataFrames → Pandera, not Great Expectations". Widening it to cover feature
stores, lakehouse formats, distributed training and GenAI serving would not
improve it; it would destroy the property that makes it recommendable, which
is that it is small enough to read in an afternoon. That work needed its own
home, and got one — see [`ml-platform`](#ml-platform-the-substrate-for-every-problem-shape).

### What's in the template (latest, `v0.29.0` and later on `main`)

- **Vendor-neutral agentic canon, 4 IDE surfaces** — rules, skills and
  workflows live once in `agentic/` (19 rules / 27 skills / 20 workflows)
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
- **Native-cloud edge protection (D-38, ADR-042)** — Cloud Armor (GCP) and
  AWS WAF+Shield Standard (AWS) are the per-cloud default, wired via
  opt-in Kustomize Components; Cloudflare stays available for genuinely
  concurrent multi-cloud deployments but is never the default. A
  read-only `edge-audit` skill and two alerts track coverage and audit
  freshness — deliberately without duplicating each cloud's own WAF
  analytics console.
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
- **38 encoded anti-patterns (D-01 → D-38)** — runtime, training,
  EDA, security, closed-loop, lifecycle (warm-up, PDB, PSS), delivery
  (env gates, API contracts, SBOM, digest pin), Copier scaffolding,
  local-first adoption safety, and CI-green release safety. Plus a
  second, deliberately separate namespace — **8 audit-standard
  anti-patterns (Q-01 → Q-08, ADR-043)** — for erosion that no runtime
  test catches: unpinned actions, license drift, evidence-free releases,
  complexity hotspots, weakened gates, one-sided vendored edits,
  undocumented changes, working-tree pollution. Owned by a new Layer 3
  agent, `Agent-QualityGuardian`, which runs the recurring 23-domain
  enterprise audit and chains into `/document-changes` so every finding
  it fixes stays documented.
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
- **External landscape review, decision-annex style (ADR-041)** — five
  external agent-tooling projects evaluated for what would genuinely
  strengthen the governance model. Four narrowly-scoped skills adopted
  (dual-axis PR review, systematic bug diagnosis, pre-scaffold ML
  problem spec capture, blameless incident postmortems); three full
  frameworks explicitly rejected with reasons and revisit triggers on
  record, including a persona/orchestration system that would have
  violated the template's own engineering-calibration principle.

## ml-platform — the substrate for every problem shape

[**github.com/DuqueOM/ml-platform** →](https://github.com/DuqueOM/ml-platform) ·
[**Full dedicated page →**](ml-platform.md)

The second template, and the enterprise one. Where `ml-service-template`
answers *"I need governed **classical ML** in production"*, `ml-platform`
answers *"I need a substrate that spans problem shapes the first one defers"* —
tabular, time series, deep learning, LLM/RAG and agents, on GCP and AWS. It
**consumes** the first template through `copier` and is forbidden from
reimplementing it: where the two disagree about serving, containers, probes,
manifests or supply chain, the template wins (ADR-003).

### What it adds above the template's boundary

- **Lakehouse and real data engineering** — Apache Iceberg with monthly
  partitioning and time travel (verified against real MinIO: reading snapshot 1
  returns January only, 77,539 rows, while the table holds both months,
  151,920), BigLake on GCP and S3 Tables on AWS, DuckDB + Polars, dbt, and
  Spark scoped to historical backfill only because the DuckDB crossover
  threshold was *measured* rather than assumed.
- **Point-in-time correct features** — `libs/feature-defs` ships `as_of_join`
  plus a leakage detector that runs on the *joined* frame, so it catches the
  mistake regardless of which join produced it. A `naive_join` is kept
  deliberately, so the detector can be shown to catch something real.
- **Orchestration with lineage** — Airflow 3 DAGs and KFP v2 pipelines, with
  Vertex AI Pipelines and SageMaker Pipelines as the managed targets. This is
  precisely the tier the template refuses on calibration grounds: for 2–3
  models a CronJob is correct, and an orchestrator is over-engineering.
- **GitOps reconciliation** — ArgoCD with ApplicationSets and Argo Rollouts,
  instead of the template's governed `kubectl apply` through GitHub Actions.
- **Grafana LGTM observability** — OpenTelemetry traces into Loki, Tempo and
  Mimir, with Jaeger as the local backend, rather than Prometheus + Grafana
  alone.
- **LLMOps as a first-class plane** — LiteLLM, a prompt registry, a semantic
  cache, guardrails, Langfuse tracing and promptfoo evaluation gates. All of
  it explicitly out of scope for the first template.
- **Deep learning** — LoRA/PEFT and LayoutLM wired as demonstrated tiers for
  the document-intelligence track.
- **Drift detection per project kind (ADR-007)** — the inherited machinery
  was built for *one* kind, a tabular service. Four kinds get four detectors
  on one shared contract: PSI with quantile bins for tabular, embedding-space
  drift for documents, recall-on-a-frozen-eval-set for retrieval, and
  tool-use / escalation / policy-gate-rejection rates for agents. Plus the
  failure most easily missed — a provider silently changing the model behind a
  version alias, where evals degrade with zero code, data or deploy change.
- **Technology triage instead of an anti-pattern catalogue (ADR-004)** —
  every tool carries a public tier: **core** (critical path, needs an ADR, a
  gate and a runbook), **demonstrated** (one narrow use with its stated
  reason), **studied** (recorded findings, not wired in), or **rejected**
  (evaluated and declined, with the reason). A reader never has to guess
  whether something is operated or merely present.
- **A status table derived from the filesystem** —
  `scripts/check_implementation_status.py` generates it, because a status
  table a human maintains will drift. Currently **48 done · 2 partial ·
  5 absent** of 55 tracked components. A component marked ⬜ is *absent*, not
  "planned".
- **Evidence layers, with the top row printed at zero** — every component
  carries the layer its evidence reaches: **37 at L1** (the suite passes),
  **11 at L2** (the thing executes), **4 with L3 evidence available but not
  run in CI**, and **0 at L4** — no cloud rollout, because none has happened.
  The taxonomy exists because six Kubernetes overlays once rendered green for
  weeks while their probes pointed at routes the service does not serve.
- **A falsifiable platform claim** — *C1: a second project reuses ≥3 shared
  libraries with no fork, verified by a dependency-graph test in CI.* If C1
  fails, this is a monorepo of unrelated projects and the platform claim is
  false. It is first testable at Phase 3, deliberately early.
- **Measurement honesty as a shipped artifact** — a semantic retrieval index
  was built, evaluated against the lexical baseline, tied it (both 15.4%
  recall@5), failed to clear the 0.05 margin, and **no index ships**. The
  number, the diagnosis and what would reverse the decision are published
  anyway.
- **10 ADRs, and a rule about documents** — ADR-005 rule H: *a document
  asserting something false is itself a defect, even when the code is
  correct.* The rule has a specific origin — an ADR in the sibling agent
  platform recorded a hardware budget as "measured" from a single reading of a
  fluctuating quantity, and rejected a model as too slow by citing a benchmark
  run under the very assumption it was used to justify. Re-measured, the
  budget was off by more than a gigabyte and the model was 3.3× faster. The
  wrong claims were preserved with a dated correction rather than edited away.

### The two templates, side by side

| | `ml-service-template` | `ml-platform` |
| --- | --- | --- |
| **Question it answers** | "I need governed **classical ML** in production" | "I need a **substrate** spanning tabular, DL, LLM and agents" |
| **Unit of reuse** | A scaffold you copy out and own | A library plus a running service, consumed in-repo |
| **Model kinds** | Tabular / classical ML only — a stated limit, not an omission | Tabular · time series · deep learning · LLM/RAG · agents |
| **Data layer** | In-memory DataFrames, Pandera validation | Iceberg lakehouse, BigLake / S3 Tables, DuckDB + Polars, dbt, point-in-time joins with a leakage detector |
| **Orchestration** | CronJob + GitHub Actions — calibrated for 2–3 models | Airflow 3 + KFP v2, Vertex AI Pipelines, SageMaker Pipelines |
| **Deployment** | `kubectl apply` through governed GitHub Actions | GitOps: ArgoCD + ApplicationSets + Argo Rollouts |
| **Observability** | Prometheus + Grafana + Evidently | OpenTelemetry + Grafana LGTM (Loki · Tempo · Mimir) + Jaeger |
| **Drift** | PSI with quantile bins, one tabular detector | Four detectors for four project kinds, one shared contract |
| **LLM / GenAI** | Out of scope by decision | LiteLLM, prompt registry, semantic cache, guardrails, promptfoo gates |
| **Governance model** | 38 anti-patterns (D-01→D-38) + 8 audit-standard (Q-01→Q-08) | Technology triage: core / demonstrated / studied / **rejected**, each with its reason |
| **Agentic surface** | 19 rules · 27 skills · 20 workflows | 23 rules · 29 skills · 22 workflows |
| **ADRs** | 52 | 10 |
| **Entry cost** | Minutes — `copier copy` a service | Hours — a monorepo with a six-stage progression |
| **Read it in** | An afternoon | Not in an afternoon, and that is the trade |

**If your models are classical ML, the first template is the right answer and
the second is over-engineering.** The second earns its complexity only once you
need problem shapes the first defers by decision — deep learning, retrieval,
agents — sharing one substrate.

## agent-local — the LLM core

[**github.com/DuqueOM/agent-local** →](https://github.com/DuqueOM/agent-local) ·
[**Full dedicated page →**](agent-local.md)

The template's governance philosophy generalized to a new domain: local,
multi-tier LLM agents. `agent-local` is a business-agnostic platform
(`core/` + thin `usecases/<name>/` domains), not a fork of anything — the
agent core on its own, without a platform around it.

**It is also the LLM plane inside `ml-platform`.** That repository vendored
this work in with its full git history (ADR-002): `core/` became
`libs/llm-core/`, and the `tienda` use-case became
`projects/store-assistant/`. Cross-repository coordination costs two CI
configurations, two changelogs and two ADR sets, and a third participant makes
that cost superlinear.

The standalone repository stays live, because the two are not the same value.
`ml-platform` gives this core one particular, governed use inside a platform;
`agent-local` is the **standalone version** of that core, for anyone who wants
it by itself. The core itself is developed in `ml-platform`. The original shared plan lives in the template's
[`ACTION_PLAN_LLM_AGENT.md`](https://github.com/DuqueOM/ml-service-template/blob/main/docs/audit/ACTION_PLAN_LLM_AGENT.md).

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

### Which one should I look at?

| I want to… | Look at |
|-----------|---------|
| **Learn how MLOps is done in production** — see real code, real ADRs, real incidents | This portfolio (`ML-MLOps-Portfolio`) |
| **Ship classical ML properly, without building a platform first** | `ml-service-template` |
| **Work beyond classical ML** — deep learning, LLM/RAG, agents — on shared substrate | `ml-platform` |
| **See lakehouse, feature store, orchestration and GitOps done together** | `ml-platform` |
| **Take the LLM agent core on its own, with no platform around it** | `agent-local` |
| **Judge scope discipline** — knowing which problems a tool should *not* absorb | Both templates, read against each other |
| **Calibrate my own portfolio project** against a live example | This portfolio |
| **Evaluate how agentic workflows accelerate ML engineering** | All four — portfolio for "how it was used", the templates for "how to reuse", agent-local for "how far it generalizes" |

### Relationship

```
ML-MLOps-Portfolio (this repo)
    │
    │  Real deployments, 3 ML services, 18 ADRs,
    │  measured incidents, 395+ tests
    │  Where the lessons were paid for.
    │
    ├──▶ ml-service-template  ·  CLASSICAL ML, production defaults
    │       │
    │       │  Extracted patterns, deliberately bounded:
    │       │  - Vendor-neutral agentic canon, 4 IDE surfaces
    │       │    (Devin · Cursor · Claude Code · Codex)
    │       │  - Behavior Protocol: AUTO / CONSULT / STOP (static + dynamic)
    │       │  - 38 anti-patterns D-01 → D-38, plus Q-01 → Q-08
    │       │  - Compliance mapping: NIST AI RMF · ISO 42001 · EU AI Act
    │       │  - CI-Green Verification Gate (D-36) — read is AUTO,
    │       │    override is STOP
    │       │  - SLSA L2 supply chain — SHA-pinned CI, OpenSSF Scorecard,
    │       │    Cosign signing, Kyverno digest + signature gates, SBOM
    │       │  - Self-auditing documentation-coherence CI gate
    │       │  Scope limit is itself an ADR: widening it would destroy
    │       │  the property that makes it recommendable.
    │       │
    │       │  consumed via copier (ADR-003) — never forked, never
    │       │  reimplemented; the template wins on serving concerns
    │       ▼
    └──▶ ml-platform  ·  the substrate EVERY problem shape shares
            │
            │  Everything above that boundary:
            │  - Lakehouse: Iceberg · BigLake / S3 Tables · DuckDB + Polars
            │  - Point-in-time joins with a leakage detector
            │  - Orchestration: Airflow 3 + KFP v2 → Vertex AI / SageMaker
            │  - GitOps: ArgoCD + ApplicationSets + Argo Rollouts
            │  - Observability: OTel → Grafana LGTM (Loki · Tempo · Mimir)
            │  - LLMOps: LiteLLM · prompt registry · semantic cache ·
            │    guardrails · promptfoo eval gates
            │  - Deep learning: LoRA/PEFT · LayoutLM
            │  - Drift per project kind (ADR-007): tabular · embedding ·
            │    retrieval · agent trajectory, one shared contract
            │  - Technology triage: core / demonstrated / studied / rejected
            │  - Status table derived from the filesystem, L4 printed at zero
            │
            ◀── agent-local, vendored with full history (ADR-002):
            │       core/ → libs/llm-core/
            │       usecases/tienda/ → projects/store-assistant/
            │       The standalone repo stays live as the core's standalone version:
            │       - Deterministic policy gate over model judgment
            │       - Reflection isolated from verifier evidence (ADR-009)
            │       - MCP/A2A evaluated and rejected (ADR-010)
            │       - 11 adversarial eval sets, OWASP LLM Top-10 mapped
            │
            └──▶ Your next MLOps or agentic project
```

The portfolio is the evidence that the underlying patterns work in practice.
`ml-service-template` is the **codified knowledge** from it, bounded on
purpose. `ml-platform` is what that boundary made necessary — and the pair is
the argument: knowing which problems a tool should *not* absorb is worth more
than a single repository that tried to absorb all of them.

</div>
