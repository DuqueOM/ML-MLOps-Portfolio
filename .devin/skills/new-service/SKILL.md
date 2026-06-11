---
name: new-service
description: Create a complete new ML service from template — end-to-end scaffolding
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash(cp:*)
  - Bash(mkdir:*)
  - Bash(sed:*)
  - Bash(docker:*)
  - Bash(kubectl:*)
  - Bash(dvc:*)
  - Bash(terraform:*)
when_to_use: >
  Use when creating a new ML microservice from scratch for a business problem.
  Examples: 'create a new churn prediction service', 'scaffold a fraud detection API',
  'new service for loan default prediction'
argument-hint: "<service-name> <business-problem>"
arguments:
  - service-name
  - business-problem
authorization_mode:
  scaffold_files: AUTO           # reversible by `rm -rf <ServiceName>/`
  init_dvc: AUTO                 # creates dvc.yaml — reversible
  create_mlflow_experiment: AUTO # creates an experiment in MLflow; harmless
  wire_cicd: AUTO                # populates .github/workflows/ — git-tracked
  push_initial_commit: CONSULT   # the first git push of the new service
  escalation_triggers:
    - target_dir_exists: STOP            # never overwrite existing service
    - eda_artifacts_missing: STOP        # require eda/ phase done first (ADR-004)
    - service_name_collides: STOP        # name clash with another service in repo
---

# Create New ML Service

Guides creation of a complete, production-ready ML service using the template system.

## Inputs
- `$service-name`: Service slug (e.g., `bankchurn`, `frauddetect`)
- `$business-problem`: What the service predicts/classifies

## Goal
A fully deployed, tested, monitored ML service with all quality gates passing,
drift detection running, and documentation complete.

## Pre-conditions
- `templates/scripts/new-service.sh` exists and is executable
- The caller has specified ServiceName (PascalCase) and service_slug (snake_case)
- Cloud target is known (gcp, aws, or both)

## Steps

### 1. Gather Requirements
**Human checkpoint**: Confirm requirements before scaffolding.

Answer these questions:
1. **Business problem**: What does this service predict/classify/estimate?
2. **Dataset**: Source, size, features, target distribution
3. **Model type**: Classification, regression, NLP, time series?
4. **Scale**: Expected request volume, latency requirements
5. **Explainability**: Is SHAP required? (High-stakes decisions = yes)

### 2. Run Scaffolding Script

```bash
bash templates/scripts/new-service.sh "$service-name" "$service-slug"
```

Verify no remaining placeholders:
```bash
grep -r "{ServiceName}\|{service}\|{SERVICE}" $service-name/ --include="*.py" --include="*.yaml" | head -20
```

**Success criteria**: Directory created with zero remaining `{ServiceName}`, `{service}`, or `{SERVICE}` placeholders. Run `examples/minimal/` if this is the first time to validate template works.

### 3. Data Validation (Agent-DataValidator)

1. Define Pandera schema in `src/$service-name/schemas.py`
2. Check for temporal data → review for leakage risk
3. Create background data for SHAP (50 representative samples)
4. Version data with DVC: `dvc add data/raw/dataset.csv`

**Success criteria**: Pandera schema validates sample data without errors. DVC tracking configured.

### 4. Training Pipeline (Agent-MLTrainer)

1. Implement `FeatureEngineer` class in `src/$service-name/training/features.py`
2. Define model pipeline in `src/$service-name/training/model.py`
3. Implement `Trainer.run()` in `src/$service-name/training/train.py`:
   - load_data() + Pandera validation
   - engineer_features()
   - split_train_val_test() (temporal if dates exist)
   - cross_validate() with StratifiedKFold
   - evaluate() with optimal threshold
   - fairness_check() (DIR >= 0.80)
   - save_artifacts() with SHA256
   - log_to_mlflow()
   - quality_gates()
4. Configure Optuna (minimum 50 trials)
5. Create MLflow experiment

**Success criteria**: `python -m src.$service-name.cli train --data data/raw/dataset.csv` completes with all quality gates passing.

### 5. Serving API (Agent-APIBuilder)

1. Define Pydantic schemas in `app/schemas.py`
2. Keep the generated FastAPI split intact:
   - `app/main.py` owns lifespan, `/health`, `/ready`, CORS, tracing,
     error envelope, `/model/info`, and `/model/reload`
   - `app/fastapi_app.py` owns `/predict`, `/predict_batch`,
     `/metrics`, model loading, feature parity, SHAP, and prediction
     logging
3. Customize the existing endpoints without changing the contract:
   - `/predict` with ThreadPoolExecutor (NEVER sync predict in async)
   - `/predict?explain=true` with SHAP KernelExplainer
   - `/predict_batch` for batch predictions (note: underscore, not slash)
   - `/health` for liveness probe (200 while process alive)
   - `/ready` for readiness probe (503 until warm-up complete — D-23)
   - `/metrics` for Prometheus
