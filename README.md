# 🚀 ML/MLOps Portfolio — Production-Ready

**Professional Machine Learning & MLOps Portfolio featuring 3 Production-Ready Projects**

<!-- CI/CD Badges -->
[![CI Pipeline](https://github.com/DuqueOM/ML-MLOps-Portfolio/actions/workflows/ci-mlops.yml/badge.svg)](https://github.com/DuqueOM/ML-MLOps-Portfolio/actions/workflows/ci-mlops.yml)
[![Coverage](https://img.shields.io/badge/Coverage->75%25-brightgreen.svg)](reports/)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](docker-compose.demo.yml)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

<!-- Tech Stack Badges -->
[![MLflow](https://img.shields.io/badge/MLflow-Tracking-0194E2.svg?logo=mlflow&logoColor=white)](https://mlflow.org)
[![DVC](https://img.shields.io/badge/DVC-Data%20Versioning-945DD6.svg)](https://dvc.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io)

---

<!-- 
=============================================================================
🎬 DEMO VIDEO & GIF SECTION
=============================================================================
TODO: Replace the placeholder below with your actual GIF and video links.

To create the GIF:
1. Record a 6-8 second demo of a prediction
2. Convert to GIF using: ffmpeg -i video.mp4 -vf "fps=15,scale=800:-1" demo.gif
3. Place in media/gifs/portfolio-demo.gif

Video options:
- Upload to YouTube (unlisted) and link here
- Use GitHub Releases to host MP4 files
- Use Google Drive with public link
=============================================================================
-->

<div align="center">

<!-- 🎬 [PLACEHOLDER: INSERT DEMO GIF HERE] -->
<!-- ![Portfolio Demo](media/gifs/portfolio-demo.gif) -->

**[📺 WATCH FULL DEMO VIDEO — CLICK HERE](#)** 
<!-- TODO: Replace # with actual video link (YouTube/Drive) -->

*See all 3 projects in action: API predictions, dashboards, and CI/CD pipeline*

</div>

---

> **A professional portfolio demonstrating the complete Machine Learning lifecycle: from exploratory analysis and model training, to CI/CD pipelines, REST APIs, and containerized deployment.**

---

## 👨‍💻 About This Portfolio

This repository focuses on **3 Main Projects (Top-3)** brought to professional software engineering standards, demonstrating Senior/Enterprise capabilities in:

- ✅ **Advanced Machine Learning**: Ensembles, Regression, Classification with imbalance handling
- ✅ **MLOps & CI/CD**: Unified automated pipelines (`ci-mlops.yml`), rigorous testing, and security scanning
- ✅ **Software Engineering**: Modular architecture, Pydantic validation, FastAPI-based APIs
- ✅ **Deployment**: Complete Dockerization and interactive dashboards (Streamlit)

---

## 🌟 TOP-3: Production-Ready Projects

### 🏦 1. [BankChurn Predictor](BankChurn-Predictor/) — Customer Churn Prediction

<!-- 
🎬 [PLACEHOLDER: BANKCHURN GIF]
![BankChurn Demo](media/gifs/bankchurn-preview.gif)
-->

**Robust customer churn prediction system for banking**

| Metric | Value |
|--------|-------|
| **AUC-ROC** | **[INSERT]** |
| **Coverage** | 77% |
| **Latency** | <50ms |

- **Architecture**: Modular design (`src/bankchurn`) installable as package
- **MLOps**: MLflow experiment tracking, Pydantic config validation, green CI/CD pipeline
- **Tech Stack**: FastAPI, Scikit-learn, Docker, DVC
- **Model Card**: [View](BankChurn-Predictor/models/model_card.md)

[📂 View Project →](BankChurn-Predictor/) | [📺 Video Demo](#) <!-- TODO: Add video link -->

---

### 🚗 2. [CarVision Market Intelligence](CarVision-Market-Intelligence/) — Vehicle Price Prediction

<!-- 
🎬 [PLACEHOLDER: CARVISION GIF]
![CarVision Demo](media/gifs/carvision-preview.gif)
-->

**Vehicle valuation platform with BI Dashboard and API**

| Metric | Value |
|--------|-------|
| **R²** | **[INSERT]** |
| **Coverage** | 96% |
| **MAPE** | **[INSERT]** |

- **User Experience**: Streamlit dashboard with 4 key sections: Overview, Market Analysis, Model Metrics, Price Predictor
- **Backend**: REST API (FastAPI) serving regression model with external integration support
- **Modeling**: Optimized Random Forest with `[features → pre → model]` pipeline and advanced metrics (bootstrap, temporal backtest)
- **Model Card**: [View](CarVision-Market-Intelligence/models/model_card.md)

[📂 View Project →](CarVision-Market-Intelligence/) | [📺 Video Demo](#) <!-- TODO: Add video link -->

---

### 📱 3. [TelecomAI Customer Intelligence](TelecomAI-Customer-Intelligence/) — Plan Recommendation

<!-- 
🎬 [PLACEHOLDER: TELECOMAI GIF]
![TelecomAI Demo](media/gifs/telecom-preview.gif)
-->

**Strategic customer intelligence for telecommunications**

| Metric | Value |
|--------|-------|
| **AUC-ROC** | **[INSERT]** |
| **Coverage** | 96% |
| **Accuracy** | **[INSERT]** |

- **Complex Modeling**: **Voting Classifier** combining multiple strategies
- **Pipeline**: Advanced preprocessing and domain-specific feature engineering
- **Automation**: End-to-end tests integrated in CI pipeline
- **Model Card**: [View](TelecomAI-Customer-Intelligence/models/model_card.md)

[📂 View Project →](TelecomAI-Customer-Intelligence/) | [📺 Video Demo](#) <!-- TODO: Add video link -->

---

## 🛠️ Tech Stack & MLOps

### Unified CI/CD Infrastructure (Staff-Level)

The entire portfolio is validated by a single master workflow (`ci-mlops.yml`) that orchestrates:

```
┌─────────────────────────────────────────────────────────────────┐
│  CI/CD Pipeline: .github/workflows/ci-mlops.yml                 │
├─────────────────────────────────────────────────────────────────┤
│  1. Build & Env    → Python 3.11/3.12 matrix, pip cache        │
│  2. Data Quality   → Validate data before tests                 │
│  3. Code Quality   → flake8, black, mypy, bandit               │
│  4. Testing        → pytest with coverage reports               │
│  5. Docker Build   → Multi-stage, push to GHCR                 │
│  6. Security       → Trivy container scanning                   │
└─────────────────────────────────────────────────────────────────┘
```

### CI Notes

| Component | Details |
|-----------|---------|
| **Workflow file** | `.github/workflows/ci-mlops.yml` |
| **Jobs** | `tests` → `coverage` → `docker-build` → `e2e` |
| **Python versions** | 3.11, 3.12 (matrix testing) |
| **Coverage threshold** | ≥70% per project |
| **Docker registry** | GitHub Container Registry (GHCR) |

**If a run fails:**
1. Check the `tests` job logs first
2. Expand `coverage-report` artifact for detailed coverage
3. For Docker failures, check base image availability

### Infrastructure as Code (IaC)

- **Terraform**: AWS and GCP modules in `infra/terraform/`
  - Full stack: EKS, S3, RDS, ECR (see `main.tf`)
  - **S3 Artifact Store**: Versioning, encryption, lifecycle policies
- **Kubernetes**: Production-ready manifests in `k8s/`

### Key Technologies

| Category | Technologies |
|----------|--------------|
| **Core** | Python 3.11+, Pandas, NumPy, Scikit-learn, XGBoost |
| **Web** | FastAPI, Streamlit, Uvicorn |
| **Ops** | Docker (Multi-Stage), GitHub Actions, Kubernetes, Make |
| **Tracking** | MLflow, DVC |
| **Monitoring** | Prometheus, Grafana |
| **Security** | Trivy, Bandit, Gitleaks |
| **Registry** | GitHub Container Registry (GHCR) |

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[Architecture](docs/ARCHITECTURE_PORTFOLIO.md)** | System design with Mermaid diagrams, Docker multi-stage, CI/CD pipeline |
| **[Operations Runbook](docs/OPERATIONS_PORTFOLIO.md)** | Deployment guide (Docker/K8s), monitoring, troubleshooting |
| **[Runbook (Quick Reference)](RUNBOOK.md)** | Copy-paste commands for common operations |
| **[Release Process](docs/RELEASE.md)** | Release workflow, GHCR publishing, rollback procedures |
| **[Dependencies](docs/DEPENDENCY_CONFLICTS.md)** | Conflict analysis (PyArrow, Pydantic), remediation plan |
| **[Release Checklist](CHECKLIST_RELEASE.md)** | Pre-launch verification checklist |
| **[Quick Start](QUICK_START.md)** | One-command demo for quick evaluation |

---

## 📁 Portfolio Structure

```
ML-MLOps-Portfolio/
├── .github/workflows/
│   └── ci-mlops.yml               # ⚡ Unified CI Pipeline (Build, Test, Scan)
│
├── BankChurn-Predictor/           # 🏦 Tier-1 Project
│   ├── src/bankchurn/             # Modular Python package
│   ├── models/model_card.md       # Model documentation
│   ├── tests/                     # Unit & integration tests
│   └── Dockerfile
│
├── CarVision-Market-Intelligence/ # 🚗 Interactive App
│   ├── app/                       # Streamlit + FastAPI
│   ├── models/model_card.md       # Model documentation
│   ├── tests/
│   └── Dockerfile
│
├── TelecomAI-Customer-Intelligence/# 📱 Advanced Analytics
│   ├── models/model_card.md       # Model documentation
│   ├── tests/
│   └── Dockerfile
│
├── common_utils/                  # Shared utilities (seed, logger)
├── tests/integration/             # Cross-project integration tests
├── infra/                         # Docker Compose, Terraform, Prometheus/Grafana
├── k8s/                           # Kubernetes manifests (deployments, HPA, ingress)
├── media/                         # Videos, GIFs, screenshots
├── docs/                          # Global documentation
├── RUNBOOK.md                     # Quick command reference
├── CHECKLIST_RELEASE.md           # Pre-launch checklist
├── CONTRIBUTING.md                # Contribution guidelines
├── CHANGELOG.md                   # Version history
└── README.md                      # This file
```

---

## 📈 Quality Metrics

| Metric | Status | Target |
|--------|--------|--------|
| **CI Pipeline** | 🟢 **Passing** | 100% Green |
| **Test Coverage** | 🟢 **> 75% (Avg)** | > 70% |
| **Security** | 🛡️ **Scanned** | 0 Critical CVEs |
| **Docker Builds** | 🐳 **Multi-Stage** | 50% Size Reduction |
| **Python Support** | ✅ **3.11 & 3.12** | Matrix Testing |

---

## 🚀 Quick Start

### One-Liner Demo (Recommended)
```bash
# 1. Generate demo models first (required for first run)
bash scripts/setup_demo_models.sh

# 2. Start full demo stack with all 3 services + MLflow
make docker-demo
# or: docker-compose -f docker-compose.demo.yml up -d --build

# 3. Run integration tests to verify everything works
bash scripts/run_demo_tests.sh
```

**Demo includes:**
- 🏦 BankChurn API: `http://localhost:8001/docs`
- 🚗 CarVision API: `http://localhost:8002/docs`
- 🚗 CarVision Dashboard: `http://localhost:8501`
- 📱 TelecomAI API: `http://localhost:8003/docs`
- 📊 MLflow UI: `http://localhost:5000`
- 📈 Prometheus: `http://localhost:9090` (with --profile monitoring)
- 📊 Grafana: `http://localhost:3000` (with --profile monitoring)

### Manual Setup (BankChurn)
```bash
# 1. Clone repository
git clone https://github.com/DuqueOM/Portafolio-ML-MLOps.git
cd Portafolio-ML-MLOps

# 2. Using Docker Compose (easiest)
docker-compose -f docker-compose.demo.yml up -d

# 3. Or build individual service
cd BankChurn-Predictor
docker build -t bankchurn:latest .
docker run -p 8000:8000 bankchurn:latest

# 4. Test API
curl -X POST "http://localhost:8001/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "CreditScore": 650,
       "Geography": "France",
       "Gender": "Female",
       "Age": 40,
       "Tenure": 3,
       "Balance": 60000,
       "NumOfProducts": 2,
       "HasCrCard": 1,
       "IsActiveMember": 1,
       "EstimatedSalary": 50000
     }'
```

### Development Setup
```bash
# Install dependencies for all projects
make install

# Run tests
make test

# Run integration tests
pytest tests/integration/test_demo.py -v

# Check service health
make health-check

# Security scans
bandit -r . -f json -o bandit-report.json
docker run --rm aquasec/trivy image <image-name>
```

---

## 👤 Author

**Duque Ortega Mutis (DuqueOM)**  
*Machine Learning & MLOps Engineer*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat&logo=linkedin)](https://linkedin.com/in/duqueom) 
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?style=flat&logo=github)](https://github.com/DuqueOM)

---

## 📬 How to Reach Me

- **Portfolio Review**: Open an issue with tag `[portfolio-review]`
- **Collaboration**: Reach out via LinkedIn
- **Bug Reports**: Use GitHub Issues

---

<div align="center">

**Status**: ✅ Production-Ready | **Last Updated**: November 2025

*Star ⭐ this repo if you find it useful!*

</div>
