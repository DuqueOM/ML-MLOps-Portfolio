# Projects

<div class="portfolio-page" markdown="1">

<div class="portfolio-hero" markdown="1">
<canvas data-neural-scene="helm" aria-hidden="true"></canvas>
<span class="portfolio-eyebrow">Projects · what I built and how</span>

# ML services in production, an LLM agent and a voice app

Three ML services I deployed to GKE and EKS, with the problems I
found and fixed in load tests on my own clusters; a WhatsApp customer-service agent, in progress; and
`read_aloud`, a text-to-speech app I use every day. I design the system and make
the decisions; I use AI coding agents (Claude Code) for speed. Each section says
which parts the agents wrote.

<div class="portfolio-actions" markdown="1">
[ML-MLOps Portfolio](#the-ml-mlops-portfolio){ .portfolio-button .portfolio-button--primary }
[WhatsApp agent](#whatsapp-customer-service-agent){ .portfolio-button }
[read_aloud](#read_aloud){ .portfolio-button }
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
Prometheus + Grafana monitoring, and the incident write-ups. Deployed to GKE
and EKS in March 2026, then shut down to save costs. I designed the
architecture and made the decisions; AI coding agents helped me build it faster.

395+ automated tests and 19 architecture decision records hold it together —
every non-trivial choice is documented with the alternatives it rejected.

</div>
<div class="portfolio-callout" markdown="1">
<strong>How to review it</strong>

Pick one service and follow its evidence chain: metrics → serving path →
deployment → incident. The debugging deep dive on BankChurn is the
strongest 10-minute read.
</div>
</div>

<div class="portfolio-media portfolio-media--demo" markdown="1">
<img src="../media/gifs/portfolio-demo.gif" alt="Portfolio deployment walkthrough — full build, test and serve cycle" loading="lazy">
</div>

The three services inside the portfolio — each with its own deep-dive page.
Hover to hold, drag to browse, or click a card to bring it to center:

<div class="portfolio-card-grid" data-pf-marquee markdown="1">
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
<span class="portfolio-badge">PySpark · temporal split</span>
</div>
<p>Demand forecasting at scale with strictly temporal validation — and the
data leak I found and fixed: R² went from 0.905 to 0.965 with honest lag features.</p>

[ChicagoTaxi Pipeline](chicagotaxi.md){ .portfolio-button }
</div>
</div>

All the infrastructure, testing, security and monitoring proof behind the
portfolio lives in one place:

<div class="portfolio-actions" markdown="1">
[:fontawesome-solid-flask: Evidence](../technical-evidence.md){ .portfolio-button .portfolio-button--primary }
[:fontawesome-solid-cloud: Deployment](../DEPLOYMENT_EVIDENCE.md){ .portfolio-button }
[:fontawesome-solid-circle-check: Status](https://github.com/DuqueOM/ML-MLOps-Portfolio/blob/main/PORTFOLIO_STATUS.md){ .portfolio-button }
[:fontawesome-solid-diagram-project: ADRs](../architecture/decisions.md){ .portfolio-button }
[:fontawesome-brands-github: Repository](https://github.com/DuqueOM/ML-MLOps-Portfolio){ .portfolio-button }
</div>

## WhatsApp customer-service agent

<div class="portfolio-split" markdown="1">
<div markdown="1">

A WhatsApp customer-service agent for a small business, **in progress**. Built
with PHP 8.3 and MySQL on the Meta Cloud API: webhooks with signature
validation, idempotent message storage, LLM tool calling so the agent can look
up real data, human handoff when the bot should not answer, and evals to
measure the answers.

I wrote the spec and the plan, and I write the core logic. AI agents generate
the scaffolding, which I review personally. First release planned for January
2027.

</div>
<div class="portfolio-callout" markdown="1">
<strong>Why this project</strong>

It has the same shape as real junior AI engineer work: an LLM inside a
product, with tools, a human in the loop and a way to measure quality.
</div>
</div>

<div class="portfolio-actions" markdown="1">
[:fontawesome-brands-github: agent-whatsapp-php](https://github.com/DuqueOM/agent-whatsapp-php){ .portfolio-button .portfolio-button--primary }
</div>

## read_aloud

<div class="portfolio-split" markdown="1">
<div markdown="1">

A Windows text-to-speech app **I use every day**. It reads selected text aloud
with local neural voices (Piper, Qwen3-TTS), in Spanish and English in the same
text, offline.

One of its voices I fine-tuned myself: a Qwen3-TTS voice trained with LoRA on
my own GPU (RTX 5070 Laptop GPU, 8 GB). I chose the training setup and the final epoch,
and used WavLM to compare the voices. 15 ADRs record the decisions. Built with
AI coding agents.

</div>
<div class="portfolio-callout" markdown="1">
<strong>What to look at</strong>

The ADRs on the LoRA training and the epoch choice, and how WavLM compares
voices.
</div>
</div>

<div class="portfolio-media portfolio-media--demo" markdown="1">
<img src="https://raw.githubusercontent.com/DuqueOM/read_aloud/main/docs/media/demo.gif" alt="read_aloud demo: selected text is read aloud and each sentence is highlighted" loading="lazy">
</div>

<div class="portfolio-actions" markdown="1">
[:fontawesome-brands-github: read_aloud](https://github.com/DuqueOM/read_aloud){ .portfolio-button .portfolio-button--primary }
</div>

## Architecture studies

Larger systems I designed and directed. AI coding agents wrote most of the code.
Not deployed to a cloud. Each one has its own page for readers who want the details.

```
ml-service-template  →  a Copier template for one classical ML service on Kubernetes (GKE/EKS)
ml-platform          →  a multi-project ML platform template: tabular, deep learning, LLM/RAG, agents
agent-local          →  a local LLM agent core with grammar-constrained routing and a policy gate
```

<div class="portfolio-actions" markdown="1">
[ml-service-template](../template.md){ .portfolio-button }
[ml-platform](../ml-platform.md){ .portfolio-button }
[agent-local](../agent-local.md){ .portfolio-button }
[How the three relate](../related-projects.md){ .portfolio-button }
</div>
<br>
</div>
