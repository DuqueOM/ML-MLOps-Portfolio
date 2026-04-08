<div align="center">

# 🚀 ML/MLOps Portfolio — Production-Ready

**3 ML services · GKE + EKS · 17 ADRs · 395+ tests · Multi-cloud Terraform**

[![CI](https://github.com/DuqueOM/ML-MLOps-Portfolio/actions/workflows/ci-mlops.yml/badge.svg)](https://github.com/DuqueOM/ML-MLOps-Portfolio/actions/workflows/ci-mlops.yml)
[![codecov](https://codecov.io/gh/DuqueOM/ML-MLOps-Portfolio/branch/main/graph/badge.svg)](https://codecov.io/gh/DuqueOM/ML-MLOps-Portfolio)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue?logo=python&logoColor=white)](https://python.org)
[![Kubernetes](https://img.shields.io/badge/K8s-GKE%20%2B%20EKS-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io)
[![Terraform](https://img.shields.io/badge/IaC-Terraform-7B42BC?logo=terraform&logoColor=white)](https://terraform.io)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[![Portfolio Site](https://img.shields.io/badge/%F0%9F%9A%80_Portfolio-Live_Demo-blue?style=for-the-badge)](https://duqueom.github.io/ML-MLOps-Portfolio/)
[![YouTube](https://img.shields.io/badge/Video_Demo-YouTube-red?style=for-the-badge&logo=youtube)](https://youtu.be/7dFFqq2ROPw)

</div>

---

> **A production-grade MLOps portfolio by a career switcher who brings 14 years of operational
> discipline to ML engineering.** Every project demonstrates the complete ML lifecycle —
> from experimentation to production — with the reliability mindset of someone who understands
> that downtime costs real money and poor monitoring creates real problems.

---

## Three Production Incidents. Diagnosed. Documented. Fixed.

```
 81% error rate under load  →  uvicorn --workers N under K8s = CPU thrashing, not parallelism
                                Fixed: asyncio.run_in_executor + ThreadPoolExecutor(4)
                                GIL analysis: sklearn/XGBoost/LightGBM C extensions release GIL
                                Result: 81% errors → 0%, CPU 2000m → 1000m   [ADR-014, ADR-015]

 SHAP returning all zeros   →  TreeExplainer incompatible with StackingClassifier
                                Fixed: KernelExplainer in original 10-feature space (~4.5s opt-in)
                                Evaluated 4 alternatives before deciding               [ADR-010]

 HPA stuck at 3 replicas    →  Memory HPA + fixed ML model RAM footprint
                                = ceil(replicas × constant/target) never decreases below current
                                Fixed: CPU-only HPA, verified 3→1 pods in 8 minutes    [ADR-001]
```

These aren't planned features — they're problems found in production, traced to root cause,
and documented in ADRs so they never happen again.

---

## ML Projects

| Project | Algorithm | Metric | Coverage | Latency p50 (GCP / AWS) |
|---------|-----------|--------|:--------:|:-------:|
| **[BankChurn Predictor](BankChurn-Predictor/)** | StackingClassifier (RF+GB+XGB+LGB→LR) + SHAP | AUC **0.87** | 90% | 200ms / 110ms |
| **[NLPInsight Analyzer](NLPInsight-Analyzer/)** | TF-IDF + LogReg (prod) · FinBERT (GPU opt-in) | Acc **80.6%** | 98% | 78ms / 100ms |
| **[ChicagoTaxi Pipeline](ChicagoTaxi-Demand-Pipeline/)** | PySpark ETL (6.3M rows) + LightGBM | R² **0.96** | 91% | 100ms / 120ms |

> **395+ tests**, **0 failures**, **85% CI threshold enforced**.  
> ChicagoTaxi R² 0.96 uses honest lag features after fixing data leakage — documented in ADR-009.

**Selected "Don't Build" decisions** (harder than building):
- Removed CarVision from portfolio — MAPE 32.9% is not defensible (ADR-009)
- Deferred Feature Store with full architecture design ready for when it's needed (ADR-007)
- Rejected Airflow for drift retraining — K8s CronJob → GitHub Actions is sufficient (ADR-006)

---

## Production Infrastructure

| Component | GCP (GKE) | AWS (EKS) |
|-----------|-----------|-----------|
| **Cluster** | e2-medium, auto-scales 1–5 nodes, `us-central1` | t3.small, auto-scales 1–5 nodes, `us-east-1` |
| **Pods** | 6 Running, 0 restarts | 6 Running, 0 restarts |
| **Ingress** | nginx + static IP | nginx + NLB (AWS Load Balancer Controller) |
| **IAM** | Workload Identity | IRSA |
| **Load Test** | 0% errors, p95 190ms | 0% errors, p95 450ms |
| **Cost** | ~$24/mo (e2-medium, cost-optimized) | ~$145/mo (t3.medium, burst) |

| Stack | Status |
|-------|--------|
| Prometheus | 16 targets UP, 16 alert rules, 15s scrape |
| Grafana | 2 dashboards, 26 panels (latency, throughput, drift, resources) |
| MLflow | 9 experiments tracked across 3 projects |
| Argo Rollouts | Canary deployments (20→50→100%) with auto-rollback |
| Drift Detection | PSI-based CronJob, daily, triggers retraining at PSI ≥ 0.25 |
| Security | Gitleaks + Bandit + Trivy + pip-audit blocking on HIGH |

---

## Architecture Decision Records (17 ADRs)

Every non-trivial decision is documented with context, alternatives evaluated, trade-offs
accepted, and verification evidence. Not explanations of what was built — records of what
was evaluated, rejected, and why.

| Category | ADRs |
|----------|------|
| **Infrastructure & Scaling** | 001 (CPU-only HPA), 002 (emptyDir model storage), 013 (multi-cloud parity), 014 (single-worker pod), 016 (GCP/AWS cost trade-off) |
| **ML Model & Inference** | 003 (StackingClassifier), 005 (dependency pinning), 010 (SHAP KernelExplainer), 015 (async ThreadPool) |
| **MLOps Pipeline** | 004 (OpenTelemetry), 006 (drift-triggered retraining), 007 (Feature Store deferred), 008 (Argo Rollouts canary) |
| **Engineering Discipline** | 009 (simplification + removals), 011 (Gradio exclusion), 012 (security scanner policy), 017 (custom vs managed) |

📐 [View all 17 ADRs →](https://duqueom.github.io/ML-MLOps-Portfolio/architecture/decisions/)

---

## Agentic Development Configuration

This repository includes a production-grade agentic development setup that encodes
the portfolio's 17 ADRs and 3 production incidents directly into the AI development
environment — not as documentation to read, but as behavioral constraints the agent
follows automatically.

```
AGENTS.md           — Project identity, critical DO NOT VIOLATE patterns, HPA targets
.windsurf/
├── rules/          — 7 context-aware rules (glob-triggered per file type)
│   ├── 01-mlops-conventions.md     always_on: core ADR constraints
│   ├── 02-kubernetes.md            k8s/**/*.yaml: HPA targets, single-worker
│   ├── 03-terraform.md             **/*.tf: state management, tagging
│   ├── 04-python-ml.md             **/*.py: async patterns, SHAP, pinning
│   ├── 05-github-actions.md        .github/workflows/: CI standards
│   ├── 06-documentation.md         docs/**/*.md: ADR format, content guidelines
│   └── 07-docker.md                Dockerfile*: multi-stage, non-root, no model bake
├── skills/         — 6 multi-step operational procedures with supplementary data
│   ├── debug-ml-inference/         symptom → root cause → ADR cross-reference
│   ├── deploy-gke/ deploy-aws/     pre/post-deploy checklists + rollback procedures
│   ├── drift-detection/            per-service PSI thresholds + alert integration
│   ├── model-retrain/              validation criteria + acceptance gates per service
│   └── release-checklist/          full multi-cloud release + CHANGELOG template
└── workflows/      — 6 structured prompt workflows (/incident, /retrain, /release,
                      /load-test, /new-adr, /drift-check)
```

The agent knows: 50%/60%/60% CPU targets (not 70%), KernelExplainer for SHAP (not
TreeExplainer), workers=1 (never N) under K8s. Operational knowledge encoded, not
just referenced.

→ [AGENTS.md](AGENTS.md) &nbsp;|&nbsp; [.windsurf/](.windsurf/)

---

## Infrastructure as Code

- **Terraform**: GCP + AWS modules, remote state, `terraform plan` = no drift
- **Kustomize**: Shared base manifests + cloud-specific overlays
- **Testing**: `tfsec` + `checkov` + `conftest` (OPA) + `kube-linter` — 9/9 GCP, 8/8 AWS

---

## CI/CD Pipeline

- **CI**: tests (matrix Python 3.11/3.12) → security (Gitleaks, Bandit) → Docker build (Trivy) → integration tests
- **CD**: `deploy-gcp.yml` + `deploy-aws.yml` — automated multi-cloud deployment on tag push
- **Coverage**: 90–98% enforced at 85% threshold via Codecov

---

## Quick Start

```bash
git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git
cd ML-MLOps-Portfolio
bash scripts/setup_demo_models.sh
docker compose -f docker-compose.demo.yml up -d --build
```

| Service | URL |
|---------|-----|
| BankChurn API | [localhost:8001/docs](http://localhost:8001/docs) |
| NLPInsight API | [localhost:8003/docs](http://localhost:8003/docs) |
| ChicagoTaxi API | [localhost:8004/docs](http://localhost:8004/docs) |
| MLflow UI | [localhost:5000](http://localhost:5000) |

---

## Documentation

| Document | Description |
|----------|-------------|
| **[Portfolio Site](https://duqueom.github.io/ML-MLOps-Portfolio/)** | Full docs with screenshots, load test results, API evidence |
| **[17 ADRs](https://duqueom.github.io/ML-MLOps-Portfolio/architecture/decisions/)** | All architectural decisions with context, alternatives, consequences |
| **[AGENTS.md](AGENTS.md)** | Agentic development configuration |
| **[ENGINEERING_HIGHLIGHTS.md](ENGINEERING_HIGHLIGHTS.md)** | Quick reference: incidents, trade-offs, key decisions |
| **[RUNBOOK.md](RUNBOOK.md)** | Copy-paste commands for common operations |

---

## AI Transparency

Built using Windsurf Cascade for code generation and boilerplate. All architectural
decisions, system design, trade-off analysis, and incident resolution are the author's.
The `.windsurf/` configuration constrains the agent with documented decisions — demonstrating
that AI tooling can be governed, not just used.

---

<div align="center">

**Built by [Duque Ortega Mutis](https://github.com/DuqueOM)** | [LinkedIn](https://linkedin.com/in/duqueom) | [Video Demo](https://youtu.be/7dFFqq2ROPw)

*Portfolio v3.6.0 — April 2026 — Deployed on GCP (GKE) + AWS (EKS)*

</div>