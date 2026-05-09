# Technical Evidence

<div class="portfolio-page" markdown="1">

<div class="portfolio-hero" markdown="1">
<span class="portfolio-eyebrow">Reviewer evidence</span>

# Technical evidence without the wall of links

This page is the short version. It is designed for a reviewer who wants to know
what was actually built without being dropped into every ADR, API reference and
deployment note at once.

Use it as a map: start with the summary, choose one review path, and open the
deep dive only if you want the full technical archive.

<div class="portfolio-actions" markdown="1">
[Open deep dive index](technical-deep-dive.md){ .portfolio-button .portfolio-button--primary }
[Check current status](PORTFOLIO_STATUS.md){ .portfolio-button }
[Review projects](projects/overview.md){ .portfolio-button }
</div>
</div>

## Quick Technical Signal

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>System scope</small>
<h3>Three ML services beyond notebooks</h3>
<p>Churn prediction, financial sentiment analysis and taxi demand forecasting
with APIs, tests, packaging and documentation.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>MLOps fundamentals</small>
<h3>Serving, tracking and deployment paths</h3>
<p>FastAPI, Docker, Kubernetes manifests, MLflow patterns, CI/CD workflows and
cloud deployment evidence.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Reliability habits</small>
<h3>Measured failures, not just demos</h3>
<p>Load-test debugging, SHAP troubleshooting, HPA correction, leakage checks and
architecture decisions with trade-offs.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Business judgment</small>
<h3>Cost and scope are documented</h3>
<p>The portfolio separates active assets from paused cloud runtime and explains
cost-control decisions honestly.</p>
</div>
</div>

## Choose A Review Path

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>3-minute review</small>
<h3>Recruiter or first screen</h3>
<p>Confirm the role fit, current status and what the portfolio is meant to show.</p>

[Recruiter brief](recruiter-brief.md){ .portfolio-button }
[Portfolio status](PORTFOLIO_STATUS.md){ .portfolio-button }
</div>

<div class="portfolio-card" markdown="1">
<small>10-minute review</small>
<h3>Hiring manager overview</h3>
<p>Understand the three services, the reusable template and the strongest
technical signals without reading the whole archive.</p>

[Projects overview](projects/overview.md){ .portfolio-button }
[Production template](template.md){ .portfolio-button }
</div>

<div class="portfolio-card" markdown="1">
<small>30-minute review</small>
<h3>Technical deep dive</h3>
<p>Open architecture, deployment, operations, model and API documentation in a
grouped index instead of a long sidebar.</p>

[Deep dive index](technical-deep-dive.md){ .portfolio-button }
</div>
</div>

## Failure Stories

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Serving failure</small>
<h3>81% API errors under load</h3>
<p>The strongest signal is the diagnosis habit: the fix was not to blindly add
resources, but to isolate a blocked inference path and verify the correction
with load testing.</p>

[Read deep dive](projects/bankchurn-debugging.md){ .portfolio-button .portfolio-button--primary }
</div>

<div class="portfolio-card" markdown="1">
<small>Explainability issue</small>
<h3>All-zero SHAP outputs</h3>
<p>The portfolio documents why explainability must match the actual model
structure and feature space, not only use the most familiar SHAP class.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Scaling issue</small>
<h3>HPA that could not scale down</h3>
<p>Memory-based autoscaling was rejected for ML pods because fixed model memory
creates a misleading signal. CPU became the clearer scaling input.</p>
</div>
</div>

## Key Engineering Decisions

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Serving</small>
<h3>One worker per pod plus executor</h3>
<p>Kubernetes handles horizontal scaling; the API keeps the event loop free by
offloading CPU-bound inference work.</p>

[ADR-014](decisions/014-single-worker-pod-ml-inference.md){ .portfolio-button }
[ADR-015](decisions/015-async-inference-threadpool.md){ .portfolio-button }
</div>

<div class="portfolio-card" markdown="1">
<small>Cost control</small>
<h3>Cloud evidence, not always-on waste</h3>
<p>The portfolio preserves deployment proof while pausing live clusters when
the monthly cost is not justified for a public showcase.</p>

[Portfolio status](PORTFOLIO_STATUS.md){ .portfolio-button }
</div>

<div class="portfolio-card" markdown="1">
<small>Template extraction</small>
<h3>Lessons became guardrails</h3>
<p>The reusable template turns repeated failure modes into documented defaults,
rules and reviewable workflows.</p>

[Production template](template.md){ .portfolio-button }
</div>
</div>

## Evidence Highlights

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Serving</small>
<h3>FastAPI inference paths</h3>
<p>Health checks, metrics endpoints, Swagger docs, Docker builds and API smoke
tests make models callable and reviewable.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Cloud</small>
<h3>GKE and EKS evidence</h3>
<p>Kubernetes manifests, Terraform examples, screenshots and CLI evidence
preserve the deployment story while runtime is paused for cost.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Operations</small>
<h3>Monitoring and runbooks</h3>
<p>Prometheus, Grafana, MLflow, load tests and troubleshooting notes show how
the system would be operated, not only trained.</p>
</div>
</div>

## Deep Archive

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<h3><a href="projects/overview.md">Projects overview</a></h3>
<p>The three ML systems and their main results.</p>
</div>

<div class="portfolio-card" markdown="1">
<h3><a href="projects/bankchurn-debugging.md">BankChurn debugging deep dive</a></h3>
<p>The full failure story: symptoms, hypotheses, root cause, fix, validation
and template lesson.</p>
</div>

<div class="portfolio-card" markdown="1">
<h3><a href="template.md">Production template</a></h3>
<p>The reusable MLOps project extracted from portfolio lessons.</p>
</div>

<div class="portfolio-card" markdown="1">
<h3><a href="technical-deep-dive.md">Deep dive index</a></h3>
<p>Grouped technical archive for architecture, deployment, operations, models
and API references.</p>
</div>

<div class="portfolio-card" markdown="1">
<h3><a href="PORTFOLIO_STATUS.md">Portfolio status</a></h3>
<p>What is active now, what is paused, and how to reactivate a live demo.</p>
</div>
</div>

</div>
