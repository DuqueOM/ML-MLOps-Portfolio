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
[Read incident writeup](projects/bankchurn-debugging.md){ .portfolio-button .portfolio-button--primary }
[Open deep dive index](technical-deep-dive.md){ .portfolio-button }
[Check current status](PORTFOLIO_STATUS.md){ .portfolio-button }
[Review projects](projects/overview.md){ .portfolio-button }
</div>
</div>

## Production Incidents

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Serving concurrency</small>
<h3>81% API errors -> 0%</h3>
<p><strong>Symptom:</strong> Locust exposed an 81% error rate under concurrent
prediction traffic.</p>
<p><strong>Hypothesis:</strong> it first looked like a scaling or CPU allocation
problem.</p>
<p><strong>Diagnosis:</strong> <code>uvicorn --workers N</code> under
Kubernetes created contention inside a shared pod CPU budget, while synchronous
ML inference blocked the FastAPI event loop.</p>
<p><strong>Fix:</strong> one worker per pod, Kubernetes HPA for horizontal
scaling, and CPU-bound inference moved to
<code>asyncio.run_in_executor()</code> with <code>ThreadPoolExecutor</code>.</p>
<p><strong>Result:</strong> error rate dropped to 0% in validation and the CPU
request was reduced by roughly 50%.</p>

[Read the full incident writeup](projects/bankchurn-debugging.md){ .portfolio-button .portfolio-button--primary }
</div>

<div class="portfolio-card" markdown="1">
<small>Explainability</small>
<h3>All-zero SHAP outputs</h3>
<p><strong>Symptom:</strong> SHAP explanations returned unusable all-zero
contributions.</p>
<p><strong>Diagnosis:</strong> the BankChurn StackingClassifier pipeline was not
compatible with the initial TreeExplainer path.</p>
<p><strong>Fix:</strong> use KernelExplainer through a predict-proba wrapper in
the original feature space, so explanations match the served model contract.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Autoscaling</small>
<h3>HPA scale-down fixed</h3>
<p><strong>Symptom:</strong> pods stayed overprovisioned after traffic dropped.</p>
<p><strong>Diagnosis:</strong> memory was a misleading HPA signal because ML pods
keep a fixed model memory footprint even when request volume falls.</p>
<p><strong>Fix:</strong> remove memory-based scaling and use CPU-only HPA,
reducing replicas from 3 to 1 in 8 minutes.</p>
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

## Visual Evidence Shortcuts

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Serving path</small>
<h3>Live ML predictions</h3>
<img class="portfolio-evidence-image" src="../media/gifs/ml-predictions.gif" alt="Animated walkthrough of ML prediction APIs">
<p>FastAPI prediction paths for the portfolio services, shown as a short visual
review instead of another long code block.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Observability path</small>
<h3>Monitoring under load</h3>
<img class="portfolio-evidence-image" src="../media/gifs/monitoring-observability.gif" alt="Animated walkthrough of monitoring and observability evidence">
<p>Grafana, Prometheus, Locust and MLflow evidence grouped for reviewers who
want runtime behavior, not only architecture claims.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Cloud path</small>
<h3>GKE and EKS parity</h3>
<img class="portfolio-evidence-image" src="../media/gifs/multicloud-parity.gif" alt="Animated walkthrough of GKE and EKS multi-cloud evidence">
<p>Side-by-side cloud evidence showing that the portfolio was exercised across
Google Cloud and AWS Kubernetes environments.</p>
</div>
</div>

## Green Checks And Runtime Evidence

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>CI proof</small>
<h3>GitHub Actions completed</h3>
<img class="portfolio-evidence-image" src="../media/screenshots/cicd/46-workflow-completado.png" alt="GitHub Actions workflow completed successfully">
<p>Visible green checks reduce the time a technical reviewer spends wondering
whether the 395+ tests are only a claim.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Smoke proof</small>
<h3>API health checks passed</h3>
<img class="portfolio-evidence-image" src="../media/screenshots/terminal/23-health-checks-apis.png" alt="Terminal showing API health checks passing">
<p>Health-check screenshots show that the APIs were exercised as running
services, not only described in documentation.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Model lifecycle</small>
<h3>MLflow experiment tracking</h3>
<img class="portfolio-evidence-image" src="../media/screenshots/monitoring/39-mlflow-experiments.png" alt="MLflow experiments screenshot">
<p>MLflow evidence makes model tracking tangible for reviewers who want to see
experiment and model registry habits.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Observability</small>
<h3>Grafana and load testing</h3>
<img class="portfolio-evidence-image" src="../media/screenshots/monitoring/38c-load-test-results.png" alt="Load test results screenshot">
<p>The load-test evidence connects observability claims to measured runtime
behavior.</p>
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

## Key Engineering Decisions

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Serving</small>
<h3>One worker per pod plus executor</h3>
<p>Kubernetes handles horizontal scaling; the API avoids
<code>uvicorn --workers N</code> inside one pod and keeps the event loop free by
offloading CPU-bound inference work to <code>asyncio.run_in_executor()</code>
and <code>ThreadPoolExecutor</code>.</p>

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
<h3><a href="../projects/overview/">Projects overview</a></h3>
<p>The three ML systems and their main results.</p>
</div>

<div class="portfolio-card" markdown="1">
<h3><a href="../projects/bankchurn-debugging/">BankChurn debugging deep dive</a></h3>
<p>The full failure story: symptoms, hypotheses, root cause, fix, validation
and template lesson.</p>
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
