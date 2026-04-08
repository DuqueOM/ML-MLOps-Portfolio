# AGENTS.md — ML-MLOps Portfolio

## Project Identity

**ML-MLOps Portfolio**: Production-ready ML systems with multi-cloud deployment (GKE + EKS),
comprehensive observability, and enterprise CI/CD. Built and operated from scratch — every
architectural decision documented in 17 ADRs with measured trade-offs.

- **Author**: Duque Ortega Mutis
- **Repository**: https://github.com/DuqueOM/ML-MLOps-Portfolio
- **Docs**: https://duqueom.github.io/ML-MLOps-Portfolio/
- **Stack**: Python 3.11+, sklearn 1.8.x, FastAPI, Docker, Kubernetes, Terraform, GitHub Actions

## ML Services (3 microservices)

| Service | Type | Production Model | Key Metric | Optional (GPU) |
|---------|------|-----------------|------------|----------------|
| **BankChurn-Predictor** | Classification | StackingClassifier (RF+GB+XGB+LGB→LR) | AUC 0.87, F1 0.62 | — |
| **NLPInsight-Analyzer** | NLP Sentiment | TF-IDF + LogisticRegression (CPU, 5ms) | Accuracy 80.6%, F1-macro 0.75 | ProsusAI/FinBERT |
| **ChicagoTaxi-Demand-Pipeline** | Regression | LightGBM (PySpark ETL, 6.3M rows) | R² 0.96, RMSE 7.87 | — |

> **NLPInsight dual-backend**: `model.joblib` (TF-IDF+LogReg, 5ms, 267MB image) is production.
> `config.json` triggers FinBERT path (87ms, 1.4GB image) — GPU-only, not deployed in K8s.
> Do NOT report FinBERT accuracy (96.91%) as the production metric — production is 80.6%.

All models at **v3.6.0**. Docker images in `us-central1-docker.pkg.dev/ml-portfolio-duque-om-202602/ml-portfolio-images/`.

## Critical Patterns — DO NOT VIOLATE

- **NEVER** use multi-worker uvicorn under Kubernetes — causes CPU thrashing, dilutes HPA signal (ADR-014)
- **NEVER** use memory-based HPA for ML pods — fixed RAM footprint mathematically prevents scale-down (ADR-001)
- **ALWAYS** use `KernelExplainer` for SHAP with StackingClassifier — `TreeExplainer` is incompatible (ADR-010)
- **ALWAYS** use compatible release pinning (`~=`) — numpy 2.x silently corrupts joblib-serialized models (ADR-005)
- **ALWAYS** use `asyncio.run_in_executor` + `ThreadPoolExecutor(4)` for CPU-bound inference (ADR-015)
- **ALWAYS** verify `kubectl config current-context` before applying K8s manifests
- **NEVER** bake model artifacts into Docker images — use emptyDir + Init Container (ADR-002)
- **ALWAYS** use temporal train/test split for ChicagoTaxi — lag features only, no same-period aggregates (ADR-009)

## HPA Targets (CPU-only — ADR-001)

| Service | CPU Target | Min Replicas | Max Replicas |
|---------|-----------|-------------|-------------|
| BankChurn-Predictor | **50%** | 1 | 5 |
| NLPInsight-Analyzer | **60%** | 1 | 3 |
| ChicagoTaxi-Demand-Pipeline | **60%** | 1 | 3 |

> These targets were refined from 70–75% to 50–60% by ADR-014. If you see 70% or 75% anywhere in
> the codebase, that is the OLD value — update to the above.

## Project Structure

```
ML-MLOps-Portfolio/
├── BankChurn-Predictor/          # Classification service
├── NLPInsight-Analyzer/          # NLP sentiment service (TF-IDF prod / FinBERT GPU optional)
├── ChicagoTaxi-Demand-Pipeline/  # Demand forecasting service
├── k8s/
│   ├── base/                     # Shared K8s manifests
│   └── overlays/
│       ├── gcp/                  # GKE-specific (Workload Identity)
│       └── aws/                  # EKS-specific (IRSA)
├── infra/
│   └── terraform/                # Cloud infrastructure IaC (GCP + AWS)
├── helm/ml-portfolio/            # Helm chart (3 services + HPA + drift)
├── docs/
│   ├── decisions/                # 17 ADRs (001–017)
│   ├── architecture/             # System design docs
│   └── media/                    # GIFs, screenshots, videos
├── scripts/                      # Automation scripts
├── .github/workflows/            # CI/CD pipelines
├── monitoring/                   # Prometheus + Grafana configs
├── AGENTS.md                     # This file — agentic development config
└── .windsurf/                    # Windsurf Cascade agentic rules, skills, workflows
```

## Architecture Decision Records (ADRs)

| ADR | Decision | Rationale |
|-----|----------|-----------|
| 001 | CPU-only HPA | Memory footprint is fixed for ML models — memory HPA cannot scale down |
| 002 | emptyDir + Init Container | Decouples model versioning from Docker image lifecycle |
| 003 | StackingClassifier | AUC 0.87 vs 0.86 single model; demonstrates ensemble methodology |
| 005 | Compatible release pinning | numpy 2.x silently corrupts joblib deserialization |
| 009 | Simplification / removals | Removed CarVision (MAPE 32.9%); fixed ChicagoTaxi data leakage |
| 010 | SHAP KernelExplainer | TreeExplainer incompatible with StackingClassifier |
| 014 | Single-worker pod | Multi-worker uvicorn is anti-pattern under K8s |
| 015 | Async ThreadPoolExecutor | sklearn C extensions release GIL — real parallelism with 1 process |
| 016 | GCP/AWS performance parity | e2-medium vs t3.medium documented as FinOps decision |
| 017 | Custom vs managed ML | FastAPI+K8s primary; SageMaker/Vertex as demonstrated complements |

