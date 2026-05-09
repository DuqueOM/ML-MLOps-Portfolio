# Portfolio Status

<div class="portfolio-page portfolio-status-page" markdown="1">

<div class="portfolio-hero" markdown="1">
<span class="portfolio-eyebrow">Operating status</span>

# Production-oriented evidence, currently in showcase mode

This page separates what is active today from what was proven during the live
cloud deployment period. It is designed for recruiters, hiring managers, and
technical reviewers who need the status in minutes, not a wall of operational
detail.

<div class="portfolio-actions" markdown="1">
[Review technical evidence](technical-evidence.md){ .portfolio-button .portfolio-button--primary }
[Read ADR-018](decisions/018-portfolio-maintenance-mode.md){ .portfolio-button }
[Open deployment evidence](DEPLOYMENT_EVIDENCE.md){ .portfolio-button }
</div>
</div>

<div class="portfolio-stat-strip" markdown="1">
<div class="portfolio-stat">
<small>Mode</small>
<strong>Showcase</strong>
<span>Reference implementation; live clusters are off.</span>
</div>
<div class="portfolio-stat">
<small>Last live deploy</small>
<strong>v3.6.0</strong>
<span>Validated during March 2026 active development.</span>
</div>
<div class="portfolio-stat">
<small>Reactivation</small>
<strong>1-2h</strong>
<span>Plus temporary GCP/AWS budget.</span>
</div>
<div class="portfolio-stat">
<small>Current proof</small>
<strong>CI + docs</strong>
<span>Code, tests, IaC, runbooks, ADRs and screenshots remain available.</span>
</div>
</div>

## Executive Readout

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>What this is</small>
<h3>Reference MLOps portfolio</h3>
<p>Three ML services, multi-cloud Kubernetes artifacts, Terraform, CI/CD,
observability, drift detection and ADR-backed design decisions.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>What is real</small>
<h3>Implementation, not slideware</h3>
<p>The code, manifests, Terraform and workflows were used against live clusters
during development. Evidence from that period is preserved in the docs.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>What is off</small>
<h3>Cost-controlled infrastructure</h3>
<p>GKE, EKS, MLflow, Prometheus and Grafana are not running continuously because
the cloud control-plane cost is not justified for a permanent showcase.</p>
</div>
</div>

## Active vs Paused Surfaces

<p class="portfolio-section-lead">
The fastest way to review the portfolio is to separate active engineering assets
from intentionally paused cloud runtime surfaces.
</p>

### Active Now

<div class="portfolio-status-grid" markdown="1">
<div class="portfolio-status-card is-active" markdown="1">
<span class="portfolio-pill is-active">Active</span>
<h3>Source code</h3>
<p>All three services remain reviewable and tested on every push.</p>
</div>

<div class="portfolio-status-card is-active" markdown="1">
<span class="portfolio-pill is-active">Active</span>
<h3>Unit and integration CI</h3>
<p><code>ci-mlops.yml</code> runs on push and PR with 395+ tests and 90-96% coverage.</p>
</div>

<div class="portfolio-status-card is-active" markdown="1">
<span class="portfolio-pill is-active">Active</span>
<h3>Terraform validation</h3>
<p><code>ci-infra.yml</code> validates infrastructure changes without requiring live clusters.</p>
</div>

<div class="portfolio-status-card is-active" markdown="1">
<span class="portfolio-pill is-active">Active</span>
<h3>GitHub Pages docs</h3>
<p>This site is the current public review surface for architecture, evidence and operations.</p>
</div>

<div class="portfolio-status-card is-active" markdown="1">
<span class="portfolio-pill is-active">Active</span>
<h3>Docker build path</h3>
<p>Images are built as CI artifacts and the Dockerfiles remain production-oriented.</p>
</div>
</div>

### Paused or Inactive

<div class="portfolio-status-grid" markdown="1">
<div class="portfolio-status-card is-inactive" markdown="1">
<span class="portfolio-pill is-inactive">Inactive</span>
<h3>GKE cluster</h3>
<p>Torn down after the live development and load-testing period.</p>
</div>

<div class="portfolio-status-card is-inactive" markdown="1">
<span class="portfolio-pill is-inactive">Inactive</span>
<h3>EKS cluster</h3>
<p>Torn down for the same cost-control reason as GKE.</p>
</div>

<div class="portfolio-status-card is-inactive" markdown="1">
<span class="portfolio-pill is-inactive">Inactive</span>
<h3>MLflow and observability stack</h3>
<p>MLflow, Prometheus and Grafana were deployed on the clusters; they are gone with them.</p>
</div>

<div class="portfolio-status-card is-paused" markdown="1">
<span class="portfolio-pill is-paused">Paused</span>
<h3>Promotion workflows</h3>
<p>Artifact Registry and ECR promotion are disabled until a live demo is requested.</p>
</div>

<div class="portfolio-status-card is-paused" markdown="1">
<span class="portfolio-pill is-paused">Paused</span>
<h3>Daily drift detection</h3>
<p>The scheduled trigger is disabled; <code>workflow_dispatch</code> is still available.</p>
</div>

