# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

---

## [5.1.0] - 2025-12-03

### Added
- **Portfolio Demo Video**: Full end-to-end walkthrough published on YouTube
  - Link: https://youtu.be/qmw9VlgUcn8
  - Integrated across all READMEs and documentation

- **Visual Assets (Complete)**:
  - 6 GIFs for project demos (time-lapse style, 800x600)
  - 8 screenshots for documentation (MLflow, Swagger, Streamlit)
  - All assets properly referenced in documentation

- **MLflow Experiment Script** (`scripts/run_experiments.py`):
  - Automated 9 experiments across 3 projects
  - BankChurn: Baseline, Tuned RF, Overfit demo
  - CarVision: Ridge, RF, GradientBoosting
  - TelecomAI: LogReg, GB, RandomForest

### Changed
- **Documentation Overhaul** (10 files updated):
  - All documentation translated to English (senior/staff level)
  - Updated metrics from MLflow experiments
  - Added YouTube badge to all key docs
  - Enabled GIF displays in project READMEs
  - Updated `docs/portfolio_landing.md` with current state
  - Added visual references to `docs/ARCHITECTURE_PORTFOLIO.md`

- **Media Management**:
  - Video files (MP4) added to `.gitignore` (hosted on YouTube)
  - GIFs and screenshots kept in repo (small, essential for docs)

### Metrics (from MLflow)
| Project | Best Model | F1/R² | AUC/RMSE |
|---------|------------|-------|----------|
| BankChurn | RandomForest (tuned) | 0.64 | 0.87 |
| CarVision | RandomForest (tuned) | 0.77 | $4,396 |
| TelecomAI | RandomForest | 0.63 | 0.82 (Acc) |

---

## [5.0.0] - 2025-12-01

### Changed (2025-12-01)
- **CI/CD Optimization**:
  - Consolidated `ci-portfolio-top3.yml` into `ci-mlops.yml` (single source of truth)
  - Added GHCR publish job to main CI workflow
  - Updated coverage thresholds: BankChurn 79%, CarVision 80%, TelecomAI 80%
  - Fixed Python version consistency (3.12 across all workflows)
  - Coverage now focuses on `src/` directories only

- **Data Location Standardization**:
  - Unified raw data to `data/raw/` across all projects
  - BankChurn: already compliant (`data/raw/Churn.csv`)
  - CarVision: moved from root to `data/raw/vehicles_us.csv`
  - TelecomAI: moved from root to `data/raw/users_behavior.csv`
  - Updated all configs, code, notebooks, tests, and docs

- **Portfolio Root Cleanup**:
  - Removed `fixes/` (historical patches, obsolete)
  - Removed `reports/` (temporary dev logs, added to .gitignore)
  - Removed `Portafolio/` (empty directory)
  - Removed `infra/docker-compose-mlflow.yml` (redundant with root)
  - Moved `Reportes Portafolio/` → `docs/historical-audits/`
  - Moved status reports to `docs/`
  - Removed `docs/guia_mlops/` from repo (personal use only)

- **Test Coverage Improvements**:
  - BankChurn: 79.5% coverage on src/ (87 tests)
  - CarVision: 97% coverage on src/carvision (17 tests)
  - TelecomAI: 97% coverage on src/telecom (14 tests)

