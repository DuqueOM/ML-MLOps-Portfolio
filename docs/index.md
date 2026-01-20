# ML-MLOps Portfolio Documentation
**Production-Ready Machine Learning Projects with Enterprise MLOps**

![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)
![MLflow](https://img.shields.io/badge/MLflow-Tracking-0194E2?style=for-the-badge)
[![GitHub Repository](https://img.shields.io/badge/📁_Full_Code-Repository-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/DuqueOM/ML-MLOps-Portfolio)
[![YouTube Demo](https://img.shields.io/badge/📺_Video-Watch_Demo-red?style=for-the-badge&logo=youtube)](https://youtu.be/qmw9VlgUcn8)

---

## 🎬 Portfolio Demo
![Portfolio Demo](media/gifs/portfolio-demo.gif)
**End-to-end demonstration** of the complete ML/MLOps stack: MLflow experiments, Docker Compose orchestration, FastAPI services, Streamlit dashboard, and Prometheus monitoring.

---

## 📖 What Is This Portfolio?

This is a **production-grade MLOps platform** showcasing enterprise best practices for deploying machine learning systems at scale. Unlike typical data science portfolios that stop at model training, this repository demonstrates the complete ML lifecycle: from data versioning and experiment tracking to containerized deployment, monitoring, and CI/CD automation.

**Built for:** Recruiters, hiring managers, ML engineers, and data scientists evaluating production ML capabilities.

### 💡 What You'll Find Here

<div class="grid cards" markdown>

-   🤖 **3 Production ML Projects**

    ---

    Complete end-to-end systems with APIs, dashboards, and monitoring

-   🏗️ **Enterprise Infrastructure**

    ---

    Terraform (AWS), Kubernetes manifests, Docker multi-stage builds

-   🔄 **Full CI/CD Pipeline**

    ---

    GitHub Actions with matrix testing, security scanning, automated deployment

-   📊 **MLOps Best Practices**

    ---

    MLflow tracking, DVC versioning, Prometheus + Grafana observability

-   🧪 **High Test Coverage**

    ---

    79-97% coverage with Pytest, integration tests, security scans

-   📚 **Comprehensive Docs**

    ---

    Model Cards v2.0, Data Cards, Architecture diagrams, Runbooks

</div>

---

## 🚀 Quick Navigation

<div class="grid cards" markdown>

-   🎯 **Getting Started**

    ---

    Get up and running in 5 minutes with Docker

    [➜ Quick Start Guide](getting-started/quickstart.md)

-   📊 **Projects**

    ---

    Explore 3 production-ready ML projects

    [➜ Project Overview](projects/overview.md)

-   🏗️ **Architecture**

    ---

    System design, data flow, CI/CD pipeline

    [➜ Architecture Docs](architecture/overview.md)

-   🔌 **API Reference**

    ---

    Complete REST API documentation

    [➜ API Documentation](api/rest-apis.md)

-   📈 **Operations**

    ---

    Deployment, monitoring, troubleshooting

    [➜ Operations Guide](operations/deployment.md)

-   📚 **Model Catalog**

    ---

    Registry of trained models and metadata

    [➜ Model Catalog](models/catalog.md)

</div>

---

## 📋 Portfolio Overview

This portfolio showcases **3 production-ready ML systems** demonstrating enterprise-grade MLOps practices:

| Project | Domain | Type | Best Metrics | Key Features |
|---------|--------|------|--------------|--------------|
| **[BankChurn Predictor](projects/bankchurn.md)** | Banking | Classification | AUC=0.853, F1=0.604 | SHAP explainability, drift detection, 79% test coverage |
| **[CarVision Market Intelligence](projects/carvision.md)** | Automotive | Regression | R²=0.766, RMSE=$4,794 | Interactive dashboard, 4 tabs, 97% test coverage |
| **[TelecomAI Customer Intelligence](projects/telecom.md)** | Telecom | Classification | AUC=0.84, Acc=82% | Plan optimization, threshold tuning, 97% coverage |

---

## 🎯 Key Capabilities Demonstrated

### Machine Learning Excellence

- ✅ **Advanced Algorithms**: Ensemble methods (VotingClassifier, RandomForest, GradientBoosting)
- ✅ **Imbalanced Data**: SMOTE, class weights, threshold optimization
- ✅ **Feature Engineering**: Centralized FeatureEngineer class (CarVision)
- ✅ **Model Validation**: 5-fold CV, bootstrap CI, temporal backtest
- ✅ **Explainability**: SHAP values, feature importance, business insights

### MLOps & DevOps

- ✅ **Experiment Tracking**: MLflow server with 9 tracked runs (3 per project)
- ✅ **Data Versioning**: DVC for dataset management and lineage
- ✅ **CI/CD Pipeline**: Unified GitHub Actions workflow
  - Matrix testing (3 projects × 2 Python versions)
  - Quality gates (Black, Flake8, Mypy, Bandit)
  - Security scans (Trivy, Gitleaks, pip-audit)
  - E2E tests with full stack validation
- ✅ **Containerization**: Multi-stage Docker builds, GHCR registry
- ✅ **Orchestration**: Kubernetes manifests, Terraform (AWS EKS)

### Software Engineering

- ✅ **Modern Python**: `src/` layout, Pydantic config, type hints
- ✅ **Testing**: Comprehensive suites (unit, integration, e2e) with 79-97% coverage
- ✅ **Code Quality**: Pre-commit hooks, automated linting, security scanning
- ✅ **Documentation**: Model cards, data cards, API docs, operations runbooks

---

## ⚡ Quick Start (5 Minutes)

### Prerequisites

- **Docker** and **Docker Compose** installed
- **8GB RAM** minimum (16GB recommended)
- **20GB disk space**

### One-Command Demo

```bash
# Clone repository
git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git
cd ML-MLOps-Portfolio

# Generate demo models (first-time only)
bash scripts/setup_demo_models.sh

# Start full stack (3 APIs + Dashboard + MLflow)
docker-compose -f docker-compose.demo.yml up -d --build

# Verify services (wait 30s for startup)
docker-compose -f docker-compose.demo.yml ps
```

### Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **🏦 BankChurn API** | [http://localhost:8001/docs](http://localhost:8001/docs) | Churn prediction (Swagger UI) |
| **🚗 CarVision API** | [http://localhost:8002/docs](http://localhost:8002/docs) | Vehicle pricing (Swagger UI) |
| **🚗 CarVision Dashboard** | [http://localhost:8501](http://localhost:8501) | Interactive analytics (Streamlit) |
| **📱 TelecomAI API** | [http://localhost:8003/docs](http://localhost:8003/docs) | Plan recommendation (Swagger UI) |
| **📊 MLflow UI** | [http://localhost:5000](http://localhost:5000) | Experiment tracking |

---

## 📊 Technology Stack

### Core ML & Data

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.11+ |
| **ML Frameworks** | Scikit-learn 1.3+, XGBoost, Optuna |
| **Data Processing** | Pandas, NumPy, Pydantic |
| **Feature Engineering** | Custom FeatureEngineer classes |

### MLOps & Infrastructure

| Component | Technology |
|-----------|-----------|
| **Experiment Tracking** | MLflow (central server) |
| **Data Versioning** | DVC (Git-based) |
| **APIs** | FastAPI with automatic OpenAPI docs |
| **Dashboard** | Streamlit (CarVision) |
| **Containerization** | Docker (multi-stage builds) |
| **Orchestration** | Docker Compose, Kubernetes |
| **CI/CD** | GitHub Actions (6-stage pipeline) |
| **IaC** | Terraform (AWS EKS, RDS, S3, ECR) |

### Security & Quality

| Component | Technology |
|-----------|-----------|
| **Code Quality** | Black, Flake8, Mypy, isort |
| **Security Scanning** | Bandit, Gitleaks, pip-audit, Trivy |
| **Testing** | pytest, pytest-cov (79-97% coverage) |
| **Pre-commit** | Automated hooks for quality gates |

---

## 📈 Portfolio Metrics

### Code Quality

| Metric | BankChurn | CarVision | TelecomAI | Target |
|--------|-----------|-----------|-----------|--------|
| **Test Coverage** | 79% | 97% | 97% | >70% ✅ |
| **Linting** | Clean | Clean | Clean | 100% ✅ |
| **Type Checking** | Strict | Strict | Strict | 100% ✅ |
| **Security Scan** | 0 HIGH | 0 HIGH | 0 HIGH | 0 ✅ |

### Performance Benchmarks

| Metric | BankChurn | CarVision | TelecomAI | Target |
|--------|-----------|-----------|-----------|--------|
| **P95 Latency** | <50ms | <100ms | <25ms | <200ms ✅ |
| **Throughput** | 500 RPS | 300 RPS | 1,200 RPS | >100 ✅ |
| **Memory Usage** | 1.2 GB | 1.8 GB | 1.0 GB | <2GB ✅ |
| **Model Size** | 4 MB | 6 KB | 156 KB | — |

---

## 🏗️ Repository Structure

```
ML-MLOps-Portfolio/
├── .github/workflows/
│   └── ci-mlops.yml               # ⚡ Unified CI Pipeline (6 jobs)
│
├── BankChurn-Predictor/           # 🏦 Customer Churn Prediction
│   ├── src/bankchurn/             # Core package
│   ├── app/fastapi_app.py         # REST API
│   ├── tests/                     # 79% coverage
│   ├── models/model_card.md       # Model documentation v2.0
│   └── data_card.md               # Dataset documentation v2.0
│
├── CarVision-Market-Intelligence/ # 🚗 Vehicle Price Prediction
│   ├── src/carvision/             # Core package (FeatureEngineer)
│   ├── app/
│   │   ├── fastapi_app.py         # REST API
│   │   └── streamlit_app.py       # Dashboard (4 tabs)
│   ├── tests/                     # 97% coverage
│   ├── models/model_card.md       # Model documentation v2.0
│   └── data_card.md               # Dataset documentation v2.0
│
├── TelecomAI-Customer-Intelligence/ # 📱 Plan Recommendation
│   ├── src/telecomai/             # Core package
│   ├── app/fastapi_app.py         # REST API
│   ├── tests/                     # 97% coverage
│   ├── models/model_card.md       # Model documentation v2.0
│   └── data_card.md               # Dataset documentation v2.0
│
├── infra/
│   ├── docker/                    # Dockerfiles (multi-stage)
│   ├── terraform/aws/             # AWS infrastructure (EKS, RDS, S3)
│   └── k8s/                       # Kubernetes manifests (HPA, services)
│
├── docs/                          # 📚 GitHub Pages documentation site
│   ├── getting-started/           # Quick start, installation, development
│   ├── projects/                  # Per-project deep dives
│   ├── architecture/              # System design, data flow, CI/CD
│   ├── api/                       # REST API & CLI reference
│   ├── operations/                # Deployment, monitoring, troubleshooting
│   └── models/                    # Model catalog & reproducibility
│
├── scripts/                       # Automation scripts
│   ├── setup_demo_models.sh       # Generate demo artifacts
│   └── run_experiments.py         # MLflow experiments
│
├── docker-compose.demo.yml        # Full demo stack
├── QUICK_START.md                 # 5-minute setup guide v2.0
├── RUNBOOK.md                     # Operations reference v2.0
├── SECURITY.md                    # Security policy
└── README.md                      # Main documentation
```

---

## 📚 Documentation

### Quick Access

| Document | Description |
|----------|-------------|
| **[Quick Start](getting-started/quickstart.md)** | Get running in 5 minutes |
| **[Architecture Overview](architecture/overview.md)** | System design with Mermaid diagrams |
| **[Operations Guide](operations/deployment.md)** | Deployment (Docker, K8s, Terraform) |
| **[API Reference](api/rest-apis.md)** | Complete REST API documentation |
| **[Model Catalog](models/catalog.md)** | Trained models registry |
| **[Troubleshooting](operations/troubleshooting.md)** | Common issues and solutions |

### Project-Specific Docs

- **[BankChurn Predictor](projects/bankchurn.md)** — Churn prediction with SHAP
- **[CarVision Market Intelligence](projects/carvision.md)** — Price prediction + dashboard
- **[TelecomAI Customer Intelligence](projects/telecom.md)** — Plan optimization

---

## 🆘 Getting Help

### Resources

- **📖 Documentation**: You're here! Explore the navigation above
- **🐛 Issues**: [GitHub Issues](https://github.com/DuqueOM/ML-MLOps-Portfolio/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/DuqueOM/ML-MLOps-Portfolio/discussions)
- **📧 Contact**: DuqueOrtegaMutis@gmail.com

### Contributing

Interested in contributing? See our [Contributing Guidelines](contributing/guidelines.md)

---

## 🎯 Target Audience

This portfolio is designed for:

- **🏢 Recruiters**: Quick demo in 5 minutes, comprehensive documentation
- **👨‍💼 Hiring Managers**: Production-ready code, enterprise MLOps practices
- **👨‍🔬 Data Scientists**: Advanced ML techniques, experiment tracking
- **👨‍💻 ML Engineers**: Deployment patterns, monitoring, infrastructure
- **🎓 Students**: Learning best practices, complete end-to-end examples

---

!!! info "Documentation Status"
    This documentation is actively maintained.  
    **Last Updated**: March 2026  
    **Portfolio Version**: 1.5.0

!!! tip "Quick Evaluation"
    **For recruiters**: Start with the [5-minute Quick Start](getting-started/quickstart.md) and explore the [Streamlit Dashboard](http://localhost:8501) (after starting demo stack)
    
    **For technical deep dive**: Review [Architecture](architecture/overview.md) and [Model Cards](models/catalog.md)

---

**ML-MLOps Portfolio** — Production-Ready Machine Learning  
Built by [Duque Ortega Mutis (DuqueOM)](https://github.com/DuqueOM)

[📖 Full Documentation](https://duqueom.github.io/ML-MLOps-Portfolio/) | [💻 Source Code](https://github.com/DuqueOM/ML-MLOps-Portfolio) | [📺 Video Demo](https://youtu.be/qmw9VlgUcn8)