<div class="portfolio-status-card is-paused" markdown="1">
<span class="portfolio-pill is-paused">Paused</span>
<h3>Daily retrain checks</h3>
<p>Paused with the same maintenance-mode logic as drift detection.</p>
</div>
</div>

## Why Infrastructure Is Off

<div class="portfolio-split" markdown="1">
<div markdown="1">

Running GKE + EKS + managed Postgres + container registries continuously costs
roughly **$180-$220/month** combined. That spend was justified during active
development, load testing and incident-style validation; it is not economical as
an always-on showcase.

The important distinction is that the portfolio is not claiming a fictional
live environment. It keeps the evidence that matters: manifests, Terraform,
runbooks, ADRs, screenshots, load-test results and incident notes from the real
deployment period.

</div>
<div class="portfolio-callout" markdown="1">
<strong>Decision record</strong>

The full rationale lives in
[ADR-018: Portfolio Maintenance Mode](decisions/018-portfolio-maintenance-mode.md).
</div>
</div>

## How Repository Noise Is Controlled

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Drift issues</small>
<h3>Workflow dispatch only</h3>
<p>The daily schedule was disabled. The previous condition treated script
failures as drift events; the workflow now checks for successful drift detection
and an explicit drift flag.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Security alerts</small>
<h3>Trivy signal cleanup</h3>
<p><code>ignore-unfixed: true</code> keeps unfixable base-image CVEs from becoming
permanent noise while preserving actionable scanner findings.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Dependencies</small>
<h3>Dependabot with limits</h3>
<p>GitHub Actions updates run weekly and are capped at three open PRs, keeping
maintenance visible without drowning the repo.</p>
</div>
</div>

## Reactivation Playbook

<p class="portfolio-section-lead">
A live end-to-end demo can be restored from the existing Terraform, workflows
and runbooks. Budget approval is the main prerequisite.
</p>

<div class="portfolio-step" markdown="1">
<span class="portfolio-step-number">1</span>
<div markdown="1">
<h3>Provision infrastructure, about 30 min</h3>

```bash
cd infra/terraform/gcp && terraform apply -var-file=terraform.tfvars
cd ../aws && terraform apply -var-file=terraform.tfvars
```
</div>
</div>

<div class="portfolio-step" markdown="1">
<span class="portfolio-step-number">2</span>
<div markdown="1">
<h3>Push images to cloud registries, about 15 min</h3>

```bash
gh workflow run promote-images.yml
```
</div>
</div>

<div class="portfolio-step" markdown="1">
<span class="portfolio-step-number">3</span>
<div markdown="1">
<h3>Deploy to clusters, about 20 min</h3>

```bash
gh workflow run deploy-gcp.yml --ref v3.6.0
gh workflow run deploy-aws.yml --ref v3.6.0
```
</div>
</div>

<div class="portfolio-step" markdown="1">
<span class="portfolio-step-number">4</span>
<div markdown="1">
<h3>Re-enable scheduled drift detection</h3>

Uncomment the <code>schedule:</code> block in
<code>.github/workflows/drift-detection.yml</code>.
</div>
</div>

<div class="portfolio-step" markdown="1">
<span class="portfolio-step-number">5</span>
<div markdown="1">
<h3>Run smoke tests</h3>

```bash
./scripts/smoke_test.sh
```
</div>
</div>

<div class="portfolio-step" markdown="1">
<span class="portfolio-step-number">6</span>
<div markdown="1">
<h3>Teardown after the demo</h3>

Run <code>terraform destroy</code> in both cloud directories to avoid turning a
demo into recurring cost.
</div>
</div>

## Maintenance Pass Summary

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Issue hygiene</small>
<h3>168 stale drift alerts closed</h3>
<p>Each closure points reviewers back to this status page and the maintenance
mode decision.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Dependency hygiene</small>
<h3>3 Dependabot PRs merged</h3>
<p>GitHub Actions bumps were merged while heavier Docker-image changes were
deferred to the next active sprint.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Security hygiene</small>
<h3>210 legacy Trivy alerts handled</h3>
<p>Legacy unfixable alerts were dismissed with documented <code>won't fix</code>
reasoning.</p>
</div>
</div>

## Reviewer FAQ

<details class="portfolio-faq-item">
<summary>Can this actually be redeployed?</summary>

Yes. Terraform is current and validated on infrastructure changes. A full
redeploy is roughly one hour from infrastructure apply to green smoke tests,
assuming credentials and budget are ready.
</details>

<details class="portfolio-faq-item">
<summary>How were the latency claims verified?</summary>

With Locust load tests against live clusters during the v3.6.0 period. Raw
results live in [Load Test Results](load-test-results.md), with visual evidence
under `docs/media/`.
</details>

<details class="portfolio-faq-item">
<summary>Why not keep a tiny cluster running?</summary>

The control-plane floor alone is material: GKE and EKS each carry monthly
control-plane cost even when workloads are near zero. ADR-018 documents the
alternatives and the final maintenance-mode decision.
</details>

<details class="portfolio-faq-item">
<summary>How would this noise problem be handled in production?</summary>

The drift workflow bug was fixed so script failure is no longer treated as a
drift event. With live data, drift jobs should complete successfully and open
issues only when PSI exceeds the configured threshold.
</details>

</div>
