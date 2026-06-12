# Technical Deep Dive Index

<div class="portfolio-page" markdown="1">

<div class="portfolio-hero" markdown="1">
<span class="portfolio-eyebrow">Technical archive</span>

# Deep evidence, grouped by reviewer intent

This page keeps the full technical archive available without making the main
navigation feel overwhelming. Start with the area you care about, then drill
into the detailed docs only when useful.

<div class="portfolio-actions" markdown="1">
[Back to evidence overview](technical-evidence.md){ .portfolio-button .portfolio-button--primary }
[Current portfolio status](DEPLOYMENT_EVIDENCE.md){ .portfolio-button }
</div>
</div>

## Architecture And Decisions

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Failure story</small>
<h3>[BankChurn debugging deep dive](projects/bankchurn-debugging.md)</h3>
<p>The 81% API error-rate investigation, root cause, fix and reusable lesson.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>System shape</small>
<h3>[Architecture overview](architecture/overview.md)</h3>
<p>How the monorepo, services, data paths, CI/CD and cloud pieces fit together.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Design detail</small>
<h3>[System design](ARCHITECTURE_PORTFOLIO.md)</h3>
<p>Deeper system architecture for reviewers who want the full implementation
picture.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Infrastructure</small>
<h3>[Infrastructure](architecture/infrastructure.md)</h3>
<p>Kubernetes, cloud resources and infrastructure layout.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>CI/CD</small>
<h3>[CI/CD pipeline](architecture/cicd.md)</h3>
<p>Build, validation and deployment automation.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Data</small>
<h3>[Data flow](architecture/data-flow.md)</h3>
<p>How data moves through training, serving and validation paths.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Trade-offs</small>
<h3>[Decisions summary](architecture/decisions.md)</h3>
<p>Readable summary of major architecture decisions and why they were made.</p>
</div>
</div>

## Deployment And Cloud Evidence

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Proof</small>
<h3>[Multi-cloud evidence](DEPLOYMENT_EVIDENCE.md)</h3>
<p>Preserved screenshots, CLI outputs and deployment proof from the active cloud
period.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Cost and parity</small>
<h3>[GCP vs AWS comparison](MULTI_CLOUD_COMPARISON.md)</h3>
<p>Measured trade-offs between the two cloud paths.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Runbook</small>
<h3>[Deployment guide](operations/deployment.md)</h3>
<p>Steps and operating notes for deployment review.</p>
</div>
</div>

## Operations, Models And APIs

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Operations</small>
<h3>[Monitoring](operations/monitoring.md)</h3>
<p>Prometheus, Grafana, metrics and operating signals.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Support</small>
<h3>[Troubleshooting](operations/troubleshooting.md)</h3>
<p>Common failure modes and diagnosis notes.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Models</small>
<h3>[Model catalog](models/catalog.md)</h3>
<p>Model summaries, metrics and project-level model context.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Reproducibility</small>
<h3>[Reproducibility](models/reproducibility.md)</h3>
<p>How experiments and results can be reviewed.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>API</small>
<h3>[REST APIs](api/rest-apis.md)</h3>
<p>Endpoint contracts and request/response review.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>CLI</small>
<h3>[CLI reference](api/cli.md)</h3>
<p>Command-line reference for project operations.</p>
</div>
</div>

## Reference Material

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Start here</small>
<h3>[Quick start](getting-started/quickstart.md)</h3>
<p>Fastest path to understand local setup and first commands.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Setup</small>
<h3>[Installation](getting-started/installation.md)</h3>
<p>Environment and dependency setup.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Development</small>
<h3>[Development setup](getting-started/development.md)</h3>
<p>Developer workflow and local contribution notes.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Release</small>
<h3>[Release process](RELEASE.md)</h3>
<p>Release and deployment process notes.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Security</small>
<h3>[Security policy](SECURITY.md)</h3>
<p>Security expectations, reporting and project posture.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Related work</small>
<h3>[Related projects](related-projects.md)</h3>
<p>How the production template connects to this portfolio.</p>
</div>
</div>

</div>
