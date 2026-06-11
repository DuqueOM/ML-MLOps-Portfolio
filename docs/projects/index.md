# Projects

<div class="portfolio-page" markdown="1">

<div class="portfolio-hero" markdown="1">
<span class="portfolio-eyebrow">Two projects · one system of evidence</span>

# A portfolio of services, and the template it produced

Everything here is two projects. The **ML-MLOps Portfolio** — one monorepo with
three production services. And the **Production Template** — the open-source
system that packaged what those services taught.

<div class="portfolio-actions" markdown="1">
[Portfolio](#the-ml-mlops-portfolio){ .portfolio-button .portfolio-button--primary }
[Template](#the-production-template){ .portfolio-button }
</div>
</div>

## The ML-MLOps Portfolio

<div class="portfolio-split" markdown="1">
<div markdown="1">

The portfolio is not three models — it is one production system that happens
to serve three of them. Each service ships with its FastAPI contract, test
suite, Docker image and Kubernetes manifests; around them sits the shared
MLOps surface: Terraform-provisioned GKE and EKS clusters, Kustomize overlays
per environment, GitHub Actions CI/CD with quality gates, MLflow tracking,
Prometheus + Grafana monitoring, and the incident writeups that prove the
system was operated, not just deployed.

395+ automated tests and 18 architecture decision records hold it together —
every non-trivial choice is documented with the alternatives it rejected.

</div>
<div class="portfolio-callout" markdown="1">
<strong>How to review it</strong>

Pick one service and follow its evidence chain: metrics → serving path →
deployment → incident. The debugging deep dive on BankChurn is the
strongest 10-minute read.
</div>
</div>

The three services inside the portfolio — each with its own deep-dive page:

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>churn classification</small>
<h3>BankChurn Predictor</h3>
<div class="portfolio-badge-row" markdown="1">
<span class="portfolio-badge">AUC 0.87</span>
<span class="portfolio-badge">90% coverage</span>
<span class="portfolio-badge">FastAPI · K8s · SHAP</span>
</div>
<p>Cost-aware churn classification — and the serving incident that went from
81% errors to 0% at half the CPU.</p>

[BankChurn Predictor](bankchurn.md){ .portfolio-button }
</div>

<div class="portfolio-card" markdown="1">
<small>financial nlp</small>
<h3>NLPInsight Analyzer</h3>
<div class="portfolio-badge-row" markdown="1">
<span class="portfolio-badge">80.6% accuracy</span>
<span class="portfolio-badge">98% coverage</span>
<span class="portfolio-badge">CPU-only serving</span>
</div>
<p>Financial sentiment with an explainable, low-cost inference path — the
heavier transformer documented as a rejected trade-off.</p>

[NLPInsight Analyzer](nlpinsight.md){ .portfolio-button }
</div>

<div class="portfolio-card" markdown="1">
<small>demand forecasting</small>
<h3>ChicagoTaxi Pipeline</h3>
<div class="portfolio-badge-row" markdown="1">
<span class="portfolio-badge">R² 0.96</span>
<span class="portfolio-badge">6.3M rows</span>
<span class="portfolio-badge">PySpark · temporal CV</span>
</div>
<p>Demand forecasting at scale with strictly temporal validation — and the
data leak that was caught before the metrics were published.</p>

[ChicagoTaxi Pipeline](chicagotaxi.md){ .portfolio-button }
</div>
</div>

All the infrastructure, testing, security and monitoring proof behind the
portfolio lives in one place:

<div class="portfolio-actions" markdown="1">
[:fontawesome-solid-flask: Technical Evidence](../technical-evidence.md){ .portfolio-button .portfolio-button--primary }
[:fontawesome-solid-cloud: Deployment evidence](../DEPLOYMENT_EVIDENCE.md){ .portfolio-button }
[:fontawesome-solid-diagram-project: Architecture decisions](../architecture/decisions.md){ .portfolio-button }
[:fontawesome-brands-github: Template repository](https://github.com/DuqueOM/ML-MLOps-Production-Template){ .portfolio-button }
</div>

## The Production Template

<div class="portfolio-split" markdown="1">
<div markdown="1">

The second project is what the first one taught: an open-source starter
system that encodes the portfolio's production lessons as reusable defaults.
Scaffold a new ML service and it arrives with the serving and training
patterns, deployment overlays and operating guardrails already in place —
the mistakes the portfolio paid for once, prevented by default.

Inside the box: a FastAPI serving scaffold with the single-worker +
ThreadPoolExecutor pattern, training pipelines with quality gates (metric,
fairness, leakage), 6 env×cloud Kustomize overlays for GCP and AWS,
Terraform modules, CI/CD that signs images and attests SBOMs (SLSA L2),
closed-loop drift monitoring, 32 documented anti-patterns and 28 ADRs.

Its differentiator is the **governed AI-assisted development layer**:
behavior rules, skills, workflows and an audit trail that keep agentic
coding reviewable and bounded — engineered, not hidden.

</div>
<div class="portfolio-callout" markdown="1">
<strong>Why it matters</strong>

The portfolio proves I can build and operate ML services. The template proves
I can turn that experience into a system other teams can adopt.
</div>
</div>

<div class="portfolio-actions" markdown="1">
[Open the Production Template](../template.md){ .portfolio-button .portfolio-button--primary }
[:fontawesome-brands-github: Template repository](https://github.com/DuqueOM/ML-MLOps-Production-Template){ .portfolio-button }
</div>

</div>
