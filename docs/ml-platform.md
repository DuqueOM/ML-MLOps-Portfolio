# ML Platform

<div class="portfolio-page portfolio-template" markdown="1">

<div class="portfolio-hero" markdown="1">
<canvas data-neural-scene="cube" aria-hidden="true"></canvas>
<span class="portfolio-eyebrow">Enterprise multi-project ML platform · monorepo</span>

# The second template — where a single service stops being the unit of reuse

[**ml-platform**](https://github.com/DuqueOM/ml-platform) is a multi-project
ML platform monorepo: one shared substrate — data, features, serving,
observability, governance, agentic tooling — reused across projects that
differ in **kind**, not merely in dataset. Tabular ML, time series, deep
learning, LLM/RAG and agents, on GCP and AWS.

It is the **second template in this lineage, not a successor to the first**.
[`ml-service-template`](template.md) scaffolds *one governed tabular service*
and is deliberately small enough to read in an afternoon. `ml-platform` covers
the work that sits *above* that boundary — point-in-time feature retrieval,
lakehouse table formats, orchestration with lineage, GitOps reconciliation,
LLM systems with evaluation gates, and governance artifacts written for an
auditor rather than a reviewer. It **consumes** the first template through
`copier` rather than replacing it
([ADR-003](https://github.com/DuqueOM/ml-platform/blob/main/docs/decisions/ADR-003-service-template-consumption.md)).

<div class="portfolio-actions" markdown="1">
[Open the ml-platform repo](https://github.com/DuqueOM/ml-platform){ .portfolio-button .portfolio-button--primary }
[Read the charter (ADR-000)](https://github.com/DuqueOM/ml-platform/blob/main/docs/decisions/ADR-000-charter-and-scope.md){ .portfolio-button }
[Compare both templates](related-projects.md){ .portfolio-button }
</div>
</div>

<div class="portfolio-stat-strip" markdown="1">
<div class="portfolio-stat">
<small>Unit of reuse</small>
<strong>Library + running service</strong>
<span>Consumed in-repo by projects — not scaffolding to be copied out.</span>
</div>
<div class="portfolio-stat">
<small>Problem shapes</small>
<strong>Tabular · TS · LLM · agents</strong>
<span>Diversity is the point: a substrate serving one shape is not a substrate.</span>
</div>
<div class="portfolio-stat">
<small>Build state</small>
<strong>48 of 55 components</strong>
<span>48 done · 2 partial · 5 absent — derived from the filesystem, not hand-maintained.</span>
</div>
<div class="portfolio-stat">
<small>Evidence depth</small>
<strong>37 L1 · 11 L2 · 0 L4</strong>
<span>No cloud rollout claimed, because none has happened. The top row is printed at zero on purpose.</span>
</div>
<div class="portfolio-stat">
<small>Governance</small>
<strong>10 ADRs · claim → gate</strong>
<span>Every published quality claim maps to a command that can fail a build.</span>
</div>
<div class="portfolio-stat">
<small>Agentic surface</small>
<strong>23 rules · 29 skills · 22 workflows</strong>
<span>Canonical store, four tool surfaces regenerated from it — never hand-edited.</span>
</div>
</div>

## The Two Templates Are Not The Same Tool

Both are multi-cloud and both are governed by ADRs. They answer different
questions, and the boundary between them is itself a written decision
([ADR-000](https://github.com/DuqueOM/ml-platform/blob/main/docs/decisions/ADR-000-charter-and-scope.md)).

| | [`ml-service-template`](template.md) | [`ml-platform`](https://github.com/DuqueOM/ml-platform) |
| --- | --- | --- |
| **Question it answers** | "I need **one** governed ML service in production" | "I need a **substrate** several unlike ML projects sit on" |
| **Unit of reuse** | A scaffold you copy out and own | A library plus a running service, consumed in-repo |
| **Model kinds** | Tabular / classical ML only — a stated limit, not an omission | Tabular · time series · deep learning · LLM/RAG · agents |
| **Data layer** | In-memory DataFrames, Pandera validation | Iceberg lakehouse, BigLake / S3 Tables, DuckDB + Polars, dbt, point-in-time joins with a leakage detector |
| **Orchestration** | CronJob + GitHub Actions — calibrated for 2–3 models | Airflow 3 + KFP v2, Vertex AI Pipelines and SageMaker Pipelines |
| **Deployment** | `kubectl apply` through governed GitHub Actions | GitOps: ArgoCD + ApplicationSets + Argo Rollouts |
| **Observability** | Prometheus + Grafana + Evidently | OpenTelemetry + Grafana LGTM (Loki · Tempo · Mimir) + Jaeger |
| **Drift** | PSI with quantile bins, one tabular detector | Four detectors for four project kinds, one shared contract ([ADR-007](https://github.com/DuqueOM/ml-platform/blob/main/docs/decisions/ADR-007-drift-detection-per-project-kind.md)) |
| **LLM / GenAI** | out of scope by decision | LiteLLM, prompt registry, semantic cache, guardrails, Langfuse, promptfoo eval gates |
| **Anti-pattern model** | 38 encoded anti-patterns (D-01→D-38) + 8 audit-standard (Q-01→Q-08) | Technology triage: every tool tiered core / demonstrated / studied / **rejected**, with the reason |
| **Entry cost** | Minutes — `copier copy`, one service | Hours — a monorepo with a six-stage progression |
| **Read it in** | An afternoon | Not in an afternoon, and that is the trade |

The honest summary: **if you have one model to ship, the first template is the
right answer and the second is over-engineering.** The second earns its
complexity only once several projects of different kinds need to share
substrate — which is exactly the claim it puts on record to be falsified.

## The Claim, Written To Be Falsified

A platform's central claim is that shared substrate makes each additional
project cheaper. That claim is untestable with one project, so it is written
down as a criterion with a test attached:

> **C1** — a second project reuses ≥3 shared libraries with no fork, verified
> by a dependency-graph test in CI.

If C1 fails, this is a monorepo of unrelated projects and the platform claim is
false. C1 is first testable at Phase 3 — deliberately early, while reversing
the decision is still cheap.

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Recruiter view</small>
<h3>Scope discipline, demonstrated twice</h3>
<p>Two templates exist because one of them refused to grow. Knowing which
problems a tool should <em>not</em> absorb is the judgment this pair is
evidence for.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Technical lead view</small>
<h3>Claims that can fail a build</h3>
<p>The claim → gate mapping in <code>docs/governance/quality-gates.md</code> is
itself checked for gaps. A measured number that cannot fail anything is
decoration.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Platform view</small>
<h3>Layers, so libs cannot import projects</h3>
<p><code>libs/</code> never imports <code>projects/</code>, projects never
import each other — enforced by a test rather than by review discipline.</p>
</div>
</div>

## Evidence Layers — What A Green Tick Is Allowed To Mean

The repository's build state is generated from the filesystem by
`scripts/check_implementation_status.py`, never maintained by hand, because a
status table a human maintains will drift. Each component also carries the
**layer** its evidence reaches:

| Layer | What it proves | Count |
| :-- | --- | :-: |
| **L1** | Contract — the test suite passes | 37 |
| **L2** | Component — the generator renders, the gate runs, the build completes | 11 |
| **L3** | Cluster — it starts and answers in `kind` | 4 available, not run in CI |
| **L4** | Cloud — a real rollout on GKE or EKS | **0** |

L4 is printed at zero on purpose. That taxonomy exists because of a measured
failure in this very repository: six Kubernetes overlays rendered green for
weeks while their probes pointed at routes the service does not serve, so no
pod could ever have reached Ready. A suite passing and a pod answering are not
the same claim.

**No cloud deployment is claimed here because none has happened.** The order is
a constraint the maintainer set explicitly: local validation precedes cloud, and
the first cloud deployment in this lineage is `ml-service-template`'s, not this
repository's.

## What Is Built, And What Is Absent

<div class="portfolio-split" markdown="1">
<div markdown="1">

**Shared libraries** — `ml-core` (drift contract, fairness metrics),
`data-contracts` (versioned contracts with an explicit compatibility rule),
`feature-defs` (point-in-time joins plus a leakage detector), `llm-core`
(prompt registry, semantic cache, guardrails), `serving-core` (deliberately
near-empty, and the emptiness is *declared* and tested — one consumer does not
justify a library).

**Projects built** — `demand-forecast` (time series, Iceberg ingestion,
panel-aware temporal splitting, expanding-window backtesting),
`rag-assistant` (LLM/retrieval, provider-fingerprint and cost-per-request
drift), `store-assistant` (agents, trajectory drift, deterministic policy
gate).

**Projects absent** — `credit-risk`, `doc-intelligence`, `agent-ops`. Marked
⬜ in the status table, which means *absent*, not *planned*.

</div>
<div markdown="1">

**Drift, per project kind** — the inherited machinery was built for one kind,
a tabular service. Four kinds get four detectors on one shared contract: PSI
with quantile bins for tabular, embedding-space drift for documents,
recall-on-frozen-eval-set for retrieval, and tool-use/escalation/policy-gate
rejection rates for agents. Plus the failure most easily missed — a provider
silently changing the model behind a version alias, where evals degrade with
zero code, data or deploy change.

**Measurement honesty as a shipped artifact** — a semantic retrieval index was
built, evaluated against the lexical baseline, tied it (both 15.4% recall@5),
failed to clear the 0.05 margin, and **no index ships**. The number, the
diagnosis and what would reverse the decision are published anyway.

</div>
</div>

## Why It Absorbed — And Did Not Replace — `agent-local`

The LLM and agent track named in the charter was already substantially built in
[`agent-local`](agent-local.md): a grammar-constrained Tier-0 router, a
deterministic policy gate whose rules are versioned data, a fail-closed tool
capability contract, cross-tier verification and an OWASP-LLM-mapped threat
model.

`ml-platform` vendored that work in with its git history
([ADR-002](https://github.com/DuqueOM/ml-platform/blob/main/docs/decisions/ADR-002-absorbing-agent-local.md)) —
`core/` became `libs/llm-core/`, the `tienda` use-case became
`projects/store-assistant/` — because cross-repository coordination costs two
CI configurations, two changelogs and two ADR sets, and a third participant
makes that cost superlinear.

The standalone repository **stays live**, because its value is not the same
value. `ml-platform` gives that core one particular, governed use inside a
platform; `agent-local` remains the business-agnostic upstream for anyone who
wants the agent core without the platform around it.

## Code Review Shortcuts

<div class="portfolio-actions" markdown="1">
[Charter — what it refuses to be (ADR-000)](https://github.com/DuqueOM/ml-platform/blob/main/docs/decisions/ADR-000-charter-and-scope.md){ .portfolio-button .portfolio-button--primary }
[Monorepo topology (ADR-001)](https://github.com/DuqueOM/ml-platform/blob/main/docs/decisions/ADR-001-monorepo-topology.md){ .portfolio-button }
[Consume, never reimplement (ADR-003)](https://github.com/DuqueOM/ml-platform/blob/main/docs/decisions/ADR-003-service-template-consumption.md){ .portfolio-button }
[Tooling triage (ADR-004)](https://github.com/DuqueOM/ml-platform/blob/main/docs/decisions/ADR-004-tooling-triage.md){ .portfolio-button }
[Drift per project kind (ADR-007)](https://github.com/DuqueOM/ml-platform/blob/main/docs/decisions/ADR-007-drift-detection-per-project-kind.md){ .portfolio-button }
[Implementation status (generated)](https://github.com/DuqueOM/ml-platform/blob/main/docs/architecture/implementation-status.md){ .portfolio-button }
[Quality gates — claim → gate](https://github.com/DuqueOM/ml-platform/blob/main/docs/governance/quality-gates.md){ .portfolio-button }
[Technology inventory](https://github.com/DuqueOM/ml-platform/blob/main/docs/architecture/technology-inventory.yaml){ .portfolio-button }
[Six-stage progression](https://github.com/DuqueOM/ml-platform/blob/main/docs/PROGRESSION.md){ .portfolio-button }
</div>

## Where It Sits In The Line

```text
ML-MLOps-Portfolio        three services, three incidents — where the lessons were paid for
        │
        ├──▶ ml-service-template     one governed tabular service · read it in an afternoon
        │            │
        │            │  consumed via copier (ADR-003), never forked
        │            ▼
        └──▶ ml-platform             the substrate several unlike projects share
                     ▲
                     │  agent core vendored with history (ADR-002)
                     │
                agent-local          business-agnostic LLM agent core, still standalone
```

<div class="portfolio-actions" markdown="1">
[Compare all four repositories](related-projects.md){ .portfolio-button .portfolio-button--primary }
[The first template](template.md){ .portfolio-button }
[The agent core](agent-local.md){ .portfolio-button }
</div>

</div>
