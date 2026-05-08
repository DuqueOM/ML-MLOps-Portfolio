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

## What This Proves In One Minute

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

## Strongest Technical Signal

<div class="portfolio-split" markdown="1">
<div markdown="1">

One of the strongest signals in the portfolio is not a tool choice; it is the
debugging habit.

During load testing, an ML API reached an **81% error rate**. The fix was not to
blindly add resources. I traced the failure to the serving pattern, changed the
inference execution model, and verified the result with a new test. The error
rate dropped to **0%**.

</div>
<div class="portfolio-callout" markdown="1">
<strong>Reliability lesson</strong>

Measure first, isolate the cause, make the smallest meaningful fix, then
document the lesson so the next system is better.
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

## What To Open Next

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<h3><a href="../projects/overview/">Projects overview</a></h3>
<p>The three ML systems and their main results.</p>
</div>

<div class="portfolio-card" markdown="1">
<h3><a href="../template/">Production template</a></h3>
<p>The reusable MLOps project extracted from portfolio lessons.</p>
</div>

<div class="portfolio-card" markdown="1">
<h3><a href="../technical-deep-dive/">Deep dive index</a></h3>
<p>Grouped technical archive for architecture, deployment, operations, models
and API references.</p>
</div>

<div class="portfolio-card" markdown="1">
<h3><a href="../PORTFOLIO_STATUS/">Portfolio status</a></h3>
<p>What is active now, what is paused, and how to reactivate a live demo.</p>
</div>
</div>

</div>
