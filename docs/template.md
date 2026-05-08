# Production Template

<div class="portfolio-page portfolio-template" markdown="1">

<div class="portfolio-hero" markdown="1">
<span class="portfolio-eyebrow">Production template and agentic operating model</span>

# A reusable ML service template with governed AI-assisted engineering

The [ML-MLOps Production Template](https://github.com/DuqueOM/ML-MLOps-Production-Template)
is the strongest artifact in this portfolio. It packages the production lessons
from the monorepo into a starter system for ML services: FastAPI serving,
training/serving parity, CI/CD, Docker, Kubernetes, Terraform examples,
observability hooks, runbooks and an explicit agentic governance model.

<div class="portfolio-actions" markdown="1">
[Open the template repo](https://github.com/DuqueOM/ML-MLOps-Production-Template){ .portfolio-button .portfolio-button--primary }
[Read the quick start](https://github.com/DuqueOM/ML-MLOps-Production-Template/blob/main/QUICK_START.md){ .portfolio-button }
[Review technical evidence](technical-evidence.md){ .portfolio-button }
</div>
</div>

<div class="portfolio-stat-strip" markdown="1">
<div class="portfolio-stat">
<small>Serving baseline</small>
<strong>FastAPI scaffold</strong>
<span>Predict, batch predict, health, readiness, metrics and model operations.</span>
</div>
<div class="portfolio-stat">
<small>Cloud posture</small>
<strong>GKE + EKS ready</strong>
<span>Kubernetes overlays and Terraform examples for both paths.</span>
</div>
<div class="portfolio-stat">
<small>Agentic governance</small>
<strong>AUTO / CONSULT / STOP</strong>
<span>Rules for when agents can act, ask or halt for safety.</span>
</div>
<div class="portfolio-stat">
<small>Adoption status</small>
<strong>Review-ready by design</strong>
<span>Template defaults are documented, tested and scoped for adoption.</span>
</div>
</div>

## Why This Is More Than A Template

<div class="portfolio-split" markdown="1">
<div markdown="1">

The template is not only a folder structure. It is an operating contract for
starting ML services with fewer avoidable mistakes. It defines what a generated
service should contain, how it should be validated, which deployment paths it
can follow and how AI agents are allowed to participate in the work.

The important point is the second-order artifact: I did not only build three
portfolio services. I extracted the reusable production system behind them.

</div>
<div class="portfolio-callout" markdown="1">
<strong>Technical reviewer signal</strong>

The most distinctive part is the agentic operating model: canonical rules,
skills, workflows and risk escalation are written as code-adjacent governance,
not left as informal prompting.
</div>
</div>

## Production Scaffold Contract

<div class="portfolio-system-map" markdown="1">
<div class="portfolio-system-node" markdown="1">
<small>1. Service API</small>
<h3>FastAPI by default</h3>
<p>The scaffold includes prediction endpoints, batch prediction, readiness,
health, metrics, error envelopes, auth hooks and model metadata.</p>
</div>

<div class="portfolio-system-node" markdown="1">
<small>2. ML lifecycle</small>
<h3>Training to serving parity</h3>
<p>Feature engineering, schema validation, model loading and inference contracts
are treated as one path instead of separate notebook and API worlds.</p>
</div>

<div class="portfolio-system-node" markdown="1">
<small>3. Quality gates</small>
<h3>CI before adoption</h3>
<p>YAML checks, workflow checks, scaffold tests, smoke paths, pre-commit hooks
and targeted validations protect the generated service.</p>
</div>

<div class="portfolio-system-node" markdown="1">
<small>4. Runtime</small>
<h3>Docker and Kubernetes</h3>
<p>Containers, Kustomize overlays, readiness probes and deployment defaults are
part of the service contract from the beginning.</p>
</div>

<div class="portfolio-system-node" markdown="1">
<small>5. Observability</small>
<h3>Metrics and operations hooks</h3>
<p>Prometheus-compatible metrics, prediction logging, tracing options, drift
checks and retraining workflows are built into the template story.</p>
</div>

<div class="portfolio-system-node" markdown="1">
<small>6. Cloud path</small>
<h3>GCP and AWS patterns</h3>
<p>The template documents GKE/EKS deployment expectations, identity patterns,
artifact registries and operational runbooks without pretending local tests are
cloud proof.</p>
</div>
</div>

## Agentic Operating Model

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Canonical rules</small>
<h3>One source of truth</h3>
<p><code>AGENTS.md</code>, agent context and the manifest define the behavior contract.
Adapter files point to canonical rules instead of drifting into parallel policy.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Risk matrix</small>
<h3>AUTO / CONSULT / STOP</h3>
<p>Low-risk work can be automated, ambiguous production work requires user
consultation, and destructive or safety-sensitive actions must stop.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Workflow skills</small>
<h3>Repeatable MLOps actions</h3>
<p>New service creation, drift checks, retraining, rollback, cost review,
release, incident and security workflows are encoded as reusable agent skills.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Reviewability</small>
<h3>Agents leave evidence</h3>
<p>The model is designed around validation logs, changelogs, ADRs, runbooks and
explicit test commands so agent-assisted work remains auditable.</p>
</div>
</div>

## What A Reviewer Should Inspect

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>First scaffold</small>
<h3>Can it generate a usable service?</h3>
<p>A reviewer should be able to scaffold a service, run the local checks and
see a coherent FastAPI project with tests and deployment artifacts.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Serving contract</small>
<h3>Does inference match training?</h3>
<p>The service should preserve feature parity, validate inputs and expose
readiness based on model loading rather than a superficial health endpoint.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Governance contract</small>
<h3>Can agents act safely?</h3>
<p>The strongest technical signal is whether agent workflows are bounded by
rules, manifests, validations and explicit escalation points.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Cloud realism</small>
<h3>Are claims scoped honestly?</h3>
<p>The template distinguishes local validation from real GKE/EKS validation,
which keeps the documentation useful without overstating production proof.</p>
</div>
</div>

## What It Shows About Me

| Signal | What it means |
|--------|---------------|
| Product thinking | I turned portfolio lessons into a reusable starter system. |
| MLOps discipline | The template treats serving, testing, packaging and deployment as one system. |
| Governance mindset | AI-assisted engineering is bounded by explicit rules, not only prompts. |
| Operational honesty | Cloud validation, cost control and limitations are documented instead of hidden. |
| Documentation taste | The repo is designed so another engineer can adopt, review and improve it. |

## Where To Go Next

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Repository</small>
<h3><a href="https://github.com/DuqueOM/ML-MLOps-Production-Template">Template source</a></h3>
<p>Start here for the actual scaffold, docs, workflows, rules and release
history.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Adoption path</small>
<h3><a href="https://github.com/DuqueOM/ML-MLOps-Production-Template/blob/main/QUICK_START.md">Quick Start</a></h3>
<p>Best entry point for generating and validating a new service from the
template.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Decision trail</small>
<h3><a href="https://github.com/DuqueOM/ML-MLOps-Production-Template/tree/main/docs/decisions">Architecture decisions</a></h3>
<p>Review the trade-offs behind the template instead of only reading the final
structure.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Portfolio context</small>
<h3><a href="technical-evidence.md">Technical evidence</a></h3>
<p>See how the template relates to the broader monorepo, cloud evidence and
production ML portfolio.</p>
</div>
</div>

</div>
