# 🚀 ML/MLOps Portfolio — Production-Ready

<div align="center">

**Enterprise-Grade Machine Learning & MLOps Portfolio**

*3 Production-Ready Projects • Unified CI/CD • Full Observability Stack*

[![Portfolio Site](https://img.shields.io/badge/🌐_Portfolio-Live_Site-blue?style=for-the-badge)](https://duqueom.github.io/ML-MLOps-Portfolio/)
[![YouTube Demo](https://img.shields.io/badge/📺_Demo-YouTube-red?style=for-the-badge&logo=youtube)](https://youtu.be/qmw9VlgUcn8)

---

[![CI Pipeline](https://github.com/DuqueOM/ML-MLOps-Portfolio/actions/workflows/ci-mlops.yml/badge.svg)](https://github.com/DuqueOM/ML-MLOps-Portfolio/actions/workflows/ci-mlops.yml)
[![codecov](https://codecov.io/gh/DuqueOM/ML-MLOps-Portfolio/branch/main/graph/badge.svg)](https://codecov.io/gh/DuqueOM/ML-MLOps-Portfolio)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](docker-compose.demo.yml)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-6.2.1-brightgreen.svg)](docs/FEATURES.md)

[![MLflow](https://img.shields.io/badge/MLflow-Tracking-0194E2.svg?logo=mlflow)](https://mlflow.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![GCP](https://img.shields.io/badge/GCP-Deployed-4285F4.svg?logo=googlecloud&logoColor=white)](docs/GCP_PRODUCTION_GUIDE.md)
[![AWS](https://img.shields.io/badge/AWS-Ready-FF9900.svg?logo=amazonaws&logoColor=white)](docs/AWS_PRODUCTION_GUIDE.md)
[![Kubernetes](https://img.shields.io/badge/K8s-GKE_%2B_EKS-326CE5.svg?logo=kubernetes&logoColor=white)](k8s/)
[![Terraform](https://img.shields.io/badge/Terraform-Multi--Cloud-7B42BC.svg?logo=terraform&logoColor=white)](infra/terraform/)
[![Prometheus](https://img.shields.io/badge/Prometheus-Metrics-E6522C.svg?logo=prometheus&logoColor=white)](infra/prometheus-config.yaml)
[![Grafana](https://img.shields.io/badge/Grafana-Dashboards-F46800.svg?logo=grafana&logoColor=white)](infra/grafana/)

</div>

---

## ⚡ 30-Second Pitch

> After **14 years managing high-pressure operations** in hospitality and logistics, I discovered that the principles that make great operational systems—reliability, monitoring, reproducibility—are the same ones that make great ML systems.
>
> This portfolio demonstrates that transition: **not just ML models that achieve good metrics, but production-ready systems** built with the discipline of someone who understands that downtime costs real money and poor monitoring creates real problems.
>
> Every project here answers the question: ***"Would I trust this in production at 2am?"***

<div align="center">

![Portfolio Demo](docs/media/gifs/01-demo-prediccion.gif)

*End-to-end walkthrough: GCP deployment, ML predictions, monitoring, and CI/CD pipeline*

</div>

---

## 📊 Key Metrics

| Project | Type | Best Metric | Coverage | API Latency | Key Features |
|---------|------|-------------|----------|-------------|--------------|
| [🏦 BankChurn](BankChurn-Predictor/) | Classification | **AUC 0.87**, F1 0.64 | 85% | <50ms p95 | Ensemble, XGBoost, LightGBM, PyTorch MLP, SHAP |
| [🚗 CarVision](CarVision-Market-Intelligence/) | Regression | **R² 0.70**, RMSE $4.4K | 86% | <30ms p95 | LightGBM, XGBoost, PyTorch MLP, Streamlit |
| [📱 TelecomAI](TelecomAI-Customer-Intelligence/) | Classification | **Acc 82%**, AUC 0.84 | 91% | <25ms p95 | XGBoost, LightGBM, PyTorch MLP, Revenue Opt |

| Infrastructure | Status | Details |
|----------------|--------|---------- |
| **GCP Deployment** | ✅ Live | GKE cluster, 6 pods, Artifact Registry, Cloud Storage |
| **AWS Deployment** | 🟡 Ready | EKS + ECR + S3 + RDS — Terraform + K8s overlays complete |
| **CI/CD** | ✅ Unified | GitHub Actions → GKE + EKS (separate deploy workflows) |
| **IaC** | ✅ Multi-Cloud | Terraform (GCP + AWS) — parallel provider configs |
| **Monitoring** | ✅ Full Stack | Prometheus + Grafana + MLflow — cloud-agnostic on K8s |
| **Security** | ✅ Automated | Gitleaks, Bandit, Trivy, pip-audit — all enforced in CI |

---

## 🌟 TOP-3: Production-Ready Projects

### 🏦 1. [BankChurn Predictor](BankChurn-Predictor/) — Customer Churn Prediction

Production-grade churn prediction enabling proactive retention campaigns with **87% AUC** discrimination. VotingClassifier ensemble with SHAP explainability, SMOTE handling, and MLflow tracking (3 experiments).

| AUC-ROC | F1 | Precision | Recall | Coverage | Latency |
|---------|-----|-----------|--------|----------|---------|
| **0.87** | 0.64 | 0.72 | 0.58 | 85% | <50ms p95 |

[📂 Project](BankChurn-Predictor/) · [📄 Model Card](BankChurn-Predictor/models/model_card.md) · [📺 Video](https://youtu.be/qmw9VlgUcn8)

---

### 🚗 2. [CarVision Market Intelligence](CarVision-Market-Intelligence/) — Vehicle Price Prediction

End-to-end vehicle valuation platform with **Streamlit BI Dashboard** (4 tabs) and REST API. Centralized `FeatureEngineer` prevents train-serve skew. Advanced validation with bootstrap CIs and temporal backtesting.

| R² | RMSE | MAE | MAPE | Coverage | Dashboard |
|----|------|-----|------|----------|-----------|
| **0.70** | $4,396 | $3,124 | 18.2% | 86% | <2s load |

[📂 Project](CarVision-Market-Intelligence/) · [📄 Model Card](CarVision-Market-Intelligence/models/model_card.md) · [📺 Video](https://youtu.be/qmw9VlgUcn8)

---

### 📱 3. [TelecomAI Customer Intelligence](TelecomAI-Customer-Intelligence/) — Plan Recommendation

Strategic plan optimization reducing **$6.9M/year** revenue leakage per 100K customers. Ensemble of LogReg + GradientBoosting + RandomForest with threshold tuning for business-aligned predictions. 1,200 RPS throughput.

| Accuracy | AUC-ROC | F1 | Precision | Coverage | Throughput |
|----------|---------|-----|-----------|----------|------------|
| **82%** | 0.84 | 0.63 | 0.72 | 91% | 1,200 RPS |

[📂 Project](TelecomAI-Customer-Intelligence/) · [📄 Model Card](TelecomAI-Customer-Intelligence/models/model_card.md) · [📺 Video](https://youtu.be/qmw9VlgUcn8)

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|-------------|
| **ML/DS** | Scikit-learn, XGBoost, LightGBM, PyTorch, Pandas, NumPy, SHAP, Optuna |
| **MLOps** | MLflow (9 experiments), DVC, Docker, Kubernetes, Terraform |
| **API & Dashboard** | FastAPI, Pydantic, Streamlit, Plotly |
| **Cloud & IaC** | GCP (GKE, GCS, AR, Cloud SQL), AWS (EKS, S3, ECR, RDS), Terraform, K8s |
| **Monitoring** | Prometheus, Grafana, Evidently (drift detection), CloudWatch |
| **CI/CD** | GitHub Actions (CI + GCP deploy + AWS deploy), Artifact Registry, ECR, Codecov |
| **Security** | Gitleaks, Bandit, Trivy, pip-audit |
| **Testing** | pytest (85-91% coverage), Codecov, pre-commit hooks |

> **v6.0+ Performance Optimizations**: Joblib compression (-76% model size), Pandas dtype optimization (-56% memory), sklearn parallelization (2-4x faster), vectorized batch predictions (-84% time). Full details in [docs/FEATURES.md](docs/FEATURES.md).

For system architecture diagrams, CI/CD pipeline details, and infrastructure specs, see [docs/ARCHITECTURE_PORTFOLIO.md](docs/ARCHITECTURE_PORTFOLIO.md).

---

## 🚀 Quick Start

```bash
# 1. Clone and enter
git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git && cd ML-MLOps-Portfolio

# 2. Generate demo models (first time only, ~2 min)
bash scripts/setup_demo_models.sh

# 3. Start full stack (APIs + MLflow + Dashboard, ~3 min build)
docker compose -f docker-compose.demo.yml up -d --build

# 4. Wait for services and verify health (~60s)
sleep 60 && bash scripts/run_demo_tests.sh

# 5. Access services
#    🏦 BankChurn API:    http://localhost:8001/docs
#    🚗 CarVision API:    http://localhost:8002/docs
#    🚗 CarVision UI:     http://localhost:8501
#    📱 TelecomAI API:    http://localhost:8003/docs
#    📊 MLflow:           http://localhost:5000
```

For API examples, monitoring setup, and troubleshooting, see [QUICK_START.md](QUICK_START.md) and [RUNBOOK.md](RUNBOOK.md).

---

## ☁️ Multi-Cloud Production Deployment

This portfolio demonstrates **cloud-agnostic MLOps** — the same ML system deployed on **both GCP and AWS**:

<div align="center">

![GKE Workloads Running](docs/media/screenshots/gcp-console/05-gke-workloads-running.png)

*6 services running simultaneously on GKE: 3 ML APIs + MLflow + Prometheus + Grafana*

</div>

### Multi-Cloud Architecture

| Component | GCP (Live) | AWS (Ready) |
|-----------|-----------|-------------|
| **K8s Cluster** | GKE (`us-central1`) ✅ | EKS (`us-east-1`) 🟡 |
| **Container Registry** | Artifact Registry ✅ | ECR 🟡 |
| **Model Storage** | Cloud Storage (GCS) ✅ | S3 (versioned + Glacier lifecycle) 🟡 |
| **Database** | Cloud SQL (Postgres) ✅ | RDS (Postgres) 🟡 |
| **Load Balancer** | GCE Ingress (static IP) ✅ | ALB (DNS) 🟡 |
| **IAM for Pods** | Workload Identity ✅ | IRSA 🟡 |
| **Init Containers** | GCS download (`google-cloud-storage`) ✅ | S3 download (`boto3`) 🟡 |
| **CI/CD** | `deploy-gcp.yml` ✅ | `deploy-aws.yml` 🟡 |
| **IaC** | `infra/terraform/gcp/` ✅ | `infra/terraform/aws/` 🟡 |
| **Monitoring** | Prometheus + Grafana + MLflow ✅ | Same stack (cloud-agnostic) 🟡 |

> **Cloud-Agnostic Design**: Monitoring stack (Prometheus, Grafana, MLflow), K8s deployment patterns (HPA, anti-affinity, health probes), and CI/CD structure are identical across clouds. Only the init container SDK and ingress annotations change.

> **💰 Cost-Aware**: Full GCP stack runs at ~$51 USD/month (3 nodes, 6 pods, monitoring + CI/CD). See [detailed cost analysis](docs/ARCHITECTURE_PORTFOLIO.md#-production-infrastructure--cost-analysis).

<div align="center">

[![🎬 Video Demo](https://img.shields.io/badge/🎬_Full_Demo-YouTube_(4_min)-red?style=for-the-badge&logo=youtube)](https://youtu.be/qmw9VlgUcn8)

</div>

<details>
<summary><strong>📊 GCP Evidence (click to expand)</strong></summary>

#### Terraform IaC — Infrastructure synchronized
![Terraform Plan](docs/media/screenshots/terraform/53-terraform-plan-no-changes.png)

#### Monitoring — Grafana Dashboard
![Grafana](docs/media/screenshots/monitoring/34-grafana-dashboard.png)

#### CI/CD — GitHub Actions Pipeline Completed
![CI/CD](docs/media/screenshots/cicd/46-workflow-completado.png)

#### ML Prediction in Production
![Prediction](docs/media/screenshots/apis/26-bankchurn-prediccion-real.png)

</details>

<details>
<summary><strong>🟡 AWS Infrastructure (click to expand)</strong></summary>

#### Terraform AWS — EKS + VPC + S3 + RDS + ECR
- Full Terraform config: [`infra/terraform/aws/`](infra/terraform/aws/)
- EKS cluster with managed node groups (t3.large)
- S3 buckets with versioning, encryption, and Glacier lifecycle
- RDS PostgreSQL for MLflow backend
- ECR repositories with lifecycle policies

#### K8s Overlay — AWS-Specific Manifests
- ALB Ingress: [`k8s/overlays/aws/ingress-aws.yaml`](k8s/overlays/aws/ingress-aws.yaml)
- S3 Download Script: [`k8s/overlays/aws/download-script-aws.yaml`](k8s/overlays/aws/download-script-aws.yaml)
- IRSA Service Account: [`k8s/overlays/aws/serviceaccount-aws.yaml`](k8s/overlays/aws/serviceaccount-aws.yaml)

#### Deploy Workflow
- [`deploy-aws.yml`](.github/workflows/deploy-aws.yml): GitHub Actions → ECR → EKS

</details>

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[Quick Start](QUICK_START.md)** | 5-minute demo with API examples and health checks |
| **[Architecture](docs/ARCHITECTURE_PORTFOLIO.md)** | System design, Mermaid diagrams, infrastructure, CI/CD workflow |
| **[GCP Production Guide](docs/GCP_PRODUCTION_GUIDE.md)** | Full GKE deployment walkthrough (12 phases) |
| **[AWS Production Guide](docs/AWS_PRODUCTION_GUIDE.md)** | Full EKS deployment walkthrough (11 phases) |
| **[Deployment Evidence](docs/GCP_DEPLOYMENT_EVIDENCE.md)** | 168+ screenshots, 13 GIFs, multi-cloud video script |
| **[Operations Runbook](RUNBOOK.md)** | Day-to-day commands, Docker, K8s, Terraform deployment |
| **[Features & Changelog](docs/FEATURES.md)** | Performance optimizations, new features (v6.0–v6.1) |
| **[Release Process](docs/RELEASE.md)** | GHCR publishing, blue/green deployments, rollback procedures |
| **[Contributing](docs/contributing/guidelines.md)** | Development workflow, code standards, PR process |
| **[Security Policy](SECURITY.md)** | Vulnerability reporting and scanning details |

---

## 🔧 Development Process

This portfolio was developed using **AI-assisted tools** (Cursor / Cascade) for code generation and boilerplate acceleration. All architectural decisions, project selection, MLOps pipeline design, infrastructure choices, and system integration were made by the author.

AI tools were used as **accelerators, not replacements** for understanding — the same way senior engineers use code completion and documentation generators to increase throughput while retaining full ownership of design decisions.

The author maintains and operates all systems independently, including CI/CD pipeline debugging, Docker optimization, Terraform configuration, and production monitoring setup.

---

## 👤 Author

**Duque Ortega Mutis (DuqueOM)**
*Machine Learning & MLOps Engineer*

14 years of operational experience transitioning to ML engineering with a focus on production-ready systems, reliability, and operational excellence.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat&logo=linkedin)](https://linkedin.com/in/duqueom)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?style=flat&logo=github)](https://github.com/DuqueOM)
[![Portfolio](https://img.shields.io/badge/Portfolio-Visit-green?style=flat)](https://duqueom.github.io/ML-MLOps-Portfolio/)
[![Email](https://img.shields.io/badge/Email-Contact-red?style=flat&logo=gmail)](mailto:DuqueOrtegaMutis@gmail.com)

---

<div align="center">

**Portfolio Version**: 6.2.1 · **License**: MIT · **Status**: ✅ Production-Ready (GCP) · 🟡 AWS Ready

*Building ML systems that work at 2am* 🌙

</div>
