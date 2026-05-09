# Projects Overview

<div class="portfolio-page" markdown="1">

<div class="portfolio-hero" markdown="1">
<span class="portfolio-eyebrow">Monorepo production evidence</span>

# One ML monorepo, three services, two cloud paths

This is not a collection of isolated notebooks. The portfolio is a monorepo
that turns three different ML problems into reviewable production systems:
model code, APIs or batch paths, Docker images, Kubernetes manifests,
multi-cloud deployment evidence, monitoring, CI/CD and documentation.

<div class="portfolio-actions" markdown="1">
[Watch the video demo](https://youtu.be/7dFFqq2ROPw){ .portfolio-button .portfolio-button--primary }
[Review technical evidence](../technical-evidence.md){ .portfolio-button }
[View deployment evidence](../DEPLOYMENT_EVIDENCE.md){ .portfolio-button }
</div>
</div>

<div class="portfolio-stat-strip" markdown="1">
<div class="portfolio-stat">
<small>Service modules</small>
<strong>3 ML systems</strong>
<span>Churn, financial NLP and taxi demand forecasting.</span>
</div>
<div class="portfolio-stat">
<small>Validation surface</small>
<strong>395+ tests</strong>
<span>Unit, integration, API, infra and smoke coverage.</span>
</div>
<div class="portfolio-stat">
<small>Deployment evidence</small>
<strong>GKE + EKS</strong>
<span>Real multi-cloud runtime evidence, now cost-controlled.</span>
</div>
<div class="portfolio-stat">
<small>Architecture record</small>
<strong>18 ADRs</strong>
<span>Decisions covering reliability, cost, security and scope.</span>
</div>
</div>

<div class="portfolio-media portfolio-media--demo" markdown="1">

<video autoplay muted loop playsinline controls preload="metadata" poster="../../media/videos/portfolio-demo-poster.jpg" aria-label="Portfolio demo showing the MLOps portfolio flow">
  <source src="../../media/videos/portfolio-demo-preview.webm" type="video/webm">
  <source src="../../media/videos/portfolio-demo-preview.mp4" type="video/mp4">
  <a href="https://youtu.be/7dFFqq2ROPw">Watch the portfolio video demo</a>
</video>

</div>

## How To Read The Portfolio

<div class="portfolio-split" markdown="1">
<div markdown="1">

The strongest signal is the system shape. Each project proves a different ML
problem, but the portfolio is meant to be reviewed as one end-to-end operating
environment: code, validation, serving, infrastructure, observability and
handoff documentation.

That matters because production ML is rarely just the model. The work is in
making the model testable, deployable, explainable and safe enough for another
person to operate.

</div>
<div class="portfolio-callout" markdown="1">
<strong>Recruiter takeaway</strong>

I can build ML work that is easier to review than a notebook-only project:
there is evidence of tests, deployment thinking, cloud operations and written
trade-offs.
</div>
</div>

## System View

<div class="portfolio-system-map" markdown="1">
<div class="portfolio-system-node" markdown="1">
<small>1. Data and features</small>
<h3>Leakage-aware inputs</h3>
<p>Temporal validation, cost-aware thresholds, text preprocessing and PySpark
ETL appear where the project needs them.</p>
</div>

<div class="portfolio-system-node" markdown="1">
<small>2. Model development</small>
<h3>Metrics with context</h3>
<p>AUC, accuracy, R2, explainability and dataset limitations are documented
instead of treated as one-line leaderboard numbers.</p>
</div>

<div class="portfolio-system-node" markdown="1">
<small>3. Serving and batch paths</small>
<h3>APIs beyond notebooks</h3>
<p>FastAPI, prediction contracts, smoke checks and batch-oriented paths make the
models callable and reviewable.</p>
</div>

<div class="portfolio-system-node" markdown="1">
<small>4. Runtime packaging</small>
<h3>Docker and Kubernetes</h3>
<p>Each service has runtime artifacts that can be built, scanned, deployed and
debugged outside a local notebook.</p>
</div>

<div class="portfolio-system-node" markdown="1">
<small>5. Cloud evidence</small>
<h3>GCP and AWS</h3>
<p>The portfolio includes GKE and EKS evidence, Artifact Registry/ECR paths,
storage buckets and deployment screenshots.</p>
</div>

<div class="portfolio-system-node" markdown="1">
<small>6. Operations and handoff</small>
<h3>Monitoring, ADRs and runbooks</h3>
<p>Prometheus/Grafana, MLflow evidence, troubleshooting notes and architecture
decisions make the system easier to operate.</p>
</div>
</div>

## Service Modules

<div class="portfolio-project-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Banking churn service</small>
<h3><a href="../bankchurn/">BankChurn Predictor</a></h3>
<p>Predicts customer churn and connects model performance to cost-aware
threshold tuning, SHAP explanations and serving reliability improvements.</p>
<p><strong>Main signal:</strong> AUC 0.87, 90% test coverage and documented
FastAPI/Kubernetes hardening.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Financial NLP service</small>
<h3><a href="../nlpinsight/">NLPInsight Analyzer</a></h3>
<p>Classifies sentiment in financial text with a lightweight production path,
an optional transformer path and explicit dataset trade-off documentation.</p>
<p><strong>Main signal:</strong> 80.6% accuracy, 98% coverage and an honest
modeling path over an easier benchmark.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Demand forecasting pipeline</small>
<h3><a href="../chicagotaxi/">ChicagoTaxi Pipeline</a></h3>
<p>Forecasts taxi demand from trip data using PySpark ETL, temporal validation
and leakage-aware feature engineering.</p>
<p><strong>Main signal:</strong> R2 0.96, 6.3M rows processed and leakage removed
from the feature set.</p>
</div>
</div>

## Project Decision Snapshot

<div class="portfolio-project-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>BankChurn Predictor</small>
<h3>Cost-aware churn decisions</h3>
<p><strong>Business impact:</strong> the threshold favors catching likely
churners because a missed churner is much more expensive than an unnecessary
retention offer.</p>
<p><strong>Key engineering decision:</strong> serve the model through a tested
FastAPI path and move CPU-bound inference away from the async event loop.</p>
<p><strong>Improve next:</strong> add request tracing and fresher traffic-backed
monitoring screenshots.</p>

[Read debugging deep dive](bankchurn-debugging.md){ .portfolio-button }
</div>

<div class="portfolio-card" markdown="1">
<small>NLPInsight Analyzer</small>
<h3>Low-cost financial sentiment</h3>
<p><strong>Business impact:</strong> the system is optimized for explainable,
low-cost inference rather than chasing a heavier model that would be harder to
operate.</p>
<p><strong>Key engineering decision:</strong> keep a lightweight baseline and
document the transformer path as an intentional trade-off, not an omission.</p>
<p><strong>Improve next:</strong> add richer domain evaluation and compare
latency/cost against a small transformer model.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>ChicagoTaxi Pipeline</small>
<h3>Forecasting with temporal discipline</h3>
<p><strong>Business impact:</strong> demand forecasting is useful only if the
pipeline avoids leakage and can scale beyond a small notebook sample.</p>
<p><strong>Key engineering decision:</strong> use PySpark and temporal
validation to process high-volume trip data with realistic forecasting rules.</p>
<p><strong>Improve next:</strong> add scheduled batch scoring and a dashboard
that compares forecast drift over time.</p>
</div>
</div>

## Monorepo Depth

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Shared production pattern</small>
<h3>Repeated operating shape</h3>
<p>The services are different ML problems, but they converge on the same
production questions: testing, packaging, runtime health and deployability.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Multi-cloud proof</small>
<h3>GKE and EKS were exercised</h3>
<p>The cloud environments are not running now for cost reasons, but the repo
keeps screenshots, CLI evidence, manifests and comparison notes.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>CI/CD discipline</small>
<h3>Checks before claims</h3>
<p>The portfolio includes automated tests, documentation validation, security
scanning, Docker validation and quality gates.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Template extraction</small>
<h3>Lessons became reusable</h3>
<p>The production patterns were extracted into the ML-MLOps Production Template,
which is the strongest proof of product thinking in the portfolio.</p>
</div>
</div>

## What This Proves

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>For recruiters</small>
<h3>More than training models</h3>
<p>The portfolio shows a candidate who can explain systems, not just model
scores: cloud, testing, reliability, documentation and cost trade-offs.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>For technical reviewers</small>
<h3>Evidence is inspectable</h3>
<p>There are source files, tests, screenshots, ADRs, API references, deployment
notes and operational docs to review independently.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>For team fit</small>
<h3>Junior scope, production habits</h3>
<p>I am not claiming years of ML platform ownership. I am showing that I can
learn quickly, build carefully and work inside real engineering constraints.</p>
</div>
</div>

## Deeper Evidence

- [Technical Evidence](../technical-evidence.md)
- [Architecture decisions](../architecture/decisions.md)
- [Multi-cloud deployment evidence](../DEPLOYMENT_EVIDENCE.md)
- [Portfolio status](../PORTFOLIO_STATUS.md)
- [Production template](../template.md)

</div>
