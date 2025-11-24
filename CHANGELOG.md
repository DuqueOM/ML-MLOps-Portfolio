# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-11-23

### Added
- **Unified Documentation Suite**:
  - `docs/ARCHITECTURE_PORTFOLIO.md`: Global microservices architecture.
  - `docs/OPERATIONS_PORTFOLIO.md`: Centralized runbook for deployment and maintenance.
  - `docs/DEPENDENCY_CONFLICTS.md`: Matrix of dependencies and conflict resolutions.
- **Cross-Project Integration Testing**:
  - `scripts/run_demo_tests.sh`: Automated smoke tests for all containerized services.
  - CI/CD Job `integration-test`: Runs the full Docker Compose stack in GitHub Actions.

### Changed
- **CI/CD Pipeline**: Refactored `ci-mlops.yml` to include E2E integration tests and summary reporting.
- **Root Documentation**: Simplified root directory by moving specialized docs to `docs/` and creating a unified `README.md`.
- **Docker Workflow**: Optimized `docker-compose.demo.yml` for robust health checks and networking.

### Removed
- Deprecated single-file runbooks (`ARCHITECTURE.md`, `OPERATIONS.md`) from root in favor of the `docs/` suite.
- Redundant status files.

## [1.0.0] - 2024-11-16

### Added
- **BankChurn-Predictor** - Customer churn prediction with ensemble models
  - FastAPI application with health checks
  - Drift monitoring (KS/PSI + Evidently)
  - Fairness tests for demographic bias
  - DVC pipeline for reproducibility
  - Model card and data card documentation

- **CarVision-Market-Intelligence** - Vehicle price prediction
  - Streamlit interactive dashboard
  - FastAPI REST API
  - Temporal validation for time-series data
  - MLflow integration

- **GoldRecovery-Process-Optimizer** - Metallurgical process optimization
  - Multi-stage process modeling
  - Ensemble regression (XGBoost, LightGBM, RandomForest)
  - Monte Carlo simulations
  - Custom sMAPE metric

- **Chicago-Mobility-Analytics** - Taxi ride duration prediction
  - Geospatial feature engineering
  - Weather API integration
  - GeoParquet support
  - PostGIS compatibility

- **Gaming-Market-Intelligence** - Video game success prediction
  - Multi-platform analysis
  - Survival analysis (Kaplan-Meier) for retention
  - LTV modeling
  - Interactive notebooks

- **OilWell-Location-Optimizer** - Oil well selection optimization
  - Bootstrap confidence intervals
  - Risk-adjusted profit maximization
  - Multi-region comparison
  - Scenario sensitivity analysis

- **TelecomAI-Customer-Intelligence** - Telecom churn prediction
  - Full MLflow integration
  - Automated retraining workflow
  - Evidently monitoring dashboards
  - Kubernetes deployment manifests

### Infrastructure
- CI/CD with GitHub Actions
  - Matrix testing for all 7 projects
  - Automated linting (black, flake8, mypy)
  - Test coverage tracking (70-75% threshold)
  - Pre-commit hooks

- Containerization
  - Dockerfiles for all projects
  - docker-compose for local development
  - MLflow infrastructure stack (PostgreSQL + MinIO)
  - Health checks and multi-stage builds

- Common Utilities
  - Centralized seed management (`common_utils/seed.py`)
  - Shared configuration patterns
  - Consistent CLI interfaces

### Documentation
- Comprehensive READMEs for each project
- Model cards and data cards
- Executive summaries
- API examples and usage guides
- Architecture documentation

## [0.9.0] - 2024-10-01

### Added
- Initial project structure
- Basic implementations of all 7 projects
- Individual project READMEs
- Makefiles for automation

### Infrastructure
- Basic CI/CD setup
- Docker support
- MLflow tracking (local)

## Format Guidelines

### Types of changes
- `Added` for new features
- `Changed` for changes in existing functionality
- `Deprecated` for soon-to-be removed features
- `Removed` for now removed features
- `Fixed` for any bug fixes
- `Security` for vulnerability fixes

---

[Unreleased]: https://github.com/DuqueOM/Portafolio-ML-MLOps/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/DuqueOM/Portafolio-ML-MLOps/releases/tag/v1.0.0
[0.9.0]: https://github.com/DuqueOM/Portafolio-ML-MLOps/releases/tag/v0.9.0
