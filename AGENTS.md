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
- **Docker**: Multi-stage builds, non-root USER, HEALTHCHECK, no COPY of secrets
- **Tests**: `tests/unit/`, `tests/integration/`, `tests/e2e/` — minimum 80% coverage
- **Docs**: MkDocs Material theme, deployed via GitHub Actions to GitHub Pages

## Agentic Configuration (.windsurf/)

This project uses a layered agentic architecture inspired by Anthropic's production patterns (AutoDream consolidation, fork-based subagents, 4-type memory taxonomy):

```
.windsurf/
├── rules/                          # Behavioral constraints (7 rules)
│   ├── 01-mlops-conventions.md     # always_on — core conventions
│   ├── 02-kubernetes.md            # glob: k8s/**/*.yaml, helm/**/*.yaml
│   ├── 03-terraform.md             # glob: **/*.tf
│   ├── 04-python-ml.md             # glob: **/*.py
│   ├── 05-github-actions.md        # glob: .github/workflows/*.yml
│   ├── 06-documentation.md         # glob: docs/**/*.md
│   └── 07-docker.md                # glob: **/Dockerfile*, **/docker-compose*.yml
├── skills/                         # Multi-step procedures (6 skills)
│   ├── debug-ml-inference/         # SKILL.md + adr-quick-reference.md
│   ├── deploy-gke/                 # SKILL.md + checklist.md
│   ├── deploy-aws/                 # SKILL.md + checklist.md
│   ├── drift-detection/            # SKILL.md + psi-thresholds.md
│   ├── model-retrain/              # SKILL.md + validation-criteria.md
│   └── release-checklist/          # SKILL.md + version-template.md
└── workflows/                      # Repeatable prompt templates (6 workflows)
    ├── release.md                  # /release — full release process
    ├── retrain.md                  # /retrain — model retraining
    ├── load-test.md                # /load-test — Locust performance testing
    ├── new-adr.md                  # /new-adr — new Architecture Decision Record
    ├── incident.md                 # /incident — ML service incident response
    └── drift-check.md              # /drift-check — PSI drift analysis
```

### Skills → Workflow Cross-References

| Trigger | Skill Invoked | Workflow Chained |
|---------|--------------|-----------------|
| Inference bug | `debug-ml-inference` | `/incident` |
| Drift alert (PSI ≥ 0.25) | `drift-detection` | `/retrain` |
| Version release | `release-checklist` | `/release` |
| Tag push (GKE) | `deploy-gke` | — |
| Tag push (EKS) | `deploy-aws` | — |
| Scheduled retrain | `model-retrain` | `/drift-check` post-deploy |

### MCP Servers (Recommended)

| MCP Server | Purpose | Integration Point |
|------------|---------|-------------------|
| `supabase-mcp-server` | Database access for feature stores | Training pipelines |
| `pinecone-mcp-server` | Vector search for embeddings | NLPInsight service |
| `@anthropic-ai/mcp-server-kubernetes` | K8s cluster management | Deploy skills |
| `mcp-server-terraform` | Terraform plan/apply | IaC workflows |
| `mcp-prometheus` | PromQL queries | Drift detection, monitoring |
| `mcp-docker` | Container management | Build & test |

### Cloud Integration

| Provider | Auth | Registry | Storage | K8s | IaC |
|----------|------|----------|---------|-----|-----|
| **GCP** | Workload Identity | Artifact Registry | GCS | GKE (us-central1) | Terraform |
| **AWS** | IRSA | ECR | S3 | EKS (us-east-1) | Terraform |
