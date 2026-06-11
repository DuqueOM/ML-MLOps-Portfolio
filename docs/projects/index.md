# Projects

<div class="portfolio-page" markdown="1">

<div class="portfolio-hero" markdown="1">
<span class="portfolio-eyebrow">Two projects · one system of evidence</span>

# A portfolio of services, and the template it produced

Everything here is two projects. The **ML-MLOps Portfolio** — one monorepo with
three production services. And the **Production Template** — the open-source
system that packaged what those services taught.

</div>

## Project 1 — The ML-MLOps Portfolio

<div class="portfolio-split" markdown="1">
<div markdown="1">

One monorepo, three different ML problems, one production discipline: each
service ships with its API, tests, Docker and Kubernetes artifacts, multi-cloud
deployment evidence (GKE + EKS), monitoring and documented incidents.
395+ automated tests and 18 architecture decision records across the system.

The three services inside the portfolio — each with its own deep-dive page:

</div>
<div class="portfolio-callout" markdown="1">
<strong>How to review it</strong>

Pick one service and follow its evidence chain: metrics → serving path →
deployment → incident. The debugging deep dive on BankChurn is the
strongest 10-minute read.
</div>
</div>

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>service 01 · churn</small>
<h3><a href="bankchurn/">BankChurn Predictor</a></h3>
<div class="portfolio-badge-row" markdown="1">
<span class="portfolio-badge">AUC 0.87</span>
<span class="portfolio-badge">90% coverage</span>
<span class="portfolio-badge">FastAPI · K8s · SHAP</span>
</div>
<p>Cost-aware churn classification — and the serving incident that went from
81% errors to 0% at half the CPU.</p>

[Open BankChurn](bankchurn.md){ .portfolio-button }
</div>

<div class="portfolio-card" markdown="1">
<small>service 02 · nlp</small>
<h3><a href="nlpinsight/">NLPInsight Analyzer</a></h3>
<div class="portfolio-badge-row" markdown="1">
<span class="portfolio-badge">80.6% accuracy</span>
<span class="portfolio-badge">98% coverage</span>
<span class="portfolio-badge">CPU-only serving</span>
</div>
<p>Financial sentiment with an explainable, low-cost inference path — the
heavier transformer documented as a rejected trade-off.</p>

[Open NLPInsight](nlpinsight.md){ .portfolio-button }
</div>

<div class="portfolio-card" markdown="1">
<small>service 03 · forecasting</small>
<h3><a href="chicagotaxi/">ChicagoTaxi Pipeline</a></h3>
<div class="portfolio-badge-row" markdown="1">
<span class="portfolio-badge">R² 0.96</span>
<span class="portfolio-badge">6.3M rows</span>
<span class="portfolio-badge">PySpark · temporal CV</span>
</div>
<p>Demand forecasting at scale with strictly temporal validation — and the
data leak that was caught before the metrics were published.</p>

[Open ChicagoTaxi](chicagotaxi.md){ .portfolio-button }
</div>
</div>

## Project 2 — The Production Template

<div class="portfolio-split" markdown="1">
<div markdown="1">

The second project is what the first one taught: an open-source starter
system that encodes the portfolio's production lessons as reusable defaults —
serving and training scaffolds, 6 env×cloud Kustomize overlays, signed images
with SBOM attestation (SLSA L2), closed-loop drift monitoring, 32 documented
anti-patterns and 28 ADRs.

Its differentiator is the **governed AI-assisted development layer**: behavior
rules, skills, workflows and an audit trail that keep agentic coding
reviewable and bounded — engineered, not hidden.

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

## Where To Go Deeper

<div class="portfolio-actions" markdown="1">
[:fontawesome-solid-flask: Technical evidence](../technical-evidence.md){ .portfolio-button }
[:fontawesome-solid-diagram-project: Architecture decisions](../architecture/decisions.md){ .portfolio-button }
[:fontawesome-brands-youtube: 3-min video demo](https://youtu.be/7dFFqq2ROPw){ .portfolio-button }
[:fontawesome-solid-file-lines: Recruiter brief](../recruiter-brief.md){ .portfolio-button }
</div>

</div>
