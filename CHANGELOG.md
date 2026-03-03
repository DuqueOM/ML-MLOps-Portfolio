# Changelog

All notable changes to the ML-MLOps Portfolio are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/).

---

## [3.2.1] — 2026-03-03

### Added
- **CarVision fairness module** (`src/carvision/fairness.py`) — error ratio, MAE/RMSE parity by group (15 tests)
- **NLPInsight fairness module** (`src/nlpinsight/fairness.py`) — per-class F1 parity, group fairness (16 tests)
- Trivy DB repository override (`ghcr.io/aquasecurity/trivy-db:2`) to fix mirror.gcr.io 404

### Changed
- **All 3 projects now have fairness audits** (was only BankChurn)
- Trivy action pinned to `0.28.0` (was `@master`)
- Documentation standardized: 30+ files updated to v3.0.0 models / v3.2.0 portfolio
- Test total: 323 (198 + 52 + 73), coverage 90–98%

### Fixed
- E2E script: `app/main.py` → `app/fastapi_app.py`
- Version inconsistencies across 8 documentation files (model_version references)

## [3.2.0] — 2026-03-03

### Added
- `CHANGELOG.md` — semver-structured changelog
- `common_utils/pyproject.toml` — makes common_utils pip-installable
- Granular ADRs in `docs/decisions/` (one per decision)
- `httpx` dependency in CI for starlette TestClient support
- `pytest` + `requests` install step for integration-test CI job
- `_model_loaded()` helper in integration tests for graceful skip

### Changed
- **Black pinned to 26.1.0** in CI workflow and `.pre-commit-config.yaml` (was unpinned / 23.12.1)
- **E2E script** (`scripts/run_e2e.sh`): CI-friendly — no longer requires `.venv`
- **E2E CI job**: removed `|| true` — now fails properly on errors
- **Benchmarks CI job**: removed `continue-on-error: true` — detects regressions
- **carvision-dashboard** in `docker-compose.demo.yml`: moved to `profiles: [dashboard]` (streamlit not in prod image)
- Integration tests accept `degraded` health status (model not loaded in CI)
- Reformatted 6 files with black 26.1.0

### Removed
- Internal deployment docs from git tracking (kept locally via `.gitignore`)

## [3.1.0] — 2026-03-03

### Added
- **OpenTelemetry** distributed tracing in all 3 FastAPI apps via `common_utils/telemetry.py`
- `NLPInsight-Analyzer/data_card.md` — Financial PhraseBank dataset documentation
- `BankChurn-Predictor/src/bankchurn/fairness.py` — Disparate Impact, Equal Opportunity metrics
- `BankChurn-Predictor/tests/test_fairness.py` — 13 fairness audit tests
- Data validation with Pandera in all 3 projects (`data/validate_data.py`)
- `k8s/network-policies.yaml` and `k8s/pod-disruption-budgets.yaml`

### Changed
- **CI coverage thresholds** raised to 85% for all 3 projects (was 79-80%)
- **CI linting made strict** — removed `|| true` from black/isort/flake8 steps
- **BankChurn model_card.md**: VotingClassifier → StackingClassifier, Docker v1.5.0 → v3.0.0
- **CarVision model_card.md**: RandomForest → LightGBM, Docker v1.5.0 → v3.0.0
- **NLPInsight model_card.md**: expanded to match BankChurn/CarVision quality
- **BankChurn/CarVision requirements-prod.txt**: sklearn 1.8.0, numpy 2.4.x, pandas 2.3.x, scipy 1.17.x
- Black formatting applied across all 3 projects
- All requirements changed from `>=` to `~=` (compatible release)

### Fixed
- NLPInsight Dockerfile: kept `torch.testing` (required by transformers)
- BankChurn model loading: numpy MT19937 BitGenerator deserialization error
- Docker image optimization: `--no-compile`, aggressive cleanup

## [3.0.0] — 2026-02-28

### Added
- **StackingClassifier** for BankChurn (RF + GB + XGB + LGB → LR meta-learner)
- **LightGBM** for CarVision with FeatureEngineer pipeline (24 features)
- **FinBERT** (ProsusAI) for NLPInsight with TF-IDF + LogReg fallback
- SHAP explainability integrated in BankChurn API responses
- Streamlit dashboard for CarVision (4 tabs: explorer, prediction, analysis, comparison)
- Multi-stage Docker builds with non-root user
- Kubernetes manifests with Init Containers for model download from GCS
- HPA with CPU-only scaling (memory-based removed — fixed footprint)
- Argo Rollouts with canary strategy and analysis templates
- Helm chart (`helm/ml-portfolio/`)

### Changed
- Models retrained with Python 3.11.14 + sklearn 1.8.0
- Docker images pushed to GCP Artifact Registry (`us-central1-docker.pkg.dev`)
- All 3 services deployed on GKE (6 pods total)

## [2.0.0] — 2026-02-15

### Added
- Multi-cloud infrastructure: GCP (GKE) + AWS (EKS) via Terraform
- Prometheus + Grafana monitoring stack on Kubernetes
- MLflow experiment tracking (9 experiments tracked)
- CI/CD with GitHub Actions (10 workflows)
- Security scanning: Gitleaks, Bandit, Trivy, pip-audit
- DVC for data versioning
- Load testing with Locust

### Changed
- Migrated from local development to cloud deployment
- All models registered in MLflow

## [1.0.0] — 2025-09-01

### Added
- Initial portfolio with 3 ML projects
- BankChurn: LogisticRegression baseline (AUC 0.812)
- CarVision: RandomForest baseline
- NLPInsight: TF-IDF + LogisticRegression
- Basic FastAPI serving for all projects
- pytest test suites

---

[3.2.1]: https://github.com/DuqueOM/ML-MLOps-Portfolio/compare/v3.2.0...HEAD
[3.2.0]: https://github.com/DuqueOM/ML-MLOps-Portfolio/compare/v3.1.0...v3.2.0
[3.1.0]: https://github.com/DuqueOM/ML-MLOps-Portfolio/compare/v3.0.0...v3.1.0
[3.0.0]: https://github.com/DuqueOM/ML-MLOps-Portfolio/compare/v2.0.0...v3.0.0
[2.0.0]: https://github.com/DuqueOM/ML-MLOps-Portfolio/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/DuqueOM/ML-MLOps-Portfolio/releases/tag/v1.0.0
