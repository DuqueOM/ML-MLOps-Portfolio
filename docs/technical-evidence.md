# Technical Evidence

<div class="portfolio-page" markdown="1">

<div class="portfolio-hero" markdown="1">
<span class="portfolio-eyebrow">Reviewer evidence</span>

# The proof behind the portfolio story

This page is for hiring managers and technical reviewers who want to quickly
understand what is implemented, what was deployed, and where the deeper evidence
lives.
</div>

## Evidence Map

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>ML services</small>
<h3>Three production-shaped projects</h3>
<p>Churn prediction, financial sentiment analysis and taxi demand forecasting.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Serving</small>
<h3>FastAPI and Docker</h3>
<p>APIs with health checks, metrics endpoints, Swagger docs and containerized
runtime paths.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>MLOps</small>
<h3>Tracking and retraining patterns</h3>
<p>MLflow, model versioning, DVC, drift detection and retraining hooks.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Cloud</small>
<h3>Multi-cloud deployment artifacts</h3>
<p>Kubernetes manifests and Terraform examples for GCP and AWS, with live
deployment evidence preserved.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>CI/CD</small>
<h3>Automated quality gates</h3>
<p>GitHub Actions pipelines with tests, security checks, Docker builds and
deployment workflows.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Operations</small>
<h3>Monitoring and runbooks</h3>
<p>Prometheus, Grafana, load tests, API metrics, status docs and troubleshooting
guides.</p>
</div>
</div>

## Debugging And Reliability

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

Other documented lessons include:

- SHAP explanations returning zero values because the wrong explainer was used
  for the model architecture.
- Memory-based autoscaling being a poor signal for ML services with a fixed
  memory footprint.
- A forecasting project where leakage had to be identified and removed before
  the metric could be trusted.

## Cost And Business Judgment

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Cost awareness</small>
<h3>Cloud choices are not neutral</h3>
<p>The portfolio compares cloud deployments that meet the service goal but have
different monthly cost profiles.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Scope control</small>
<h3>Right-size the platform</h3>
<p>The goal is not to build every possible tool; it is to choose what creates
evidence, reliability and maintainability.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Communication</small>
<h3>Trade-offs are written down</h3>
<p>Architecture decisions and runbooks make the reasoning inspectable by a
reviewer.</p>
</div>
</div>

## Important Links

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<h3><a href="projects/overview/">Projects overview</a></h3>
<p>The three ML systems and their main results.</p>
</div>

<div class="portfolio-card" markdown="1">
<h3><a href="architecture/overview/">Architecture overview</a></h3>
<p>How services, data, CI/CD and cloud pieces fit together.</p>
</div>

<div class="portfolio-card" markdown="1">
<h3><a href="architecture/decisions/">Decision records</a></h3>
<p>Why the portfolio made specific production and platform trade-offs.</p>
</div>

<div class="portfolio-card" markdown="1">
<h3><a href="DEPLOYMENT_EVIDENCE/">Deployment evidence</a></h3>
<p>Preserved proof from the live cloud deployment period.</p>
</div>

<div class="portfolio-card" markdown="1">
<h3><a href="PORTFOLIO_STATUS/">Portfolio status</a></h3>
<p>What is active now, what is paused, and how to reactivate a live demo.</p>
</div>

<div class="portfolio-card" markdown="1">
<h3><a href="operations/monitoring/">Operations and monitoring</a></h3>
<p>Monitoring concepts, signals and operating practices.</p>
</div>
</div>

</div>
