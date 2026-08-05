# agent-local — The LLM Plane

<div class="portfolio-page portfolio-template" markdown="1">

<div class="portfolio-hero" markdown="1">
<canvas data-neural-scene="cube" aria-hidden="true"></canvas>
<span class="portfolio-eyebrow">Local, multi-tier LLM agent platform</span>

# The template's governance philosophy, generalized to a domain it was never written for

[**agent-local**](https://github.com/DuqueOM/agent-local) is a sibling of
the [ML Service Template](template.md), not a fork of it — a
reusable platform (`core/` + thin `usecases/<name>/` domains) for
local, multi-tier LLM agents. It reuses the template's Terraform and
Kustomize when it needs cloud, and runs the template's day-2 maintenance
discipline (drift checks, retraining-equivalent eval gates, CI hardening)
against its own local model tiers instead of a tabular ML model. The
shared plan lives in the template's
[`ACTION_PLAN_LLM_AGENT.md`](https://github.com/DuqueOM/ml-service-template/blob/main/docs/audit/ACTION_PLAN_LLM_AGENT.md).

<div class="portfolio-actions" markdown="1">
[Open the agent-local repo](https://github.com/DuqueOM/agent-local){ .portfolio-button .portfolio-button--primary }
[Read the README](https://github.com/DuqueOM/agent-local/blob/main/README.md){ .portfolio-button }
[Compare all three repos](related-projects.md){ .portfolio-button }
</div>
</div>

<div class="portfolio-stat-strip" markdown="1">
<div class="portfolio-stat">
<small>Architecture</small>
<strong>Multi-tier, local-first</strong>
<span>Grammar-constrained routing picks the smallest model tier that can do the job.</span>
</div>
<div class="portfolio-stat">
<small>Safety model</small>
<strong>Deterministic policy gate</strong>
<span>Versioned YAML policy, checked before a user ever sees a response — never model self-judgment.</span>
</div>
<div class="portfolio-stat">
<small>Evidence isolation</small>
<strong>ADR-009</strong>
<span>Reflection notes go to their own channel — structurally unreachable by the policy gate or verifier.</span>
</div>
<div class="portfolio-stat">
<small>Autonomy gate</small>
<strong>11 adversarial eval sets</strong>
<span>Offline gate proves a "successfully fooled" model still can't get a policy-violating response past the gate.</span>
</div>
<div class="portfolio-stat">
<small>Interop discipline</small>
<strong>MCP/A2A rejected (ADR-010)</strong>
<span>A precise technical conflict, written down with the exact evidence that would reverse it.</span>
</div>
<div class="portfolio-stat">
<small>Security mapping</small>
<strong>OWASP LLM Top-10 (2025)</strong>
<span>Every category — prompt injection to unbounded consumption — mapped to a concrete control.</span>
</div>
</div>

## How To Read This Project

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Recruiter view</small>
<h3>Governance that generalizes, not a one-off</h3>
<p>The signal isn't "another LLM agent demo" — it's that the same
AUTO/CONSULT/STOP, contract-tested governance model from the ML template
was ported to a completely different domain and held.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Technical lead view</small>
<h3>Inspect the policy/evidence separation</h3>
<p>The strongest engineering claim is ADR-009: reflection is structurally
isolated from verifier-visible evidence. Read the ADR, then read the
eval set that proves it.</p>
</div>

<div class="portfolio-team-view portfolio-card" markdown="1">
<small>Platform adoption view</small>
<h3>Can a new use-case be added without forking core?</h3>
<p>A new domain is a thin `usecases/<name>/` folder — the safety-critical
loop, routing, and policy gate live once in `core/` and are never
duplicated per use-case.</p>
</div>
</div>

## Why This Exists

<div class="portfolio-split" markdown="1">
<div markdown="1">

Most "LLM agent" code couples the loop, prompts and business rules into
one application. That doesn't scale past a single use-case: the
safety-critical logic diverges across copies the moment a second
use-case needs a tweak, and nobody can tell which copy is the one that's
actually safe. `agent-local` centralizes that logic in `core/` and
consumes it from configuration — a new domain (the shipped example is a
WhatsApp store assistant) is a `usecases/<name>/` folder, never a fork.

</div>
<div class="portfolio-callout" markdown="1">
<strong>Technical reviewer signal</strong>

The 7-station reasoning loop runs at **adaptive depth** — smalltalk skips
reflection and critique entirely, so the safety machinery's cost is paid
only when the task actually warrants it. Autonomy is earned per-tier via
eval gates, not assumed at framework-adoption time.
</div>
</div>

## What Makes It Distinctive

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Policy gate</small>
<h3>Deterministic, not model judgment</h3>
<p>Every response is checked against versioned YAML policies before it
reaches a user. The gate never trusts model-authored text as evidence —
policy-as-data, the same discipline the template applies to quality
gates.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Evidence isolation</small>
<h3><a href="https://github.com/DuqueOM/agent-local/blob/main/docs/decisions">Reflection ≠ evidence (ADR-009)</a></h3>
<p>A model's internal reflection notes go to their own channel, consumed
only by the final response generator — structurally prevented from being
read as tool evidence by the policy gate or verifier. Closes a class of
self-fabricated-evidence attack rather than just discouraging it.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Interoperability discipline</small>
<h3>MCP/A2A evaluated and rejected (ADR-010)</h3>
<p>The trendy interoperability standards were assessed against the
platform's fail-closed tool-capability contract and declined on a precise
conflict: MCP's capability hints are explicitly "untrusted unless from a
trusted server," while this contract requires registry-verified
capability. Written down with the exact evidence that would reverse it —
not a permanent no.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Eval-gated autonomy</small>
<h3>11 adversarial sets + offline gate</h3>
<p>Including a dedicated injection-containment set and full-loop tests
proving a model that gets "successfully fooled" still can't push a
policy-violating response past the deterministic gate. Autonomy expands
only when the gate proves it's safe to.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Security mapping</small>
<h3>OWASP LLM Top-10 (2025)</h3>
<p>A dedicated security model document maps the platform's controls to
each of the ten categories, from prompt injection to unbounded
consumption — not a generic "we take security seriously" paragraph.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Shared governance, not a copy</small>
<h3>Same AUTO/CONSULT/STOP contract</h3>
<p>Inherits the ML template's behavior protocol and contract-testing
discipline rather than inventing a bespoke, one-off safety story per
project — the generalization itself is the evidence the philosophy
travels.</p>
</div>
</div>

## How It Compares

<div class="portfolio-split" markdown="1">
<div markdown="1">

The local/multi-tier LLM agent space has real, capable alternatives.
None of them make the same trade-off this platform does: earning
autonomy through eval gates before granting it, with policy enforcement
that doesn't depend on trusting the model's own account of itself.

</div>
<div class="portfolio-callout" markdown="1">
<strong>The honest version</strong>

This is a platform for teams that want a genuinely local, tiered agent
with a deterministic safety gate — not a managed cloud-agent product,
and not a framework optimized for maximum autonomy or ecosystem breadth.
</div>
</div>

| Alternative | Strong at | What this platform adds |
|---|---|---|
| **LangChain / LangGraph** | The largest ecosystem, very flexible graph-based orchestration, huge integration surface | Guardrails are typically callbacks/prompt-level checks — advisory, not a structurally separate deterministic gate. Reflection and tool evidence aren't isolated by contract; local multi-tier routing is left to the integrator to build. |
| **AutoGPT-style autonomous agents** | Explicit optimization for capability and autonomy, minimal friction to "just let it run" | No eval-gated autonomy model — capability isn't earned against an adversarial test suite before being granted. No structural separation between a model's self-reflection and what the policy layer treats as evidence. |
| **CrewAI** | Strong multi-agent role/collaboration orchestration | Safety still lives in role prompting and conventions, not a versioned-policy-as-data gate independent of any agent's output. Closer to a BMAD-style persona model than a governance-first platform. |
| **OpenAI Assistants API / managed cloud-agent platforms** | Fully managed, minimal ops burden, deep vendor integration | Cloud-locked by design — no local story, and policy enforcement lives inside the vendor's black box, unauditable and unversioned in your own repo. |
| **Bare Ollama + a wrapper script** | The common DIY path to "a local LLM agent"; minimal setup | Exactly what this platform replaces: no tiering discipline, no policy-as-data, no eval-gated autonomy, no telemetry-as-contract — just a script calling a model with no safety architecture underneath it. |

## What It Shows About Me

| Signal | What it means |
|--------|---------------|
| Systems thinking beyond one domain | The same governance philosophy generalizes from tabular ML serving to LLM agents without being reinvented. |
| Security-first LLM engineering | Reflection/evidence isolation and an OWASP LLM Top-10 mapping are structural, not aspirational. |
| Disciplined interoperability judgment | MCP/A2A were evaluated and rejected with written, reversible reasoning — not adopted by default or dismissed without looking. |
| Autonomy calibration | Capability expands only behind an adversarial eval gate, matching the template's own "evidence before promotion" quality-gate philosophy. |

## Where To Go Next

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Repository</small>
<h3><a href="https://github.com/DuqueOM/agent-local">agent-local source</a></h3>
<p>Start here for `core/`, `usecases/`, the ADRs and the eval harness.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Decision trail</small>
<h3><a href="https://github.com/DuqueOM/agent-local/tree/main/docs/decisions">Architecture decisions</a></h3>
<p>ADR-009 (reflection isolation) and ADR-010 (MCP/A2A rejection) are the
two most load-bearing reads.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Sibling project</small>
<h3><a href="template.md">The production template</a></h3>
<p>See the governance philosophy this platform generalizes, in its
original tabular-ML-serving context.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Portfolio context</small>
<h3><a href="related-projects.md">How all three repos relate</a></h3>
<p>The full lineage: portfolio → template → agent-local, and which one to
look at for what.</p>
</div>
</div>

</div>
