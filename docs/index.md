# Duque Ortega Mutis

## MLOps & Production ML Portfolio

I am an entry-level MLOps / Production ML candidate based in Mexico City. Before
moving into machine learning, I spent 14 years running business operations:
teams, vendors, budgets, customer processes, and cost decisions. That background
shapes the way I build ML systems: not as isolated notebooks, but as services
that need to be deployed, monitored, explained, and improved.

I am looking for my first formal role in **MLOps, Production ML, Applied AI, ML
Platform, or Data Engineering with ML workflows**.

[Contact me](contact.md) | [View the template](template.md) | [See technical evidence](technical-evidence.md)

---

## The Short Version

| What I am building toward | Evidence in this portfolio |
|---------------------------|----------------------------|
| Reliable ML services | FastAPI APIs, Docker images, Kubernetes manifests, health checks, and smoke tests. |
| Production-minded workflows | CI/CD, MLflow tracking, model versioning, monitoring, and deployment runbooks. |
| Business-aware engineering | Cost comparisons, trade-off documentation, and decisions tied to reliability and maintainability. |
| Clear communication | Architecture Decision Records, model cards, project summaries, and video walkthroughs. |
| Reusable systems | A separate MLOps template that packages the lessons from this portfolio into a starter framework. |

---

## Why This Portfolio Exists

Many beginner ML portfolios stop at training a model and reporting a metric.
This one asks the next question: **what happens after the model needs to serve
real requests?**

That is why the projects include APIs, containers, tests, deployment artifacts,
monitoring, incident notes, and documented decisions. The goal is not to claim
senior-level production ownership. The goal is to show that I understand the
operational side of ML and can grow quickly inside a team that builds real
systems.

---

## Featured Project: ML-MLOps Production Template

The most important project here is the reusable
[ML-MLOps Production Template](template.md).

It grew out of the mistakes and lessons from the portfolio: blocked inference
APIs, fragile deploy paths, missing monitoring, unclear model promotion rules,
and documentation that can drift away from reality.

The template turns those lessons into a reusable starting point for ML services:

- FastAPI serving structure
- Docker and Kubernetes defaults
- Terraform examples for GCP and AWS
- MLflow, drift detection, and retraining hooks
- CI/CD and validation workflows
- safety checks for secrets, images, and deployment decisions
- agent-assisted workflow rules that keep automation inside documented limits

For recruiters, this shows product thinking: I did not only build one portfolio;
I extracted the reusable system behind it.

[Read the template overview](template.md) | [Open the GitHub repo](https://github.com/DuqueOM/ML-MLOps-Production-Template)

---

## Portfolio Projects

These three projects show the technical foundation behind the template.

| Project | What it shows | Why it matters |
|---------|---------------|----------------|
| [BankChurn Predictor](projects/bankchurn.md) | Customer churn model served through an API with SHAP explanations and threshold tuning. | Connects ML metrics to business cost: missing a churner is more expensive than a retention offer. |
| [NLPInsight Analyzer](projects/nlpinsight.md) | Financial sentiment analysis with a lightweight production path and an optional transformer path. | Shows honest benchmark selection instead of chasing an inflated metric. |
| [ChicagoTaxi Pipeline](projects/chicagotaxi.md) | PySpark data processing and demand forecasting on millions of taxi trips. | Shows data engineering, leakage detection, and temporal validation. |

<img src="media/gifs/portfolio-demo.gif" alt="Portfolio walkthrough" width="640">

---

## A Concrete Debugging Story

During load testing, one ML API reached an 81% error rate. The quick answer
would have been "add more resources." Instead, I traced the behavior to CPU
contention in the serving path, changed the inference pattern to use
asynchronous execution with a thread pool, and brought the error rate down to
0%.

That experience is a good summary of how I want to work:

1. measure the problem;
2. understand the cause;
3. fix the smallest meaningful thing;
4. document the lesson so the next system is better.

[Read the technical evidence](technical-evidence.md)

---

## How To Review This Site In 3 Minutes

1. Start with [About Me](about.md) to understand my background and target roles.
2. Open [Production Template](template.md) to see the reusable project I am most proud of.
3. Skim [Projects](projects/overview.md) for the three ML systems.
4. Use [Technical Evidence](technical-evidence.md) if you want the deeper engineering proof.
5. Reach out through [Contact](contact.md) if the profile fits an entry-level or junior ML/MLOps opening.

---

## Current Operating Status

The cloud infrastructure is currently **off to control cost**, but the code,
deployment manifests, CI/CD workflows, screenshots, and runbooks remain available
as evidence from the active development period. The system can be reactivated
from the documented infrastructure and deployment steps.

[Portfolio status](PORTFOLIO_STATUS.md) | [Video demo](https://youtu.be/7dFFqq2ROPw)
