<div class="portfolio-page portfolio-home" markdown="1">

<div class="portfolio-hero portfolio-hero--profile" markdown="1">
<div class="portfolio-hero-copy" markdown="1">
<span class="portfolio-eyebrow">Production ML · MLOps · Applied AI</span>

# From operations to production ML

I'm **Duque Ortega Mutis**, based in Mexico City, and I am making my first
formal career move into ML/MLOps.

My previous career was not technical by title, but it was technical in practice:
I spent 14 years coordinating people, budgets, vendors, customer pressure,
deadlines and process failures. That work taught me to value systems that are
clear, measurable and usable by the next person responsible for them.

That is why this portfolio is built around production habits rather than only
model scores. I am early-career in formal ML employment, but I am not new to
ownership, trade-offs, documentation or operating under pressure.

<div class="portfolio-quote-card portfolio-quote-card--inline" markdown="1">
<small>How to read my seniority</small>

> Entry-level / junior in formal ML/MLOps employment. Experienced in ownership, pressure,
> cost-awareness and making systems easier for other people to operate.
</div>

<div class="portfolio-actions" markdown="1">
[Watch the 3-min demo](https://youtu.be/7dFFqq2ROPw){ .portfolio-button .portfolio-button--primary }
[Recruiter brief](recruiter-brief.md){ .portfolio-button }
[Contact](contact.md){ .portfolio-button }
</div>
</div>
<figure class="portfolio-profile-frame portfolio-profile-frame--compact">
<img src="media/profile/duque-ortega-mutis.webp" alt="Duque Ortega Mutis in a professional portrait">
</figure>
</div>

<div class="portfolio-stat-strip" markdown="1">
<div class="portfolio-stat">
<small>Service modules</small>
<strong>3 ML systems</strong>
<span>Churn classification, financial NLP, demand forecasting — one monorepo.</span>
</div>
<div class="portfolio-stat">
<small>Validation surface</small>
<strong>395+ tests</strong>
<span>Unit, integration, API contract, infra and smoke coverage.</span>
</div>
<div class="portfolio-stat">
<small>Deployment evidence</small>
<strong>GKE + EKS</strong>
<span>Real multi-cloud runtime windows, screenshots and CLI evidence.</span>
</div>
<div class="portfolio-stat">
<small>Architecture record</small>
<strong>18 ADRs</strong>
<span>Decisions with alternatives rejected and revisit triggers.</span>
</div>
</div>

## Three Production Incidents, Diagnosed From First Principles

The fastest way to evaluate this portfolio is through the failures it survived.
Each incident below was measured, root-caused, fixed and documented — not
patched by trial and error.

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Serving under load</small>
<h3>81% error rate → 0%</h3>
<p>A load test exposed an 81% error rate. Root cause: <code>uvicorn --workers</code>
inside Kubernetes — shared CPU budget produces thrashing, not parallelism.
Redesigned the inference path with <code>asyncio</code> + <code>ThreadPoolExecutor</code>
(GIL analysis documented). Errors dropped to 0% and CPU requests halved
(2000m → 1000m).</p>

[Read the debugging deep dive](projects/bankchurn-debugging.md){ .portfolio-button }
</div>

<div class="portfolio-card" markdown="1">
<small>Explainability</small>
<h3>SHAP returning all zeros</h3>
<p>TreeExplainer is silently incompatible with a <code>StackingClassifier</code>
ensemble. Evaluated four alternatives before deciding; fixed with
<code>KernelExplainer</code> computed in the original feature space so
explanations stay meaningful to the business.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Autoscaling</small>
<h3>HPA that could never scale down</h3>
<p>Memory-based HPA plus the fixed RAM footprint of a loaded ML model makes
scale-down mathematically impossible. Switched to CPU-only HPA: 3 → 1 pods
in 8 minutes, with the reasoning captured in
<a href="decisions/001-cpu-only-hpa/">ADR-001</a>.</p>
</div>
</div>

## System View

<div class="portfolio-split" markdown="1">
<div markdown="1">

The strongest signal is the system shape. Each project proves a different ML
problem, but the portfolio is one end-to-end operating environment: code,
validation, serving, infrastructure, observability and handoff documentation.

Production ML is rarely just the model. The work is in making the model
testable, deployable, explainable and safe enough for another person to operate.

</div>
<div class="portfolio-callout" markdown="1">
<strong>Reviewer takeaway</strong>

Every claim on this page maps to inspectable evidence: source, tests,
screenshots, ADRs, deployment notes. Nothing here asks to be taken on faith.
</div>
</div>

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
<p>AUC, accuracy, R², explainability and dataset limitations are documented
instead of treated as leaderboard one-liners.</p>
</div>

<div class="portfolio-system-node" markdown="1">
<small>3. Serving and batch paths</small>
<h3>APIs beyond notebooks</h3>
<p>FastAPI, prediction contracts, smoke checks and batch-oriented paths make
the models callable and reviewable.</p>
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
<p>GKE and EKS deployment windows, Artifact Registry/ECR paths, Terraform,
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
<h3><a href="projects/bankchurn/">BankChurn Predictor</a></h3>
<div class="portfolio-badge-row" markdown="1">
<span class="portfolio-badge">AUC 0.87</span>
<span class="portfolio-badge">90% coverage</span>
<span class="portfolio-badge">FastAPI · K8s · SHAP</span>
</div>
<p>Churn classification with cost-aware threshold tuning (a missed churner
costs more than a retention offer), SHAP explanations and the serving-path
hardening documented in the incidents above.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Financial NLP service</small>
<h3><a href="projects/nlpinsight/">NLPInsight Analyzer</a></h3>
<div class="portfolio-badge-row" markdown="1">
<span class="portfolio-badge">80.6% accuracy</span>
<span class="portfolio-badge">98% coverage</span>
<span class="portfolio-badge">CPU-friendly serving</span>
</div>
<p>Financial sentiment classification with a lightweight production path and a
documented transformer trade-off: explainable, low-cost inference was chosen
over a heavier model that would be harder to operate.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Demand forecasting pipeline</small>
<h3><a href="projects/chicagotaxi/">ChicagoTaxi Pipeline</a></h3>
<div class="portfolio-badge-row" markdown="1">
<span class="portfolio-badge">R² 0.96</span>
<span class="portfolio-badge">6.3M rows</span>
<span class="portfolio-badge">PySpark · temporal CV</span>
</div>
<p>Demand forecasting over 6.3M trips with PySpark ETL, temporal validation
and a data-leakage correction that survived honest re-evaluation.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Flagship open source</small>
<h3><a href="template/">ML-MLOps Production Template</a></h3>
<div class="portfolio-badge-row" markdown="1">
<span class="portfolio-badge">32 anti-patterns</span>
<span class="portfolio-badge">SLSA L2 supply chain</span>
<span class="portfolio-badge">AUTO / CONSULT / STOP</span>
</div>
<p>The production lessons from all three services, packaged as a reusable
system: serving and training templates, GKE+EKS overlays, signed images with
SBOM attestation, closed-loop monitoring — and a governed AI-assisted
development layer (rules, skills, audit trail) that keeps agentic coding
reviewable and bounded.</p>
</div>
</div>

## Engineering Decisions Worth Reading

<div class="portfolio-card-grid portfolio-card-grid--compact" markdown="1">
<div class="portfolio-card" markdown="1">
<small><a href="decisions/014-single-worker-pod-ml-inference/">ADR-014</a></small>
<h3>One uvicorn worker per pod</h3>
<p>Horizontal scale belongs to the HPA, not to in-pod worker processes
competing for the same CPU budget.</p>
</div>

<div class="portfolio-card" markdown="1">
<small><a href="decisions/015-async-inference-threadpool/">ADR-015</a></small>
<h3>ThreadPoolExecutor for inference</h3>
<p>CPU-bound <code>model.predict()</code> in an async endpoint blocks the event
loop; the executor keeps health probes alive under load.</p>
</div>

<div class="portfolio-card" markdown="1">
<small><a href="decisions/002-emptydir-model-storage/">ADR-002</a></small>
<h3>Models out of the image</h3>
<p>Init container + <code>emptyDir</code> decouples model promotion from image
rebuilds and keeps images signable and small.</p>
</div>

<div class="portfolio-card" markdown="1">
<small><a href="decisions/013-multicloud-parity-policy/">ADR-013</a></small>
<h3>Multi-cloud parity policy</h3>
<p>GCP-primary with explicit AWS parity rules — what must match, what may
diverge, and how divergence is documented.</p>
</div>
</div>

[Browse all 18 ADRs](architecture/decisions.md){ .portfolio-button }

## Evidence Index

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<h3><a href="technical-evidence/">Technical evidence</a></h3>
<p>Tests, coverage, CI/CD runs, security scanning and quality gates.</p>
</div>

<div class="portfolio-card" markdown="1">
<h3><a href="DEPLOYMENT_EVIDENCE/">Deployment evidence</a></h3>
<p>GKE and EKS windows: screenshots, CLI transcripts, manifests, cost notes.</p>
</div>

<div class="portfolio-card" markdown="1">
<h3><a href="about/">About me</a></h3>
<p>Career path, operations background in numbers, education and how I work.</p>
</div>

<div class="portfolio-card" markdown="1">
<h3><a href="https://github.com/DuqueOM">GitHub profile</a></h3>
<p>Source for everything on this site, plus the production template repo.</p>
</div>
</div>

</div>