### Fixed
- **Critical CI/CD Integration Test Failures** (2025-11-24):
  - Fixed BankChurn Dockerfile Python version mismatch between builder (3.13) and runtime (3.12) stages, causing `ModuleNotFoundError` for uvicorn and pip.
  - Corrected model artifact paths from `models/` to `artifacts/` for CarVision and TelecomAI to match API expectations.
  - Updated `docker-compose.demo.yml` volume mounts to use `artifacts/` instead of `models/` for CarVision and TelecomAI services.
  - Removed explicit `image:` names from docker-compose services to allow auto-generation, fixing CI build errors ("No such image" failures).
  - Fixed CarVision prediction test payload to use correct schema (`model_year`, `model`) instead of incorrect fields.
  - Fixed TelecomAI prediction test payload to match API schema (`calls`, `minutes`, `messages`, `mb_used`).
  - Improved CarVision model training to handle missing values correctly by data type (strings → 'unknown', numbers → 0).
  - Updated TelecomAI training script to use correct dataset schema from `users_behavior.csv` (`is_ultra` target instead of `Churn`).
  - Added required CSV datasets for demo model training (`Churn_Modelling.csv`, `vehicles_us.csv`, `WA_Fn-UseC_-Telco-Customer-Churn.csv`).
  - **Result**: All integration tests now pass successfully (BankChurn ✅, CarVision ✅, TelecomAI ✅).

### Added
- **Comprehensive Documentation Suite** (2500+ lines):
  - `docs/ARCHITECTURE_PORTFOLIO.md`: System architecture with Mermaid diagrams, Docker multi-stage strategy, CI/CD pipeline, and tech stack.
  - `docs/OPERATIONS_PORTFOLIO.md`: Complete operations runbook with Docker/K8s deployment, monitoring (Prometheus/Grafana), troubleshooting, and backup procedures.
  - `docs/RELEASE.md`: Full release workflow with semantic versioning, GHCR publishing, rollback procedures, and model versioning.
  - `docs/DEPENDENCY_CONFLICTS.md`: Dependency conflict analysis (PyArrow, Pydantic, Python versions) with 4-phase remediation plan.
  - `docs/PR_PLAN.md`: 10 prioritized Pull Requests with complete specifications, diffs, risk assessment, and 4-week timeline.
  - `docs/PORTFOLIO_DELIVERABLES.md`: Executive summary of all deliverables.

- **Docker Standardization**:
  - Multi-stage Dockerfiles for CarVision and TelecomAI (50% image size reduction).
  - Non-root user (`appuser`, UID 1000) across all projects.
  - Health checks on `/health` endpoint for all services.
  - Standardized to `python:3.11-slim` base image.

- **Shared Utilities** (`common_utils/`):
  - `logger.py`: Centralized logging configuration for consistency across projects.
  - `seed.py`: Already existed, now documented and promoted for cross-project use.

- **Cross-Project Integration Testing**:
  - `tests/integration/test_demo.py`: Python-based integration tests with pytest and requests.
  - Health checks for all services (BankChurn, CarVision, TelecomAI, MLflow).
  - Prediction endpoint validation with correct API schemas.

### Changed
- **CI/CD Pipeline** (`ci-mlops.yml`):
  - Added Python version matrix (3.11, 3.12) for comprehensive testing.
  - Integrated Python-based integration tests replacing shell scripts.
  - Enhanced coverage reporting per Python version.
  - Consistent dependency installation strategy.

- **Root README.md**:
  - Updated Python version badge to 3.11+.
  - Corrected workflow reference from `ci-portfolio-top3.yml` to `ci-mlops.yml`.
  - Added references to all new documentation.
  - Enhanced Quick Start section with monitoring services.
  - Updated metrics table with multi-stage Docker and Python matrix.

- **BankChurn-Predictor**:
  - Unified sklearn Pipeline implementation (preprocessor + model).
  - Pydantic-based config validation.
  - 77% test coverage achieved.

- **CarVision-Market-Intelligence**:
  - Centralized `FeatureEngineer` class for all feature engineering.
  - Removed legacy files (`data/preprocess.py`, `data/validate_data.py`, `evaluate.py`).
  - >95% test coverage.

### Fixed
- Python version mismatch in Dockerfiles (now consistent 3.11-slim).
- Outdated API schemas in integration tests.
- Docker image size optimization (builder stage cleanup).

### Security
- Implemented non-root Docker users across all projects.
- Health checks for container monitoring.
- Documented security scanning with Trivy and Bandit.

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
