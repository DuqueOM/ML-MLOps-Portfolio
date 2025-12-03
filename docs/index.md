# ML-MLOps Portfolio Documentation

Welcome to the **ML-MLOps Portfolio** documentation. This portfolio demonstrates production-ready machine learning projects with enterprise-grade MLOps practices.

## 📺 Video Demo

[![YouTube Demo](https://img.shields.io/badge/YouTube-Watch%20Demo-red?style=for-the-badge&logo=youtube)](https://youtu.be/qmw9VlgUcn8)

Watch the complete end-to-end demo: [https://youtu.be/qmw9VlgUcn8](https://youtu.be/qmw9VlgUcn8)

---

## Quick Navigation

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Getting Started**

    ---

    Get up and running in minutes with our quick start guide.

    [:octicons-arrow-right-24: Quick Start](getting-started/quickstart.md)

-   :material-view-dashboard:{ .lg .middle } **Projects**

    ---

    Explore our three production-ready ML projects.

    [:octicons-arrow-right-24: View Projects](projects/overview.md)

-   :material-cog:{ .lg .middle } **Architecture**

    ---

    Understand the system design and data flow.

    [:octicons-arrow-right-24: Architecture](architecture/overview.md)

-   :material-api:{ .lg .middle } **API Reference**

    ---

    Complete API and CLI documentation.

    [:octicons-arrow-right-24: API Docs](api/rest-apis.md)

</div>

## Portfolio Overview

This portfolio features **3 Production-Ready Projects**:

| Project | Type | Best Metrics | Coverage | Key Features |
|---------|------|--------------|----------|--------------|
| [BankChurn Predictor](projects/bankchurn.md) | Classification | F1=0.64, AUC=0.87 | 79% | MLflow (3 runs), FastAPI, Ensemble |
| [CarVision Market Intelligence](projects/carvision.md) | Regression | RMSE=$4,396, R²=0.77 | 97% | Streamlit Dashboard, MLflow (3 runs) |
| [TelecomAI Customer Intelligence](projects/telecom.md) | Classification | Acc=0.82, F1=0.63 | 97% | GradientBoosting, MLflow (3 runs) |

## Key Capabilities Demonstrated

### Machine Learning
- Advanced ensemble methods (VotingClassifier, RandomForest, XGBoost)
- Imbalanced data handling (SMOTE, class weights)
- Feature engineering pipelines
- Model evaluation with multiple metrics

### MLOps & DevOps
- **CI/CD**: Unified GitHub Actions pipeline with matrix testing
- **Experiment Tracking**: MLflow integration for parameters, metrics, and artifacts
- **Data Versioning**: DVC for dataset management
- **Containerization**: Multi-stage Docker builds
- **Security**: Gitleaks, Bandit, Trivy scanning

### Software Engineering
- Modular Python packages with `src/` layout
- Pydantic configuration validation
- Comprehensive test suites (unit, integration, e2e)
- Pre-commit hooks for code quality

## Demo Access

```bash
# Start full demo stack (all 3 services + MLflow)
docker-compose -f docker-compose.demo.yml up -d --build

# Access points:
# - BankChurn API:    http://localhost:8001/docs
# - CarVision API:    http://localhost:8002/docs
# - CarVision Dashboard: http://localhost:8501
# - TelecomAI API:    http://localhost:8003/docs
# - MLflow UI:        http://localhost:5000
```

## Repository Structure

```
ML-MLOps-Portfolio/
├── BankChurn-Predictor/          # Customer churn prediction
├── CarVision-Market-Intelligence/ # Vehicle price prediction
├── TelecomAI-Customer-Intelligence/ # Plan recommendation
├── .github/workflows/            # CI/CD pipelines
├── infra/                        # Docker, Terraform, K8s
├── docs/                         # This documentation
└── scripts/                      # Automation scripts
```

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/DuqueOM/ML-MLOps-Portfolio/issues)
- **Discussions**: Open a discussion for questions
- **Contributing**: See [Contributing Guidelines](contributing/guidelines.md)

---

!!! info "Documentation Status"
    This documentation is actively maintained. Last updated: December 2025.
