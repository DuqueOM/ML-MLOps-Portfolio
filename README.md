# 🚀 ML/MLOps Portfolio — Production-Ready + AI-Native

**Professional Machine Learning & MLOps Portfolio featuring 3 Production-Ready Projects**

> 💡 **Unique Feature:** AI-assisted development ready — includes AGENTS.md configuration for Claude, Cursor, Windsurf, and other AI coding tools. This portfolio isn't just viewable by recruiters; it's **ready for AI-human collaboration** from day one.

### 📚 View Full Documentation & Site

[![Portfolio](https://img.shields.io/badge/%F0%9F%9A%80_Portfolio-Live_Demo-blue?style=for-the-badge)](https://duqueom.github.io/ML-MLOps-Portfolio/)
[![AI-Ready](https://img.shields.io/badge/🤖_AI--Assisted-AGENTS.md-success?style=for-the-badge)](./AGENTS.md)

---

[![CI Pipeline](https://github.com/DuqueOM/ML-MLOps-Portfolio/actions/workflows/ci-mlops.yml/badge.svg)](https://github.com/DuqueOM/ML-MLOps-Portfolio/actions/workflows/ci-mlops.yml)
[![codecov](https://codecov.io/gh/DuqueOM/ML-MLOps-Portfolio/branch/main/graph/badge.svg)](https://codecov.io/gh/DuqueOM/ML-MLOps-Portfolio)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](./BankChurn-Predictor/pyproject.toml)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](./docker-compose.demo.yml)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

[![MLflow](https://img.shields.io/badge/MLflow-Tracking-0194E2.svg?logo=mlflow&logoColor=white)](./BankChurn-Predictor/configs/config.yaml)
[![DVC](https://img.shields.io/badge/DVC-Data%20Versioning-945DD6.svg)](./BankChurn-Predictor/dvc.yaml)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688.svg?logo=fastapi&logoColor=white)](./BankChurn-Predictor/app/fastapi_app.py)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B.svg?logo=streamlit&logoColor=white)](./CarVision-Market-Intelligence/app/streamlit_app.py)

---

[![Portfolio Demo](./docs/media/gifs/portfolio-demo.gif)](./docs/media/gifs/portfolio-demo.gif)

### 📺 Watch the Full Demo

[![YouTube Demo](https://img.shields.io/badge/YouTube-Watch%20Demo-red?style=for-the-badge&logo=youtube)](https://youtu.be/qmw9VlgUcn8)

*End-to-end walkthrough: Architecture, MLflow experiments, API demos, and Streamlit dashboards*

---

## 📑 Table of Contents

* [💡 Why This Portfolio Exists](#-why-this-portfolio-exists)
* [👨‍💻 About This Portfolio](#-about-this-portfolio)
* [🤖 AI-Native Development](#-ai-native-development-new)
* [🌟 TOP-3 Projects](#-top-3-production-ready-projects)
* [🛠️ Tech Stack & MLOps](#%EF%B8%8F-tech-stack--mlops)
* [📚 Documentation](#-documentation)
* [🚀 Quick Start](#-quick-start)
* [👤 Author](#-author)

---

## 💡 Why This Portfolio Exists

After 14 years managing high-pressure operations in hospitality and logistics, I discovered that the principles that make great operational systems—reliability, monitoring, reproducibility—are the same ones that make great ML systems.

This portfolio demonstrates that transition: not just ML models that achieve good metrics, but **production-ready systems** built with the discipline of someone who understands that downtime costs real money and poor monitoring creates real problems.

Every project here answers the question: "Would I trust this in production at 2am?"

---

## 🤖 AI-Native Development [NEW]

### **What Makes This Portfolio Different**

This isn't just code—it's **AI-collaboration ready**. The repository includes comprehensive AI assistant configuration:

```
.windsurf/
├── rules/                    # AI coding assistant instructions
│   ├── architecture.md       # System design decisions
│   ├── coding-standards.md   # Code generation rules
│   └── mlops-patterns.md     # Best practices
└── AGENTS.md                 # Universal AI assistant config
```

**Compatible with:**
- 🌊 Windsurf IDE
- 🎯 Cursor
- 🤖 Claude Code
- 💻 GitHub Copilot
- 🔮 And more...

**Why this matters for recruiters:**
> *Shows forward thinking: Not just "can code," but "designs systems for human-AI collaboration." This is Staff+ engineering mindset—thinking about knowledge scalability, not just code scalability.*

**Try it yourself:**
1. Clone this repo
2. Open in Windsurf/Cursor/Claude Code
3. Ask AI: "Explain the BankChurn architecture"
4. Watch it give you context-aware, accurate responses

[📖 Read full AI setup guide →](./AGENTS.md)

---

## 👨‍💻 About This Portfolio

This repository focuses on **3 Main Projects (Top-3)** brought to professional software engineering standards, demonstrating Senior/Enterprise capabilities in:

* ✅ **Advanced Machine Learning**: Ensembles, Regression, Classification with imbalance handling
* ✅ **MLOps & CI/CD**: Unified automated pipelines (`ci-mlops.yml`), rigorous testing, and security scanning
* ✅ **Software Engineering**: Modular architecture, Pydantic validation, FastAPI-based APIs
* ✅ **Deployment**: Complete Dockerization and interactive dashboards (Streamlit)
* ✅ **AI-Native**: AGENTS.md configuration for AI-assisted development

---

## 🌟 TOP-3: Production-Ready Projects

### 🏦 1. [BankChurn Predictor](./BankChurn-Predictor) — Customer Churn Prediction

🎬 Click to expand demo

[![BankChurn Demo](./docs/media/gifs/bankchurn-preview.gif)](./docs/media/gifs/bankchurn-preview.gif)

**Production-grade customer churn prediction system for banking**

| Metric | Value | Notes |
| --- | --- | --- |
| **F1-Score** | **0.64** | Tuned RandomForest |
| **AUC-ROC** | **0.87** | 3 experiments tracked |
| **Coverage** | 79% | Unit + Integration |
| **Latency** | <50ms | FastAPI async |

* **Architecture**: Modular Python package (`src/bankchurn`) with Pydantic config validation
* **MLOps**: MLflow experiment tracking with baseline/tuned/overfit comparison runs
* **Tech Stack**: FastAPI, Scikit-learn (Ensemble), Docker, DVC
* **Model Card**: [View](./BankChurn-Predictor/models/model_card.md)

[📂 View Project →](./BankChurn-Predictor) | [📺 Video Demo](https://youtu.be/qmw9VlgUcn8)

---

### 🚗 2. [CarVision Market Intelligence](./CarVision-Market-Intelligence) — Vehicle Price Prediction

🎬 Click to expand demo (API + Streamlit)

**API Demo:**
[![CarVision API Demo](./docs/media/gifs/carvision-preview.gif)](./docs/media/gifs/carvision-preview.gif)

**Streamlit Dashboard:**
[![Streamlit Dashboard](./docs/media/gifs/streamlit-carvision.gif)](./docs/media/gifs/streamlit-carvision.gif)

**Vehicle valuation platform with BI Dashboard and REST API**

| Metric | Value | Notes |
| --- | --- | --- |
| **R²** | **0.77** | RandomForest tuned |
| **RMSE** | **$4,396** | 3 experiments tracked |
| **Coverage** | 97% | Comprehensive tests |

* **User Experience**: Streamlit dashboard with 4 sections: Overview, Market Analysis, Model Metrics, Price Predictor
* **Backend**: REST API (FastAPI) with centralized `FeatureEngineer` class for consistent inference
* **Modeling**: Optimized RandomForest with `[features → pre → model]` pipeline, bootstrap CI, temporal backtest
* **Model Card**: [View](./CarVision-Market-Intelligence/models/model_card.md)

[📂 View Project →](./CarVision-Market-Intelligence) | [📺 Video Demo](https://youtu.be/qmw9VlgUcn8)

---

### 📱 3. [TelecomAI Customer Intelligence](./TelecomAI-Customer-Intelligence) — Plan Recommendation

🎬 Click to expand demo

[![TelecomAI Demo](./docs/media/gifs/telecom-preview.gif)](./docs/media/gifs/telecom-preview.gif)

**Strategic customer intelligence for telecommunications**

| Metric | Value | Notes |
| --- | --- | --- |
| **AUC-ROC** | **0.84** | GradientBoosting |
| **F1-Score** | **0.63** | 3 experiments tracked |
| **Coverage** | 97% | Full test suite |

* **Modeling**: GradientBoosting and RandomForest classifiers with experiment comparison
* **Pipeline**: Standardized preprocessing with MLflow tracking
* **Automation**: End-to-end tests integrated in unified CI pipeline
* **Model Card**: [View](./TelecomAI-Customer-Intelligence/models/model_card.md)

[📂 View Project →](./TelecomAI-Customer-Intelligence) | [📺 Video Demo](https://youtu.be/qmw9VlgUcn8)

---

## 🛠️ Tech Stack & MLOps

### Unified CI/CD Infrastructure (Staff-Level)

The entire portfolio is validated by a single master workflow (`ci-mlops.yml`) that orchestrates:

```
┌───────────────────────────────────────────────────────────┐
│  CI/CD Pipeline: .github/workflows/ci-mlops.yml           │
├───────────────────────────────────────────────────────────┤
│  1. Build & Env    → Python 3.11/3.12 matrix, pip cache   │
│  2. Data Quality   → Validate data before tests           │
│  3. Code Quality   → flake8, black, mypy, bandit          │
│  4. Testing        → pytest with coverage reports         │
│  5. Docker Build   → Multi-stage, push to GHCR            │
│  6. Security       → Trivy container scanning             │
└───────────────────────────────────────────────────────────┘
```

### Key Technologies

| Category | Advanced | Proficient | Familiar |
| --- | --- | --- | --- |
| **MLOps** | Docker, GitHub Actions, MLflow | Kubernetes, Terraform | DVC |
| **Cloud** | AWS (EKS, S3, ECR) | Prometheus, Grafana | GCP basics |
| **ML** | Scikit-learn, XGBoost | Pandas, NumPy | TensorFlow, PyTorch |
| **AI Tools** | Windsurf, Claude Code | Cursor, Copilot | - |

---

## 📚 Documentation

| Document | Description |
| --- | --- |
| **[Architecture](./docs/ARCHITECTURE_PORTFOLIO.md)** | System design with Mermaid diagrams, Docker multi-stage, CI/CD pipeline |
| **[Operations Runbook](./docs/OPERATIONS_PORTFOLIO.md)** | Deployment guide (Docker/K8s), monitoring, troubleshooting |
| **[AI Assistant Guide](./AGENTS.md)** | Configuration for AI-assisted development (Windsurf, Cursor, etc.) |
| **[Runbook (Quick Reference)](./RUNBOOK.md)** | Copy-paste commands for common operations |
| **[Release Process](./docs/RELEASE.md)** | Release workflow, GHCR publishing, rollback procedures |

---

## 📈 Quality Metrics

| Metric | Status | Target | Achievement |
| --- | --- | --- | --- |
| **CI Pipeline** | 🟢 **Passing** | 100% Green | ✅ 100% |
| **Test Coverage** | 🟢 **79%–97%** | ≥79% BankChurn, ≥97% others | ✅ Met |
| **Security** | 🛡️ **Scanned** | 0 Critical CVEs | ✅ 0 Critical |
| **Docker Builds** | 🐳 **Multi-Stage** | <500MB images | ✅ Optimized |
| **Python Support** | ✅ **3.11 & 3.12** | Matrix Testing | ✅ Both versions |
| **AI-Ready** | 🤖 **AGENTS.md** | AI assistant compatible | ✅ Configured |

---

## 🚀 Quick Start

### ⚡ 5-Command Demo (Copy-Paste Ready)

```bash
# 1. Clone and enter
git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git && cd ML-MLOps-Portfolio

# 2. Generate demo models (first time only)
bash scripts/setup_demo_models.sh

# 3. Start full stack (APIs + MLflow + Dashboard)
docker-compose -f docker-compose.demo.yml up -d --build

# 4. Wait for services and verify
sleep 60 && bash scripts/run_demo_tests.sh

# 5. Open services
echo "
🏦 BankChurn API:    http://localhost:8001/docs
🚗 CarVision API:    http://localhost:8002/docs
🚗 CarVision UI:     http://localhost:8501
📱 TelecomAI API:    http://localhost:8003/docs
📊 MLflow:           http://localhost:5000
"
```

### 🤖 AI-Assisted Development Setup

```bash
# If using Windsurf IDE:
1. Open this repo in Windsurf
2. AI automatically detects .windsurf/rules/
3. Ask: "Explain the architecture"
4. Get context-aware responses

# If using Cursor/Claude Code:
1. Open this repo
2. AI reads AGENTS.md
3. Start coding with full project context
```

---

## 👤 Author

**Duque Ortega Mutis (DuqueOM)**  
*Machine Learning & MLOps Engineer*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat&logo=linkedin)](https://linkedin.com/in/duqueom)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?style=flat&logo=github)](https://github.com/DuqueOM)

---

## 📬 How to Reach Me

* **Issues**: [GitHub Issues](https://github.com/DuqueOM/ML-MLOps-Portfolio/issues)
* **Discussions**: [GitHub Discussions](https://github.com/DuqueOM/ML-MLOps-Portfolio/discussions)
* **Contributing**: See [Contributing Guidelines](./docs/contributing/guidelines.md)

---

**Status**: ✅ Production-Ready | **Last Updated**: March 2026

*Star ⭐ this repo if you find it useful!*