# Agentic Development Configuration

**Last Updated**: April 2026 | **Portfolio Version**: 3.6.0

> 18 ADRs and 3 production incidents encoded as behavioral constraints for AI-assisted development.
> Not documentation the agent reads — rules the agent follows automatically.

---

## What this is

This portfolio was built using [Windsurf Cascade](https://windsurf.ai/) as the AI development assistant. Most developers who use AI tools configure them with style preferences or basic project context. This portfolio takes a different approach: the same 18 Architectural Decision Records that document production decisions are encoded as **behavioral constraints** that govern every interaction between the AI and the codebase.

The result: the agent cannot accidentally introduce `uvicorn --workers N` under Kubernetes (ADR-014), generate HPA manifests with the old 70% threshold instead of 50%/60% (ADR-001), or use `TreeExplainer` for SHAP with a `StackingClassifier` (ADR-010). Operational knowledge encoded, not just referenced.

---

## Architecture — three layers

```
AGENTS.md                    ← project identity + DO NOT VIOLATE patterns
.windsurf/
├── rules/     (7 files)     ← context-aware behavioral constraints
├── skills/    (6 dirs)      ← multi-step operational procedures
└── workflows/ (6 files)     ← structured prompt-triggered workflows
```

---

## Layer 1 — Rules (behavioral constraints)

Rules are the always-active layer. They fire contextually based on what file the agent is editing — not globally, avoiding token waste.

| File | Trigger | What it enforces |
|------|---------|-----------------|
| `01-mlops-conventions.md` | `always_on` | Core ADR patterns, tech stack, code standards |
| `02-kubernetes.md` | `k8s/**/*.yaml`, `helm/**/*.yaml` | CPU-only HPA, correct thresholds (50%/60%/60%), single-worker |
| `03-terraform.md` | `**/*.tf` | Remote state, resource tagging, secrets never hardcoded |
| `04-python-ml.md` | `**/*.py` | Async inference pattern, KernelExplainer for SHAP, `~=` pinning |
| `05-github-actions.md` | `.github/workflows/*.yml` | Matrix strategy, SHA-pinned actions, coverage thresholds |
| `06-documentation.md` | `docs/**/*.md` | ADR format, content guidelines, technical writing standards |
| `07-docker.md` | `Dockerfile*`, `docker-compose*.yml` | Multi-stage builds, non-root user, no model artifacts baked in |

The glob trigger system means the Kubernetes rule only activates when editing K8s manifests — the agent isn't carrying irrelevant context for every Python file it touches.

---

## Layer 2 — Skills (operational procedures)

Skills are multi-step procedures invoked for complex operational tasks. Each skill has a `SKILL.md` with the procedure and supplementary data files with service-specific parameters.

| Skill | Invoked when | Supplementary data |
|-------|-------------|-------------------|
| `debug-ml-inference` | Inference bug, wrong predictions, slow latency, HPA issues | `adr-quick-reference.md` — symptom → root cause → ADR mapping |
| `deploy-gke` | Deploying to GKE (GCP) | `checklist.md` — pre/post-deploy verification + rollback procedure |
| `deploy-aws` | Deploying to EKS (AWS) | `checklist.md` — IRSA troubleshooting + rollback procedure |
| `drift-detection` | PSI monitoring, retraining triggers | `psi-thresholds.md` — per-service, per-feature PSI thresholds |
| `model-retrain` | Any model retraining event | `validation-criteria.md` — per-service acceptance gates + baseline metrics |
| `release-checklist` | Publishing a new version | `version-template.md` — CHANGELOG entry template + versioning rules |

### Diagnostic decision tree — `debug-ml-inference`

The `adr-quick-reference.md` maps symptoms directly to verified root causes:

| Symptom | Root Cause | ADR |
|---------|-----------|-----|
| 81%+ error rate under load | `uvicorn --workers N` sharing CPU budget under K8s | ADR-014 |
| HPA stuck, never scales down | Memory-based HPA + fixed ML model RAM footprint | ADR-001 |
| SHAP returns all-zero values | `TreeExplainer` incompatible with `StackingClassifier` | ADR-010 |
| Wrong predictions, no error raised | numpy 2.x + joblib deserialization | ADR-005 |
| Slow predictions (>500ms p95) | `ThreadPoolExecutor` saturation or CPU limit too low | ADR-015 |

---

## Layer 3 — Workflows (structured prompt templates)

Workflows are invoked by typing a slash command. They provide structured, step-by-step protocols for repeatable operational tasks — each step verified against the portfolio's actual configuration.

| Command | Purpose | Cross-references |
|---------|---------|-----------------|
| `/incident` | ML service incident response (P1–P4 classification, diagnostic commands, post-incident ADR) | Invokes `debug-ml-inference` skill |
| `/retrain` | Model retraining (data validation → training → evaluation → MLflow → deployment) | Invokes `model-retrain` skill |
| `/drift-check` | PSI-based drift analysis (manual trigger, threshold evaluation, root cause) | Invokes `drift-detection` skill |
| `/release` | Full release process (version bump → Docker build → GKE deploy → EKS deploy → git tag) | Invokes `release-checklist` skill |
| `/load-test` | Locust performance testing (service selection, baseline comparison, HPA verification) | — |
| `/new-adr` | Create a new Architecture Decision Record (auto-numbered, standard format, index update) | — |

### Skills → Workflow cross-references

| Trigger | Skill invoked | Workflow chained |
|---------|--------------|-----------------|
| Inference bug | `debug-ml-inference` | `/incident` |
| Drift alert (PSI ≥ 0.25) | `drift-detection` | `/retrain` |
| Version release | `release-checklist` | `/release` |
| Tag push (GKE) | `deploy-gke` | — |
| Tag push (EKS) | `deploy-aws` | — |
| Scheduled retrain | `model-retrain` | `/drift-check` post-deploy |

---

## Critical constraints encoded

These patterns are in the `always_on` rule and repeat across multiple context-specific rules. They exist because each one corresponds to a real production incident or architectural failure:

```
NEVER  uvicorn --workers N under Kubernetes
       → Workers share one CPU budget → thrashing, not parallelism
       → ADR-014, ADR-015 | Incident: 81% error rate

NEVER  memory-based HPA for ML pods
       → Fixed model RAM footprint = mathematically cannot scale down
       → ADR-001 | Incident: HPA stuck at 3 replicas for hours

ALWAYS KernelExplainer for SHAP with StackingClassifier
       → TreeExplainer is incompatible → all-zero values in production
       → ADR-010 | Incident: silent SHAP failure

ALWAYS compatible release pinning (~=) for all dependencies
       → numpy 2.x silently corrupts joblib-serialized models
       → ADR-005 | Incident: wrong predictions, no error raised

ALWAYS verify kubectl config current-context before apply
       → Prevents applying to the wrong cluster
       → Safety gate on all K8s operations

HPA CPU targets: BankChurn 50% · NLPInsight 60% · ChicagoTaxi 60%
       → Refined from 70–75% by ADR-014 for faster scale-out
       → Any value of 70% in K8s manifests is outdated — update it
```

---

## MCP server integration (recommended)

For full agent capability with live cluster and infrastructure access:

| MCP Server | Purpose | Integration point |
|------------|---------|------------------|
| `@anthropic-ai/mcp-server-kubernetes` | Live K8s cluster management | Deploy skills, incident workflows |
| `mcp-server-terraform` | Terraform plan/apply | IaC workflows |
| `mcp-prometheus` | PromQL queries against live metrics | Drift detection, monitoring |
| `mcp-docker` | Container build and management | CI/CD workflows |

Without MCP servers, all skills and workflows operate in read-only advisory mode — they provide commands and checklists, but execute nothing autonomously.

---

## AI transparency

This portfolio was built using Windsurf Cascade for code generation and boilerplate acceleration. All architectural decisions, system design, trade-off analysis, incident diagnosis, and ADR documentation are the author's own work.

The `.windsurf/` configuration is itself a demonstration of the engineering philosophy behind this portfolio: **AI tools should be governed by documented decisions, not given free rein.** The same rigor applied to production systems applies to the development environment that builds them.

→ [View AGENTS.md on GitHub](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/AGENTS.md)
→ [View .windsurf/ directory on GitHub](https://github.com/DuqueOM/ML-MLOps-Portfolio/tree/main/.windsurf)

---

*Part of the [ML-MLOps Portfolio](https://github.com/DuqueOM/ML-MLOps-Portfolio) — April 2026 — v3.6.0*