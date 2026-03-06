# ML-MLOps Portfolio Documentation

**ML/MLOps portfolio with 3 deployed projects** — GKE + EKS, GitHub Actions CI/CD, Prometheus + Grafana + MLflow.

[![GitHub](https://img.shields.io/badge/📁_Code-Repository-181717?style=for-the-badge&logo=github)](https://github.com/DuqueOM/ML-MLOps-Portfolio)
[![YouTube](https://img.shields.io/badge/📺_Video-Demo-red?style=for-the-badge&logo=youtube)](https://youtu.be/qmw9VlgUcn8)

![Portfolio Demo](media/gifs/01-demo-prediccion.gif)

---

## Projects (v3.5.0, Python 3.11.14)

| Project | Algorithm | Primary Metric | Tests | Coverage |
|---------|-----------|----------------|:-----:|:--------:|
| **[BankChurn](projects/bankchurn.md)** | StackingClassifier (RF+GB+XGB+LGB→LR) + SHAP | AUC 0.87 | 199 | 90% |
| **[NLPInsight](projects/nlpinsight.md)** | TF-IDF + LogReg (prod) / FinBERT (GPU) | Acc 80.6% | 74 | 98% |
| **[ChicagoTaxi](projects/chicagotaxi.md)** | PySpark ETL + RandomForest (6.3M rows) | R² 0.96 | 22 | 91% |

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
| MLflow UI | [localhost:5000](http://localhost:5000) |

## Technology Stack

| Layer | Technologies |
|-------|-------------|
| **ML** | scikit-learn 1.8.0, LightGBM 4.6+, HuggingFace Transformers, SHAP 0.50.0 |
| **API** | FastAPI, Pydantic |
| **Tracking** | MLflow 3.10, DVC |
| **Monitoring** | Prometheus, Grafana, Evidently AI, OpenTelemetry |
| **Responsible AI** | Fairness audits (×3), drift detection (KS+PSI+Evidently), Pandera validation |
| **Containers** | Docker (multi-stage), Kubernetes (GKE/EKS) |
| **IaC** | Terraform (GCP + AWS modules) |
| **CI/CD** | GitHub Actions, Trivy, Bandit, Gitleaks |
| **Testing** | pytest (90–98%, 294+ tests), Locust, Codecov |

## Production Infrastructure

| Metric | GCP (GKE) | AWS (EKS) |
|--------|-----------|-----------|
| **Pods** | 6 (3 APIs with HPA + MLflow + Prometheus + Grafana) | 6 |
| **Nodes** | 4 × e2-medium | 2 × t3.large |
| **Cost** | ~$51/month | ~$170/month |
| **Uptime** | 99.9%+ | 99.9%+ |

## Documentation

| Document | Description |
|----------|-------------|
| [Quick Start](getting-started/quickstart.md) | Get running in 5 minutes |
| [Architecture](ARCHITECTURE_PORTFOLIO.md) | System design and cost analysis |
| [Model Catalog](models/catalog.md) | Production model registry |
| [API Reference](api/rest-apis.md) | REST API documentation |
| [Operations](operations/deployment.md) | Deployment and monitoring |
| [Troubleshooting](operations/troubleshooting.md) | Common issues |

## AI Transparency

Developed using AI-assisted tools (Cursor/Cascade) for code generation acceleration. All architectural decisions, MLOps design, and infrastructure choices made by the author.

---

**Built by [Duque Ortega Mutis](https://github.com/DuqueOM)** | [Source Code](https://github.com/DuqueOM/ML-MLOps-Portfolio) | [Video Demo](https://youtu.be/qmw9VlgUcn8)

*Last Updated: March 2026 — v3.5.0*
