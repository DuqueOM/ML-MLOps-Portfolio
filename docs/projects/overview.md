# Projects Overview

These projects are the technical evidence behind my transition into MLOps and
Production ML. Each one starts with a machine learning problem, then goes one
step further: API design, testing, deployment artifacts, monitoring, and
documentation.

[Watch the video demo](https://youtu.be/7dFFqq2ROPw)

<img src="../media/gifs/portfolio-demo.gif" alt="Portfolio Demo" width="640">

---

## The Three Projects

| Project | Problem | What I practiced |
|---------|---------|------------------|
| [BankChurn Predictor](bankchurn.md) | Predict which banking customers may churn. | Classification, cost-aware threshold tuning, SHAP explanations, FastAPI serving. |
| [NLPInsight Analyzer](nlpinsight.md) | Classify sentiment in financial text. | NLP, honest benchmark selection, lightweight serving, optional transformer path. |
| [ChicagoTaxi Pipeline](chicagotaxi.md) | Forecast taxi demand from trip data. | PySpark ETL, time-based validation, leakage detection, batch-style ML workflow. |

## What They Have In Common

- Python-based ML workflows with measurable metrics.
- APIs or pipelines that can be tested and reviewed.
- Docker and deployment artifacts instead of notebook-only demos.
- Documentation explaining why choices were made.
- Practical trade-offs around latency, cost, explainability, and maintainability.

## Key Results

| Project | Main metric | Additional signal |
|---------|-------------|-------------------|
| BankChurn | AUC 0.87 | 90% test coverage and a documented inference reliability fix. |
| NLPInsight | 80.6% accuracy | 98% coverage and a more honest dataset choice over an easier benchmark. |
| ChicagoTaxi | R2 0.96 | 6.3M rows processed and leakage removed from the feature set. |

## Why These Projects Matter For Junior Roles

I am not claiming years of professional ML platform ownership. These projects
show that I can learn the tools, connect them into working systems, explain my
decisions, and notice operational risks that matter in real teams.

For a recruiter, the simple takeaway is:

> I can help build, test, document, and operate ML services while continuing to
> grow under experienced technical guidance.

For a technical reviewer, the deeper evidence is here:

- [Technical Evidence](../technical-evidence.md)
- [Architecture decisions](../architecture/decisions.md)
- [Portfolio status](../PORTFOLIO_STATUS.md)
