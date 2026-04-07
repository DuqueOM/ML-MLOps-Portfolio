# AGENTS.md — ML-MLOps Portfolio

## Project Identity

**ML-MLOps Portfolio**: Production-ready ML systems with multi-cloud deployment (GKE + EKS), comprehensive observability, and enterprise CI/CD.

- **Author**: Duque Ortega Mutis
- **Repository**: https://github.com/DuqueOM/ML-MLOps-Portfolio
- **Docs**: https://duqueom.github.io/ML-MLOps-Portfolio/
- **Stack**: Python 3.11+, sklearn 1.8.x, FastAPI, Docker, Kubernetes, Terraform, GitHub Actions

## ML Services (3 microservices)

| Service | Type | Model | Key Metric |
|---------|------|-------|------------|
| **BankChurn-Predictor** | Classification | StackingClassifier (RF+GB+XGB+LGB→LR) | AUC 0.8693, F1 0.6243 |
| **NLPInsight-Analyzer** | NLP Sentiment | ProsusAI/FinBERT (transfer learning) | Accuracy 96.91% |
| **ChicagoTaxi-Demand-Pipeline** | Regression | LightGBM (n=500, lr=0.05) | R² 0.7955 |

All models at **v3.0.0**. Docker images in `us-central1-docker.pkg.dev/ml-portfolio-duque-om-202602/ml-portfolio-images/`.

## Critical Patterns — DO NOT VIOLATE

- **NEVER** use multi-worker uvicorn under Kubernetes — causes CPU thrashing, dilutes HPA signal (ADR-014)
- **NEVER** use memory-based HPA for ML pods — fixed RAM footprint mathematically prevents scale-down (ADR-001)
- **ALWAYS** use `KernelExplainer` for SHAP with StackingClassifier — `TreeExplainer` is incompatible (ADR-010)
- **ALWAYS** use compatible release pinning (`~=`) — numpy 2.x silently corrupts joblib-serialized models (ADR-005)
- **ALWAYS** use `asyncio.run_in_executor` + `ThreadPoolExecutor(4)` for inference — sklearn/XGBoost release GIL (ADR-015)
- **ALWAYS** verify `kubectl config current-context` before applying K8s manifests

## Project Structure

```
ML-MLOps-Portfolio/
├── BankChurn-Predictor/         # Classification service
├── NLPInsight-Analyzer/         # NLP sentiment service
├── ChicagoTaxi-Demand-Pipeline/ # Demand forecasting service
├── k8s/
│   ├── base/                    # Shared K8s manifests
│   └── overlays/
│       ├── gcp/                 # GKE-specific (Workload Identity)
│       └── aws/                 # EKS-specific (IRSA)
├── infra/
│   └── terraform/               # Cloud infrastructure IaC
├── helm/ml-portfolio/           # Helm chart (3 services + HPA + drift)
├── docs/
│   ├── decisions/               # 17 ADRs (001-017)
│   ├── architecture/            # System design docs
│   └── media/                   # GIFs, screenshots, videos
├── scripts/                     # Automation scripts
├── .github/workflows/           # CI/CD pipelines
└── monitoring/                  # Prometheus + Grafana configs
```

## Architecture Decision Records (ADRs)

| ADR | Decision | Rationale |
|-----|----------|-----------|
| 001 | CPU-only HPA | Memory footprint is fixed for ML models |
| 005 | Compatible release pinning | numpy 2.x breaks joblib serialization |
| 010 | SHAP KernelExplainer | TreeExplainer incompatible with StackingClassifier |
| 014 | Single-worker pod | Multi-worker uvicorn is anti-pattern under K8s |
| 015 | Async ThreadPoolExecutor | sklearn C extensions release GIL |
| 016 | GCP/AWS performance parity | e2-medium vs t3.medium documented as FinOps decision |
| 017 | Custom vs managed ML platforms | FastAPI+K8s primary, SageMaker/Vertex as complements |

Full index: `docs/decisions/README.md`

## CI/CD Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci-mlops.yml` | Push/PR to main | Lint, test, build for all 3 services |
| `ci-infra.yml` | Changes to infra/ | Terraform validate + plan |
| `deploy-gcp.yml` | Tag push | Deploy to GKE |
| `deploy-aws.yml` | Tag push | Deploy to EKS |
| `drift-detection.yml` | Daily cron | PSI-based drift check |
| `retrain-bankchurn.yml` | Drift alert | Automated retraining |

## Monitoring

- **Prometheus**: Custom metrics per service (`bankchurn_requests_total`, `nlpinsight_*`, `chicagotaxi_*`)
- **Grafana**: ML performance dashboard at `infra/grafana/dashboards/ml-performance.json`
- **Drift**: PSI-based detection via `k8s/drift-detection-cronjob.yaml`
- **Load testing**: Locust scripts in `scripts/load_test_services.py`

## File Conventions

- **Python**: Type hints on all public functions, Pydantic for config, Google docstrings
- **K8s YAML**: Kustomize overlays, labels include `app`, `version`, `environment`
- **Terraform**: Variables with description + type, remote state with locking
- **Tests**: `tests/unit/`, `tests/integration/`, `tests/e2e/` — minimum 80% coverage
- **Docs**: MkDocs Material theme, deployed via GitHub Actions to GitHub Pages