4. Keep `FeatureEngineer.transform_inference()` aligned with training
5. Define `predict_proba_wrapper` for SHAP in original feature space
6. Write API tests with TestClient and keep
   `tests/test_fastapi_template_contract.py` passing

**Success criteria**: `pytest tests/test_fastapi_template_contract.py tests/test_api.py -v` passes. `curl localhost:8000/health` returns healthy and `/ready` returns 200 only after the model is loaded and warmed.

### 6. Containerization (Agent-DockerBuilder)

1. Customize `Dockerfile` (multi-stage, non-root, HEALTHCHECK)
2. Verify `.dockerignore` excludes models/, data/raw/, tests/
3. Build and test locally:
   ```bash
   docker build -t $service-name:dev .
   docker run -p 8000:8000 $service-name:dev
   curl localhost:8000/health
   ```

**Success criteria**: Docker build succeeds. Container starts and /health returns 200.

### 7. Kubernetes (Agent-K8sBuilder)

1. Create deployment from `templates/k8s/deployment.yaml`
2. Create HPA (CPU-only, 50-70% target) from `templates/k8s/hpa.yaml`
3. Create Service from `templates/k8s/service.yaml`
4. Create Kustomize overlays for GCP and AWS
5. Init container configured for model download

**Success criteria**: `for o in gcp-dev gcp-staging gcp-prod aws-dev aws-staging aws-prod; do kustomize build k8s/overlays/$o; done` renders valid YAML for all 6 overlays.

### 8. Infrastructure (Agent-TerraformBuilder)

1. Add container repository in `infra/terraform/{cloud}/`
2. Add IAM permissions (Workload Identity for GCP, IRSA for AWS)
3. `terraform plan` → verify → `terraform apply`

**Success criteria**: `terraform plan` shows expected resources with no errors.

### 9. CI/CD (Agent-CICDBuilder)

1. Add service to build matrix in `.github/workflows/ci.yml`
2. Add drift detection to scheduled workflow
3. Create `retrain-$service-name.yml` with quality gates
4. Configure GitHub Secrets

**Success criteria**: CI workflow triggers on PR and runs tests + lint + type check.

### 10. Monitoring (Agent-MonitoringSetup)

1. Verify `/metrics` exports `{service}_requests_total`, `{service}_request_duration_seconds`
2. Create Grafana dashboard from `templates/monitoring/grafana-dashboard.json`
3. Configure P1-P4 alerts in AlertManager
4. Verify Pushgateway connectivity for drift metrics

**Success criteria**: Grafana dashboard shows live metrics. Alert rules configured.

### 11. Drift Detection (Agent-DriftSetup)

1. Define PSI thresholds per feature with domain reasoning
2. Implement `drift_detection.py` with quantile-based bins
3. Create K8s CronJob for scheduled drift checks
4. Configure heartbeat alert (48h timeout)

**Success criteria**: CronJob runs successfully. PSI metrics appear in Pushgateway.

### 12. Documentation (Agent-DocumentationAI)

1. Create ADR for model selection decision
2. Write service `README.md` with real metrics
3. Create runbook with P1-P4 commands
4. Update root project documentation

**Success criteria**: README includes measured metrics, not estimates.

### 13. Testing (Agent-TestGenerator)

1. Data leakage regression test
2. SHAP consistency + non-zero + original feature space tests
3. Quality gate threshold tests
4. Inference latency SLA test (P95 < SLA)
5. Fairness DIR >= 0.80 test
6. Load test with Locust (100 concurrent, < 1% error)

**Success criteria**: `pytest tests/ -v --cov=src --cov-report=term-missing` shows >= 90% coverage.

## Rules
- Never skip quality gates — all must pass before deployment
- Never use `==` for ML package pinning — use `~=` (compatible release)
- Never bake models into Docker images — use init container pattern
- Always create an ADR for every non-trivial decision
- Always measure and document real metrics, not estimates

## Acceptance Criteria

A service is production-ready when ALL of these pass:
- [ ] Test coverage >= 90%
- [ ] Load test < 1% errors under 100 concurrent users
- [ ] P95 latency within SLA
- [ ] Primary metric >= quality gate
- [ ] Fairness DIR >= 0.80
- [ ] Drift detection configured + CronJob running
- [ ] Heartbeat alert configured
- [ ] IRSA/Workload Identity configured (no hardcoded credentials)
- [ ] ADRs written for all non-trivial decisions
- [ ] README with real measured metrics
- [ ] Runbook with executable P1-P4 commands
