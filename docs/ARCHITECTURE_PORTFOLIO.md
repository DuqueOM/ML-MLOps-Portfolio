# Portfolio Architecture

**3 ML projects deployed end-to-end** — trained, containerized, served on GKE + EKS, monitored via Prometheus + Grafana.

[![YouTube Demo](https://img.shields.io/badge/📺_Video-Watch_Demo-red?style=for-the-badge&logo=youtube)](https://youtu.be/qmw9VlgUcn8)

---

## System Overview

| Principle | Implementation |
|-----------|---------------|
| **Modularity** | Each project is self-contained with its own pipeline |
| **Consistency** | Shared patterns: `src/` layout, Pydantic config, FastAPI |
| **Observability** | MLflow + Prometheus + Grafana |
| **Security** | Gitleaks, Bandit, Trivy, pip-audit |
| **Scalability** | Kubernetes HPA, CPU-based autoscaling |

## Projects (v3.5.0, Python 3.11.14 + sklearn 1.8.0)

| Project | Algorithm | Primary Metric | In-Pod Latency | Tests | Coverage |
|---------|-----------|----------------|---------------|:-----:|:--------:|
| **BankChurn** | StackingClassifier (RF+GB+XGB+LGB→LR) | AUC 0.87 | 103ms p50 | 199 | 90% |
| **NLPInsight** | TF-IDF + LogReg (prod) / FinBERT (GPU) | Acc 80.6% | 5ms p50 | 74 | 98% |
| **ChicagoTaxi** | PySpark ETL + RandomForest (lag features) | R² 0.9649 | 75ms p50 | 22 | 91% |

## Infrastructure

- **Containers**: Multi-stage Docker builds, non-root execution, `--no-deps` for heavy packages
- **Orchestration**: GKE (GCP) + EKS-ready (AWS), Terraform IaC
- **Model Delivery**: GCS → Init Container → Pod (ConfigMap-driven paths)
- **CI/CD**: GitHub Actions (tests → security → docker build → Trivy scan → integration)
- **Monitoring**: Prometheus (15s scrape, 16/16 targets UP, 16 alert rules) → Grafana (2 auto-provisioned dashboards, 25 panels total)

## GCP Production Cost (~$51/month)

| Service | Cost | % |
|---------|------|---|
| Compute Engine (4× e2-medium) | $20.50 | 40% |
| GKE management | $13.35 | 26% |
| Container Scanning | $9.10 | 18% |
| Networking | $6.15 | 12% |
| Cloud SQL (MLflow) | $1.70 | 3% |

> Covered by Free Tier credits. Optimized with single-zone cluster, e2-medium nodes, and cleanup policies.

## Technology Stack

| Layer | Technologies |
|-------|-------------|
| **ML** | scikit-learn 1.8.0, LightGBM 4.6+, HuggingFace Transformers, SHAP 0.50.0 |
| **API** | FastAPI, uvicorn, Pydantic |
| **Tracking** | MLflow 3.10, DVC |
| **Monitoring** | Prometheus, Grafana, Evidently AI, OpenTelemetry |
| **Responsible AI** | Fairness audits (×3), drift detection (KS+PSI+Evidently), Pandera validation |
| **Containers** | Docker, Kubernetes (GKE/EKS) |
| **IaC** | Terraform (GCP + AWS modules) |
| **CI/CD** | GitHub Actions, Trivy, Bandit, Gitleaks |
| **Testing** | pytest (90–98% coverage, 295+ tests), Locust (load testing, 2,675 requests, 0% errors) |

## Visual Evidence

| GKE Workloads | Grafana Monitoring | MLflow Experiments |
|---------------|-------------------|-------------------|
| ![GKE](https://raw.githubusercontent.com/DuqueOM/ML-MLOps-Portfolio/main/docs/media/screenshots/gcp-console/05-gke-workloads-running.png) | ![Grafana](https://raw.githubusercontent.com/DuqueOM/ML-MLOps-Portfolio/main/docs/media/screenshots/monitoring/34-grafana-dashboard.png) | ![MLflow](https://raw.githubusercontent.com/DuqueOM/ML-MLOps-Portfolio/main/docs/media/screenshots/monitoring/39-mlflow-experiments.png) |

## Related Docs

- [Model Catalog](models/catalog.md) — Production model registry
- [Deployment Evidence](DEPLOYMENT_EVIDENCE.md) — Multi-cloud verification
- [API Reference](api/rest-apis.md) — REST API documentation
- [Quick Start](getting-started/quickstart.md) — Get running in 5 minutes

---

*Last Updated: March 2026 — Portfolio v3.5.0*
