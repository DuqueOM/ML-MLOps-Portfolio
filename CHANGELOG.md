# Changelog

All notable changes to the ML-MLOps Portfolio are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [Semantic Versioning](https://semver.org/).

---

## [3.5.0] — 2026-03-05

### Fixed
- **ChicagoTaxi data leakage** — removed same-period aggregate features (`avg_fare`, `avg_distance_miles`, `avg_speed_mph`) that leaked future information; replaced with lag features (`trip_count_lag_1h`, `_lag_24h`, `_lag_168h`, `_rolling_24h`); switched from random to temporal train/test split. R² improved from 0.905 → 0.9649 with honest, leak-free features
- **Version inconsistencies** — unified all docs to v3.5.0, fixed dates (June 2026 → March 2026, February 2026 → March 2026) across README badge, model cards, architecture docs
- **`sys.path.insert` hack removed** — `common_utils` is now a pip-installable package (`pip install -e ./common_utils`); removed `sys.path.insert(0, ...)` from all 3 FastAPI apps, 3 conftest.py files, and test_integration.py

### Changed
- **Portfolio reduced to 3 projects** — removed (MAPE 32.9% not defensible); moved to `Applied-ML-Projects` repo alongside recovered TelecomAI project
- **NLPInsight dataset upgrade** — Financial PhraseBank (4,845 sentences, 97% acc) → Twitter Financial News Sentiment (11,931 real tweets, 80.6% acc). Harder, noisier, more realistic benchmark
- **NLPInsight production model** — TF-IDF + LogReg for CPU deployment (<5ms); FinBERT fine-tuning supported via training pipeline when GPU available
- **README.md** — updated to 3 projects, architecture diagram without all metrics updated
- **common_utils/pyproject.toml** — fixed package discovery (`package-dir` mapping), license reference, version 1.2.0
- **Version badges** — all docs updated from 3.4.0 → 3.5.0

### Added
- **ADR-009: Simplification** — documents deliberate evaluation of each infrastructure component, data leakage fix, and removal rationale
- **ChicagoTaxi lag features** — `compute_lag_features()` and `temporal_train_test_split()` functions in `batch_predict.py`
- **BankChurn Gradio demo** — `app/gradio_demo.py` interactive churn prediction UI with risk assessment

## [3.4.0] — 2026-03-04

### Added
- **ChicagoTaxi Demand Pipeline** — 4th portfolio project: PySpark ETL processing 6.3M taxi trips (2.8 GB CSV → 95 MB Parquet), Dask batch prediction (19K rows/sec), FastAPI serving layer, R² 0.905
- `ChicagoTaxi-Demand-Pipeline/` — full project structure: scripts, FastAPI app, Dockerfile (Python 3.11), tests (22 passing), model card, config
- `k8s/chicagotaxi-deployment.yaml` — Deployment + Service + HPA (CPU-only scaling)
- `k8s/overlays/aws/chicagotaxi-deployment-aws.yaml` — AWS EKS overlay
- ChicagoTaxi entries in: model-configmaps (GCP + AWS), upload-models-to-gcs.sh, Helm values.yaml, CI pipeline matrix
- **Structured JSON logging** — `common_utils/logging.py` (JSONFormatter + HumanFormatter), integrated in all 3 FastAPI apps
- **mypy config** — `mypy.ini` at repo root, mypy step in CI quality gates
- **Docker optimization** — `.so` stripping, test data removal (BankChurn), aggressive torch cleanup (NLPInsight)
- **Argo Rollouts** — `scripts/deploy-canary.sh`, `docs/decisions/008-argo-rollouts-canary.md`

### Changed
- **RUNBOOK.md streamlined** — 603 → 124 lines (80% reduction); removed verbose padding, kept essential operations
- **README.md** — updated to 3 projects, architecture diagram includes ChicagoTaxi, tech stack adds PySpark + Dask, version 3.4.0
- **CI pipeline** — ChicagoTaxi added to test matrix, quality gates (black, flake8, mypy), model card verification
- K8s deployments updated with `LOG_FORMAT=json`, `SERVICE_NAME`, `LOG_LEVEL` env vars

## [3.3.2] — 2026-03-04

### Changed
- **Project documentation rewritten** — all 3 MkDocs project pages now explain the business problem, metric rationale, and cost of errors (not just metrics tables)
- **Overclaiming language removed** — "Enterprise-Grade", "production-grade" replaced with concrete evidence statements across README, docs/index.md, ARCHITECTURE_PORTFOLIO.md, DEPLOYMENT_EVIDENCE.md
- **Version consistency** — all 40+ docs updated to v3.3.1 with consistent Grafana panel counts (25 panels / 2 dashboards) and latency data from canonical DEPLOYMENT_EVIDENCE.md

### Added
- **ADR-006: Drift-Triggered Retraining** — K8s CronJob queries Prometheus for PSI/AUC/RMSE/F1 drift; triggers GitHub Actions `workflow_dispatch` if thresholds exceeded
- **ADR-007: Feature Store Decision** — documents why feature stores don't apply to request-time features, and what the Feast architecture would look like at scale
- **`k8s/drift-retraining-cronjob.yaml`** — lightweight CronJob implementation of ADR-006
- **NLPInsight model_card.md link fixed** — was pointing to non-existent `models/model_card.md`, corrected to `model_card.md`

## [3.3.1] — 2026-03-03

### Added
- **Multi-target Dockerfile** — `--target api` and `--target dashboard` builds from single Dockerfile

### Changed
- **FastAPI `root_path`** — all 3 APIs now support `API_ROOT_PATH` env var for Ingress path-based routing
- **Load test metrics improved** — p50 160ms, p95 480ms, 973 requests, 0% errors (10 users, 2 min)

### Fixed
- Dashboard image missing Streamlit due to early pip cleanup in Dockerfile
- **Grafana `ml-portfolio-dashboard.json`** — replaced 8 broken panels using non-existent metrics (`http_requests_total`, `predictions_total`, `model_drift_score`, `node_cpu_seconds_total`, `container_memory_usage_bytes`) with real per-service metrics
- **Prometheus alert rules** — removed alerts referencing non-existent metrics (`model_drift_score`, `kube_node_status_condition`, `container_*`); replaced with `process_resident_memory_bytes` per-service alerts
- **Prometheus scrape config** — fixed duplicate scrape (port 80 vs 8000); removed node-exporter job (not deployed); removed MLflow scrape (no `/metrics` endpoint)
- **Result**: 16/16 Prometheus targets UP (0 DOWN), 16 alert rules loaded, 2 Grafana dashboards fully functional

## [3.3.0] — 2026-03-03

### Added
- **Adversarial/robustness tests** (`tests/adversarial/test_robustness.py`) — 43 tests covering edge cases, boundary conditions, SQL injection, XSS, NaN/Inf, unicode for all 3 services
- **Kubernetes Pod Security Standards** — baseline enforce + restricted warn/audit labels on `ml-portfolio` namespace
- **Staging environment** — `staging.tfvars` for both GCP and AWS Terraform with reduced resources
- **CI test model generator** (`scripts/generate_ci_test_models.py`) — creates lightweight sklearn models for Docker Compose integration tests

### Changed
- **Prometheus alert rules** — replaced generic `http_requests_total` with actual per-service metrics (`bankchurn_requests_total`, `nlpinsight_requests_total`); per-service latency and prediction rate alerts
- **Security scans now blocking** — Gitleaks `continue-on-error` removed; Bandit fails on HIGH+ severity issues; pip-audit remains advisory
- **Spanish→English comments** — translated all Spanish comments in CI workflows, Dockerfiles, `config.yaml`, `docker-compose.yml`, `run_e2e.sh`
- **CI integration test** — added `generate_ci_test_models.py` step before Docker Compose spin-up
- **Helm namespace template** — added Pod Security Standards labels

### Fixed
- Prometheus rules that would never fire due to metric name mismatch
- E2E tests skipping in CI due to missing models

## [3.2.1] — 2026-03-03

### Added
- **NLPInsight fairness module** (`src/nlpinsight/fairness.py`) — per-class F1 parity, group fairness (16 tests)
- Trivy DB repository override (`ghcr.io/aquasecurity/trivy-db:2`) to fix mirror.gcr.io 404

### Changed
- **All 3 projects now have fairness audits** (was only BankChurn)
- Trivy action pinned to `0.28.0` (was `@master`)
- Documentation standardized: 30+ files updated to v3.0.0 models / v3.2.0 portfolio
- Test total: 294 (198 + 74 + 22), coverage 90–98%

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
- Dashboard in `docker-compose.demo.yml`: moved to `profiles: [dashboard]` (streamlit not in prod image)
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
- **NLPInsight model_card.md**: expanded to match BankChurn quality
- **BankChurn requirements-prod.txt**: sklearn 1.8.0, numpy 2.4.x, pandas 2.3.x, scipy 1.17.x
- Black formatting applied across all 3 projects
- All requirements changed from `>=` to `~=` (compatible release)

### Fixed
- NLPInsight Dockerfile: kept `torch.testing` (required by transformers)
- BankChurn model loading: numpy MT19937 BitGenerator deserialization error
- Docker image optimization: `--no-compile`, aggressive cleanup

## [3.0.0] — 2026-02-28

### Added
- **StackingClassifier** for BankChurn (RF + GB + XGB + LGB → LR meta-learner)
- **LightGBM** for vehicle pricing with FeatureEngineer pipeline (moved to Applied-ML-Projects)
- **FinBERT** (ProsusAI) for NLPInsight with TF-IDF + LogReg fallback
- SHAP explainability integrated in BankChurn API responses
- Streamlit dashboard for vehicle pricing (moved to Applied-ML-Projects)
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
- NLPInsight: TF-IDF + LogisticRegression
- Basic FastAPI serving for all projects
- pytest test suites

---

[3.3.0]: https://github.com/DuqueOM/ML-MLOps-Portfolio/compare/v3.2.1...HEAD
[3.2.1]: https://github.com/DuqueOM/ML-MLOps-Portfolio/compare/v3.2.0...v3.2.1
[3.2.0]: https://github.com/DuqueOM/ML-MLOps-Portfolio/compare/v3.1.0...v3.2.0
[3.1.0]: https://github.com/DuqueOM/ML-MLOps-Portfolio/compare/v3.0.0...v3.1.0
[3.0.0]: https://github.com/DuqueOM/ML-MLOps-Portfolio/compare/v2.0.0...v3.0.0
[2.0.0]: https://github.com/DuqueOM/ML-MLOps-Portfolio/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/DuqueOM/ML-MLOps-Portfolio/releases/tag/v1.0.0
