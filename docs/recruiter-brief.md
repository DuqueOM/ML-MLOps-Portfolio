# Recruiter Brief

<div class="portfolio-page" markdown="1">

<div class="portfolio-hero" markdown="1">
<span class="portfolio-eyebrow">Recruiter-friendly screening view</span>

# ML engineer who builds systems that survive production

3 minutes of evidence: three services deployed on GKE + EKS, three incidents
measured and root-caused, and an open-source production template that packaged
the lessons. Early-career in formal ML employment — that is stated once and
not repeated.

Before tech, I spent 14 years running operations — teams, budgets, vendors,
delivery under pressure. That is where the cost discipline, documentation habit
and ownership come from. The engineering is the recent chapter; the production
thinking has been there since before the first model.

<div class="portfolio-actions portfolio-actions--anchors" markdown="1">
[Snapshot](#quick-screening-snapshot){ .portfolio-button .portfolio-button--primary }
[Proof Points](#key-proof-points){ .portfolio-button }
[Roles](#best-fit-roles){ .portfolio-button }
[Background](#why-the-background-matters){ .portfolio-button }
[Difference](#what-makes-me-different){ .portfolio-button }
[90 Days](#first-90-days-contribution){ .portfolio-button }
</div>
</div>

## Quick Screening Snapshot

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Target level</small>
<h3>Entry-level / junior MLOps & Production ML</h3>
<p>I am looking for a role with room to
learn, contribute and grow into stronger production ML ownership.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Location</small>
<h3>Mexico City / Remote</h3>
<p>Open to remote-first opportunities, especially with US, Mexico or LATAM teams
where written technical communication matters.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Languages</small>
<h3>Spanish native, English B2</h3>
<p>Comfortable with technical documentation, async collaboration and interview
conversations in English with preparation.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Education</small>
<h3>TripleTen Data Science, 2026</h3>
<p>Formal training layer supporting the portfolio projects and MLOps transition.
Hands-on AWS (EKS, ECR, IRSA, Terraform) exercised across the portfolio
infrastructure code.</p>
</div>
</div>

<div class="portfolio-callout" markdown="1">
<strong>Level:</strong> Early-career in formal ML/MLOps employment. The scope,
compensation band and code-review dynamic of a junior role are the right fit.
The operations maturity is a contribution, not a claim of seniority.
</div>

## Key Proof Points

<div class="portfolio-card-grid portfolio-card-grid--compact" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Incident: serving</small>
<h3><a href="../projects/bankchurn-debugging/">81% errors → 0%</a></h3>
<p>Load test exposed a Kubernetes serving failure. Root cause: uvicorn worker
contention. Fixed with asyncio + ThreadPoolExecutor. CPU request halved.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Incident: explainability</small>
<h3>SHAP returning all zeros</h3>
<p>TreeExplainer silently incompatible with a StackingClassifier ensemble.
Evaluated four alternatives; fixed with KernelExplainer in original feature space.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Incident: autoscaling</small>
<h3>HPA that could never scale down</h3>
<p>Memory-based HPA plus fixed ML model footprint makes scale-down mathematically
impossible. Switched to CPU-only HPA: 3 → 1 pods in 8 minutes.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Reusable system</small>
<h3><a href="../template/">Production template</a></h3>
<p>32 anti-patterns, 28 ADRs, SLSA L2 supply chain, governed AI-assisted
development — all packaged as reusable defaults for the next ML service.</p>
</div>
</div>

## Best-Fit Roles

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Primary fit</small>
<h3>Junior ML Engineer</h3>
<p>Applied ML roles where model work needs APIs, testing, deployment and a
clear handoff into an engineering workflow.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Strong second</small>
<h3>Junior Data Scientist (production-leaning)</h3>
<p>DS roles where the model is not the end state — serving, monitoring and
operability matter alongside the modeling work.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Adjacent path</small>
<h3>Junior Data Engineer (ML workflows)</h3>
<p>Pipeline, batch and data-path roles connected to production ML systems —
PySpark, validation, feature engineering, cloud storage.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Low-volume bonus</small>
<h3>MLOps Engineer</h3>
<p>Serving, CI/CD, monitoring, MLflow hygiene, deployment artifacts and
reliability improvements for ML systems in production.</p>
</div>
</div>

## Why The Background Matters

<div class="portfolio-split" markdown="1">
<div markdown="1">

Most ML portfolios show model scores. This one shows what happens after the
model works: APIs, tests, deployment artifacts, incidents diagnosed from first
principles, monitoring, cost decisions and documentation another person can
review.

The 14 years in operations are the source of the cost discipline, the
documentation habit and the bias toward ownership. The engineering is the
recent chapter — and three deployed services, three root-caused incidents and
one extracted production template are the proof.

</div>
<div class="portfolio-callout" markdown="1">
<strong>One sentence on level</strong>

Early-career in formal ML/MLOps employment. The right seat is junior — that is
the honest scope, the right compensation band and where the learning happens.
</div>
</div>

## What Makes Me Different

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>2026 differentiator</small>
<h3>Governed AI-assisted development</h3>
<p>I engineer my AI workflow — behavior protocols, audit trail, eval gates —
instead of hiding it. The template's governance layer is the proof.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Debugging</small>
<h3>I measure before guessing</h3>
<p>Three incidents, three root causes found by measuring — not by trial and
error. The 81%→0% writeup is the clearest example.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Ownership</small>
<h3>Decisions are documented</h3>
<p>18 ADRs, runbooks and status pages so reviewers can see why, not only what.
Another person can operate this system.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Cost awareness</small>
<h3>Budget is part of the design</h3>
<p>14 years of operations means cost, scope and maintenance enter the
engineering discussion from the start, not as afterthoughts.</p>
</div>
</div>

## First 90 Days Contribution

<div class="portfolio-feature-band" markdown="1">
<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Days 1-30</small>
<h3>Learn and document the workflow</h3>
<p>Run the stack locally, understand the model lifecycle, map deployment steps,
document gaps and fix small onboarding or test issues.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Days 31-60</small>
<h3>Contribute to delivery support</h3>
<p>Help with FastAPI endpoints, validation checks, MLflow hygiene, CI/CD tasks,
Docker/Kubernetes artifacts or monitoring improvements under review.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Days 61-90</small>
<h3>Own a focused reliability improvement</h3>
<p>Take one scoped improvement from issue to documentation: smoke tests,
readiness checks, drift notes, runbooks, cost tracking or deployment evidence.</p>
</div>
</div>
</div>

## What To Look For In The Portfolio

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Project judgment</small>
<h3>Reusable MLOps template</h3>
<p>The strongest project is the production template: a reusable starting point
for ML services with serving, testing, deployment and workflow guardrails.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Debugging ability</small>
<h3>Measured incident writeups</h3>
<p>The portfolio includes load testing, inference-path debugging and documented
trade-offs rather than only final model metrics.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Communication</small>
<h3>Evidence a team can review</h3>
<p>Architecture notes, model cards, runbooks, deployment evidence and current
portfolio status are written so both technical and non-technical reviewers can
understand the story.</p>
</div>
</div>

## Suggested Screening Questions

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Debugging</small>
<h3>Ask about the 81% API error rate</h3>
<p>The important signal is the diagnosis process: how I moved from symptoms to
root cause, fixed the serving path and verified the result.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Product thinking</small>
<h3>Ask why I built the template</h3>
<p>The template shows how I converted repeated portfolio lessons into reusable
guardrails for future ML services.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Cost judgment</small>
<h3>Ask about GCP vs AWS trade-offs</h3>
<p>The cloud comparison is useful because it connects technical deployment
evidence with operating cost and scope control.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Self-awareness</small>
<h3>Ask what I would improve next</h3>
<p>This opens the most honest conversation: where the portfolio is strong,
where it is still controlled evidence, and how I would evolve it on a team.</p>
</div>
</div>

## What I Am Building Next

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Live evidence</small>
<h3>More real traffic windows</h3>
<p>Run short, cost-controlled live demos to capture fresh Grafana, Prometheus
and MLflow evidence without leaving infrastructure online permanently.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Collaboration</small>
<h3>More public review signals</h3>
<p>Add external feedback, PR review examples or open-source contributions so
the portfolio shows how I work with other engineers.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Depth</small>
<h3>One deeper infrastructure writeup</h3>
<p>Expand one operational topic, such as monitoring or deployment strategy,
into a concise trade-off article.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Domain fit</small>
<h3>A project closer to operations</h3>
<p>Explore a future project around inventory, staffing, cost anomalies or
operations forecasting, where my previous background is a direct advantage.</p>
</div>
</div>

## Current Boundaries And Next Proof

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Live traffic</small>
<h3>Controlled load tests, not 24/7 users</h3>
<p>The strongest runtime evidence comes from controlled load tests and live
development windows, not persistent production user traffic.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Cloud ML platforms</small>
<h3>GCP and AWS Kubernetes first</h3>
<p>My cloud work is centered on GKE, EKS, Terraform and kubectl. SageMaker and
Azure ML are not yet core strengths.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>ML depth</small>
<h3>Engineering and deployment side</h3>
<p>I am not presenting myself as an ML researcher. My strongest signal is
turning applied models into testable, operable systems.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>External collaboration</small>
<h3>Next public signal</h3>
<p>Open-source contribution, external review or a PR review sample is the next
proof I want to add.</p>
</div>
</div>

## Useful Links

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<h3><a href="../">Home</a></h3>
<p>Personal-professional story, target roles and working style.</p>
</div>

<div class="portfolio-card" markdown="1">
<h3><a href="../template/">Production Template</a></h3>
<p>The reusable MLOps project that best summarizes the portfolio.</p>
</div>

<div class="portfolio-card" markdown="1">
<h3><a href="../technical-evidence/">Technical Evidence</a></h3>
<p>Deeper proof for technical hiring managers.</p>
</div>

<div class="portfolio-card" markdown="1">
<h3><a href="../contact/">Contact</a></h3>
<p>Email, LinkedIn, GitHub, video demo and repository links.</p>
</div>
</div>

</div>