Full index: `docs/decisions/` | Live: https://duqueom.github.io/ML-MLOps-Portfolio/architecture/decisions/

## CI/CD Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------| 
| `ci-mlops.yml` | Push/PR to main | Lint, test, build for all 3 services |
| `ci-infra.yml` | Changes to infra/ | Terraform validate + plan |
| `deploy-gcp.yml` | Tag push | Deploy to GKE |
| `deploy-aws.yml` | Tag push | Deploy to EKS |
| `drift-detection.yml` | Daily cron | PSI-based drift check (threshold 0.25) |
| `retrain-bankchurn.yml` | Drift alert | Automated retraining |

## Monitoring

- **Prometheus**: Custom metrics per service (`bankchurn_requests_total`, `nlpinsight_*`, `chicagotaxi_*`)
- **Grafana**: ML performance dashboard at `infra/grafana/dashboards/ml-performance.json`
- **Drift**: PSI-based detection via `k8s/base/drift-retraining-cronjob.yaml` (daily 06:00 UTC)
- **Load testing**: Locust scripts in `scripts/load_test_services.py`

## File Conventions

- **Python**: Type hints on all public functions, Pydantic for config/schemas, Google docstrings
- **K8s YAML**: Kustomize overlays, labels include `app`, `version`, `environment`, `managed-by`
- **Terraform**: Variables with description + type, remote state with locking
- **Docker**: Multi-stage builds, non-root USER, HEALTHCHECK, no COPY of secrets or model artifacts
- **Tests**: `tests/unit/`, `tests/integration/`, `tests/e2e/` — minimum 80% coverage enforced in CI
- **Docs**: MkDocs Material theme, deployed via GitHub Actions to GitHub Pages

## Agentic Configuration (.windsurf/)

This project uses a layered agentic architecture for AI-assisted development with Windsurf Cascade.
The configuration encodes operational knowledge from 17 ADRs and 3 production incidents into
behavioral constraints, reusable skills, and structured workflows.

```
.windsurf/
├── rules/                           # Behavioral constraints (7 rules, context-aware)
│   ├── 01-mlops-conventions.md      # always_on — core stack + ADR patterns
│   ├── 02-kubernetes.md             # glob: k8s/**/*.yaml, helm/**/*.yaml
│   ├── 03-terraform.md              # glob: **/*.tf
│   ├── 04-python-ml.md              # glob: **/*.py
│   ├── 05-github-actions.md         # glob: .github/workflows/*.yml
│   ├── 06-documentation.md          # glob: docs/**/*.md
│   └── 07-docker.md                 # glob: **/Dockerfile*, docker-compose*.yml
├── skills/                          # Multi-step operational procedures (6 skills)
│   ├── debug-ml-inference/          # SKILL.md + adr-quick-reference.md
│   ├── deploy-gke/                  # SKILL.md + checklist.md
│   ├── deploy-aws/                  # SKILL.md + checklist.md + IRSA troubleshooting
│   ├── drift-detection/             # SKILL.md + per-service PSI thresholds
│   ├── model-retrain/               # SKILL.md + per-service validation criteria
│   └── release-checklist/           # SKILL.md + CHANGELOG version template
└── workflows/                       # Prompt-triggered structured workflows (6 workflows)
    ├── release.md                   # /release — full multi-cloud release process
    ├── retrain.md                   # /retrain — model retraining with gates
    ├── load-test.md                 # /load-test — Locust performance testing
    ├── new-adr.md                   # /new-adr — create Architecture Decision Record
    ├── incident.md                  # /incident — ML service incident response
    └── drift-check.md               # /drift-check — PSI drift analysis
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

### MCP Servers (Recommended for full agent capability)

| MCP Server | Purpose | Integration Point |
|------------|---------|-------------------|
| `@anthropic-ai/mcp-server-kubernetes` | K8s cluster management | Deploy skills |
| `mcp-server-terraform` | Terraform plan/apply | IaC workflows |
| `mcp-prometheus` | PromQL queries | Drift detection, monitoring |
| `mcp-docker` | Container management | Build & test |
| `supabase-mcp-server` | Database access | Training pipelines |
| `pinecone-mcp-server` | Vector search | NLPInsight embeddings |

### Cloud Integration

| Provider | Auth | Registry | Storage | K8s | IaC |
|----------|------|----------|---------|-----|-----|
| **GCP** | Workload Identity | Artifact Registry | GCS | GKE (us-central1) | Terraform |
| **AWS** | IRSA | ECR | S3 | EKS (us-east-1) | Terraform |

## AI Transparency

This project was built using Windsurf Cascade (AI-assisted coding) for code generation and
boilerplate. All architectural decisions, system design, trade-off analysis, incident diagnosis,
and ADR documentation are the author's. AI tools accelerate throughput — they don't replace
engineering judgment.