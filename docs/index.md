# Duque Ortega Mutis

<div class="portfolio-page portfolio-home" markdown="1">

<div class="portfolio-hero" markdown="1">
<span class="portfolio-eyebrow">MLOps & Production ML Portfolio</span>

# Building ML systems that can be tested, shipped and operated

I am an entry-level MLOps / Production ML candidate based in Mexico City. Before
moving into machine learning, I spent 14 years running business operations:
teams, vendors, budgets, customer processes and cost decisions. That background
shapes how I build ML systems: as services that need reliability, monitoring,
clear trade-offs and documentation people can actually use.

<div class="portfolio-actions" markdown="1">
[Review the technical evidence](technical-evidence.md){ .portfolio-button .portfolio-button--primary }
[View the production template](template.md){ .portfolio-button }
[Contact me](contact.md){ .portfolio-button }
</div>
</div>

<div class="portfolio-stat-strip" markdown="1">
<div class="portfolio-stat">
<small>Portfolio scope</small>
<strong>3 ML services</strong>
<span>Churn, financial sentiment and taxi demand.</span>
</div>
<div class="portfolio-stat">
<small>Engineering proof</small>
<strong>395+ tests</strong>
<span>CI, coverage, infra checks and smoke paths.</span>
</div>
<div class="portfolio-stat">
<small>Cloud evidence</small>
<strong>GKE + EKS</strong>
<span>Real deployment period, now cost-controlled.</span>
</div>
<div class="portfolio-stat">
<small>Reusable system</small>
<strong>MLOps template</strong>
<span>The portfolio lessons packaged into a starter framework.</span>
</div>
</div>

## The Short Version

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Reliable ML services</small>
<h3>APIs beyond notebooks</h3>
<p>FastAPI services, Docker images, Kubernetes manifests, health checks and
smoke tests.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Production workflows</small>
<h3>CI/CD and model operations</h3>
<p>GitHub Actions, MLflow patterns, model versioning, monitoring and deployment
runbooks.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Business-aware engineering</small>
<h3>Cost and trade-offs</h3>
<p>Architecture decisions connect reliability, budget, scope and operational
maintenance.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Communication</small>
<h3>Evidence reviewers can follow</h3>
<p>ADRs, model cards, project summaries, load-test notes and portfolio status
documentation.</p>
</div>
</div>

## Featured System: ML-MLOps Production Template

<div class="portfolio-split" markdown="1">
<div markdown="1">

The most important project here is the reusable
[ML-MLOps Production Template](template.md). It grew out of the mistakes and
lessons from the portfolio: blocked inference APIs, fragile deploy paths,
missing monitoring, unclear model promotion rules and documentation that can
drift away from reality.

For recruiters, this shows product thinking: I did not only build one
portfolio; I extracted the reusable system behind it.

</div>
<div class="portfolio-callout" markdown="1">
<strong>Template capabilities</strong>

- FastAPI serving structure
- Docker and Kubernetes defaults
- Terraform examples for GCP and AWS
- MLflow, drift detection and retraining hooks
- CI/CD and validation workflows
- Agent-assisted workflow rules
</div>
</div>

## Portfolio Projects

<div class="portfolio-project-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Classification</small>
<h3><a href="projects/bankchurn/">BankChurn Predictor</a></h3>
<p>Customer churn model with cost-aware threshold tuning, SHAP explanations and
FastAPI serving.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>NLP</small>
<h3><a href="projects/nlpinsight/">NLPInsight Analyzer</a></h3>
<p>Financial sentiment analysis with a lightweight production path and honest
benchmark selection.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Data engineering</small>
<h3><a href="projects/chicagotaxi/">ChicagoTaxi Pipeline</a></h3>
<p>PySpark demand forecasting with temporal validation and leakage detection on
millions of taxi trips.</p>
</div>
</div>

<div class="portfolio-media" markdown="1">
<img src="media/gifs/portfolio-demo.gif" alt="Portfolio walkthrough">
</div>

## A Concrete Debugging Story

<div class="portfolio-card-grid" markdown="1">
<div class="portfolio-card" markdown="1">
<small>Symptom</small>
<h3>81% API error rate</h3>
<p>Load testing revealed a serving-path failure that looked like a scaling
problem from the outside.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Diagnosis</small>
<h3>CPU contention in inference</h3>
<p>The problem was traced to the serving execution pattern, not just resource
quantity.</p>
</div>

<div class="portfolio-card" markdown="1">
<small>Outcome</small>
<h3>0% error rate after fix</h3>
<p>The inference path was changed and verified with load testing and documented
technical evidence.</p>
</div>
</div>

## How To Review This Site In 3 Minutes

<div class="portfolio-step" markdown="1">
<span class="portfolio-step-number">1</span>
<div markdown="1">
<h3>Start with the candidate story</h3>
Open [About Me](about.md) to understand my background, target roles and why
operations matter in the way I approach ML.
</div>
</div>

<div class="portfolio-step" markdown="1">
<span class="portfolio-step-number">2</span>
<div markdown="1">
<h3>Review the reusable template</h3>
Open [Production Template](template.md) to see the project I am most proud of.
</div>
</div>

<div class="portfolio-step" markdown="1">
<span class="portfolio-step-number">3</span>
<div markdown="1">
<h3>Skim the three projects</h3>
Use [Projects Overview](projects/overview.md) for the ML systems behind the
template.
</div>
</div>

<div class="portfolio-step" markdown="1">
<span class="portfolio-step-number">4</span>
<div markdown="1">
<h3>Check the current operating status</h3>
Open [Portfolio Status](PORTFOLIO_STATUS.md) to separate active assets from
cost-controlled cloud runtime.
</div>
</div>

## Current Operating Status

<div class="portfolio-callout" markdown="1">
The cloud infrastructure is currently **off to control cost**, but the code,
deployment manifests, CI/CD workflows, screenshots and runbooks remain available
as evidence from the active development period. The system can be reactivated
from the documented infrastructure and deployment steps.

[Read the portfolio status](PORTFOLIO_STATUS.md) ·
[Watch the video demo](https://youtu.be/7dFFqq2ROPw)
</div>

</div>
