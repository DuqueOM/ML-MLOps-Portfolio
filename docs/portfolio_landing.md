# ML/MLOps Portfolio — Production-Ready Projects

## 📺 Video Demo

[![YouTube Demo](https://img.shields.io/badge/YouTube-Watch%20Demo-red?style=for-the-badge&logo=youtube)](https://youtu.be/qmw9VlgUcn8)

---

## 1. Executive Summary

A portfolio featuring **3 production-ready ML projects** with complete MLOps infrastructure. Each project includes:

- **Reproducible pipelines** via `Makefile` or CLI (`main.py` with `--mode` and `--config`)
- **Inference APIs** (FastAPI) and dashboards (Streamlit) where applicable
- **Versioned artifacts**: models (`model.joblib`), metrics JSON, and documentation
- **Experiment tracking**: MLflow integration with 9 tracked runs across all projects
- **Containerization**: Dockerfiles with multi-stage builds and health checks
- **Unified CI/CD**: Single workflow validating all projects with matrix testing

---

## 2. Project Summary (TOP-3)

| Project | Domain | Key Value | Tech Stack | Quick Demo | Target Role |
|---------|--------|-----------|------------|------------|-------------|
| **BankChurn-Predictor** | Banking Churn | Ensemble classifier with class imbalance handling | Python, scikit-learn, FastAPI, MLflow, DVC | `docker compose -f docker-compose.demo.yml up -d` | Senior Data Scientist — Customer Intelligence |
| **CarVision-Market-Intelligence** | Used Car Pricing | Price prediction + Streamlit dashboard + API | Python, scikit-learn, FastAPI, Streamlit, MLflow | `docker compose -f docker-compose.demo.yml up -d` | Senior Data Scientist — Pricing & Analytics |
| **TelecomAI-Customer-Intelligence** | Telecom | Plan recommendation classifier with API | Python, scikit-learn, FastAPI, Docker, MLflow | `docker compose -f docker-compose.demo.yml up -d` | ML Engineer — Customer Analytics |

## 2.1 Technical Comparison

| Project | Problem | Model | Best Metrics | Production Level |
|---------|---------|-------|--------------|------------------|
| **BankChurn-Predictor** | Churn prediction (`Exited`) | RandomForest (tuned) | F1=0.64, AUC=0.87 | CLI + API + Docker + CI + Model Card |
| **CarVision-Market-Intelligence** | Price prediction (`price`) | RandomForest in sklearn Pipeline | RMSE=$4,396, R²=0.77 | CLI + Dashboard + API + Docker + CI |
| **TelecomAI-Customer-Intelligence** | Plan recommendation (`is_ultra`) | GradientBoosting/RandomForest | Acc=0.82, F1=0.63 | CLI + API + Docker + CI + Model Card |

---

## 3. MLflow Experiments

All projects are integrated with a central MLflow server. Each project has **3 tracked runs** demonstrating:

- **Baseline models**: Simple algorithms for comparison
- **Tuned models**: Optimized hyperparameters
- **Alternative approaches**: Different algorithms or configurations

| Experiment | Runs | Best Model | Key Insight |
|------------|------|------------|-------------|
| BankChurn-Predictor | 3 | BC-2_RandomForest_Tuned | Balanced class weights improve F1 |
| CarVision-Market-Intelligence | 3 | CV-2_RandomForest_Tuned | Tree models outperform linear |
| TelecomAI-Customer-Intelligence | 3 | TL-3_RandomForest | Ensemble methods excel |

**Run all experiments:**
```bash
docker compose -f docker-compose.demo.yml up -d
python scripts/run_experiments.py
# View at http://localhost:5000
```

---

## 4. Technology Stack

| Category | Technologies |
|----------|--------------|
| **Language** | Python 3.11+ |
| **ML/Statistics** | scikit-learn, XGBoost, RandomForest, GradientBoosting |
| **MLOps/Tracking** | MLflow (central server), DVC (data versioning) |
| **APIs/Frontends** | FastAPI, Streamlit |
| **Infrastructure** | Docker, Docker Compose, GitHub Actions |
| **Security** | Trivy, Bandit, Gitleaks |
| **Testing** | pytest, pytest-cov (79-97% coverage) |

---

## 5. CI/CD Pipeline

Unified workflow (`.github/workflows/ci-mlops.yml`) with:

- **Matrix testing**: 3 projects × 2 Python versions (3.11, 3.12)
- **Quality gates**: flake8, black, mypy, bandit
- **Test coverage**: pytest with coverage thresholds
- **Docker builds**: Multi-stage with caching
- **Security scans**: Trivy container scanning
- **Integration tests**: Full stack validation on `main` branch

---

## 6. Visual Assets

All demo materials are available in `media/`:

| Asset Type | Files | Status |
|------------|-------|--------|
| **GIFs** | 6 animated demos | ✅ Complete |
| **Screenshots** | 8 UI captures | ✅ Complete |
| **Videos** | MP4 source files | ✅ Complete |
| **YouTube** | Full walkthrough | ✅ [Published](https://youtu.be/qmw9VlgUcn8) |

---

## 7. Navigation

- **[README.md](../README.md)**: Quick overview and demo commands
- **[QUICK_START.md](../QUICK_START.md)**: One-command demo guide
- **[ARCHITECTURE_PORTFOLIO.md](ARCHITECTURE_PORTFOLIO.md)**: System design diagrams
- **[OPERATIONS_PORTFOLIO.md](OPERATIONS_PORTFOLIO.md)**: Deployment and monitoring
- **Project READMEs**: Detailed documentation per project
