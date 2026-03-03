# Multi-Cloud Deployment Evidence

> Production deployment of 3 ML services on **Google Cloud Platform (GKE)** and **Amazon Web Services (EKS)**.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  GCP (us-central1)             │  AWS (us-east-1)           │
│                                │                            │
│  GKE Cluster (e2-medium)       │  EKS Cluster (t3.large)    │
│  ┌──────────┐ ┌──────────┐     │  ┌──────────┐ ┌────────┐   │
│  │BankChurn │ │CarVision │     │  │BankChurn │ │CarVis. │   │
│  │  :8000   │ │:8000+8501│     │  │  :8000   │ │  :8000 │   │
│  └────┬─────┘ └────┬─────┘     │  └────┬─────┘ └───┬────┘   │
│  ┌────┴─────┐ ┌────┴─────┐     │  ┌────┴─────┐ ┌───┴────┐   │
│  │NLPInsight│ │ MLflow   │     │  │NLPInsigh│ │ MLflow │   │
│  │  :8000   │ │  :5000   │     │  │  :8000   │ │  :5000 │   │
│  └──────────┘ └──────────┘     │  └──────────┘ └────────┘   │
│  Prometheus + Grafana          │  Prometheus + Grafana      │
│  GCE Ingress (static IP)       │  ALB (DNS)                 │
│  Artifact Registry + GCS       │  ECR + S3                  │
│  Cloud SQL (PostgreSQL)        │  RDS (PostgreSQL)          │
│  Terraform IaC                 │  Terraform IaC             │
└─────────────────────────────────────────────────────────────┘
```

## Verified Capabilities

| Capability | GCP | AWS | Evidence |
|------------|-----|-----|----------|
| Container orchestration (K8s) | GKE | EKS | `kubectl get pods -n ml-portfolio` |
| Auto-scaling (HPA) | CPU-based | CPU-based | Scaled 3→1 pods under low load |
| Model serving (FastAPI) | 3 services | 3 services | `/health` + `/predict` endpoints |
| Batch prediction | All 3 APIs | All 3 APIs | `/predict_batch` endpoints |
| Monitoring (Prometheus) | Custom metrics | Custom metrics | `bankchurn_*`, `carvision_*`, `nlpinsight_*` |
| Dashboards (Grafana) | ML Performance | ML Performance | Latency, throughput, error rates |
| Experiment tracking (MLflow) | Cloud SQL backend | RDS backend | Hyperparameter comparison |
| Infrastructure as Code | Terraform GCP | Terraform AWS | `infra/terraform/{gcp,aws}/` |
| CI/CD (GitHub Actions) | Build + Deploy | Build + Deploy | 10-job pipeline, GHCR publish |
| Container registry | Artifact Registry | ECR | Multi-arch images |
| Object storage (models) | GCS | S3 | Init containers download on boot |
| Data versioning | DVC + GCS | DVC + S3 | `dvc push/pull` |
| Security scanning | Trivy + Bandit + Gitleaks | Trivy + Bandit + Gitleaks | SARIF reports |
| Test coverage | 85-99% (292 tests) | 85-99% | Codecov integration, 85% CI threshold |
| Infra testing (Terraform) | tfsec + checkov | tfsec + checkov | Hard gates + advisory |
| Infra testing (K8s) | kube-linter + conftest | kube-linter + conftest | OPA policies (13 rules) |

## Infrastructure Test Results

| Test | Type | GCP | AWS |
|------|------|-----|-----|
| `terraform fmt` | Hard gate | ✅ Pass | ✅ Pass |
| `terraform validate` | Hard gate | ✅ Pass | ✅ Pass |
| `tfsec` | Advisory | ✅ (51/71) | ✅ (84/116) |
| `checkov` | Advisory | ✅ (51/71) | ✅ (84/116) |
| YAML syntax | Hard gate | ✅ 24/24 | ✅ 24/24 |
| `kube-linter` | Advisory | ✅ 17 findings | ✅ 17 findings |
| `conftest` (OPA) | Hard gate | ✅ 0 violations | ✅ 0 violations |

> Run: `bash tests/infra/run_all_tests.sh`

## Model Performance (v3.0.0 — Python 3.11, sklearn 1.8.0)

| Model | Algorithm | Key Metric | Size |
|-------|-----------|------------|------|
| BankChurn | StackingClassifier (RF+GB+XGB+LGB→LR) | AUC 0.87, F1 0.62 | 4.1 MB |
| CarVision | LightGBM + FeatureEngineer (24 features) | R² 0.80, RMSE $6,744 | 5.7 MB |
| NLPInsight | FinBERT (ProsusAI) / TF-IDF+LogReg fallback | Acc 97%, F1-w 0.97 | 309 KB |

## Test Coverage (~92% overall, 292 tests)

| Project | Coverage | Tests | CI Threshold |
|---------|----------|-------|--------------|
| BankChurn | 90.0% | 198 | 85% |
| CarVision | 95.4% | 37 | 85% |
| NLPInsight | 99.6% | 57 | 85% |

## Key Metrics

### Single-Request Latency (via port-forward, includes ~70ms network overhead)

| Service | Latency | With SHAP | Model Size | Memory per Worker |
|---------|---------|-----------|------------|-------------------|
| BankChurn | ~271ms | ~517ms (`?explain=true`) | 1.2 MB | ~300Mi |
| CarVision | ~257ms | N/A | 8.5 MB | ~550Mi |
| NLPInsight | ~100ms | N/A | 316 KB | ~1.0 GB |

### Load Test Results (Locust, 10 users, 2min, via kubectl port-forward)

| Endpoint | p50 | p75 | p95 | p99 | Requests | Errors |
|----------|-----|-----|-----|-----|----------|--------|
| bankchurn:predict | 140ms | 140ms | 170ms | 220ms | 251 | 1 (0.4%) |
| carvision:predict | 88ms | 91ms | 96ms | 99ms | 233 | 0 |
| nlpinsight:predict | 83ms | 86ms | 87ms | 89ms | 237 | 0 |
| **Aggregated** | **89ms** | **120ms** | **130ms** | **140ms** | **985** | **1 (0.1%)** |

**SLA Compliance**: Error rate 0.1% < 1% ✅ · P95 130ms < 500ms ✅ · P99 140ms < 1000ms ✅

> **Note**: Port-forward adds ~70ms overhead per request and serializes TCP connections.
> The single error (`status 0`) was a port-forward connection drop, not an application error.
> Production latency behind an Ingress/LoadBalancer will be significantly better.

## Performance Optimizations Applied

### Root Causes Identified
1. **BankChurn SHAP per request**: Explainability computation (~700ms) ran on every `/predict` call
2. **Single uvicorn worker**: CPU-bound sklearn `predict()` blocked the event loop under concurrency
3. **e2-medium (1 shared vCPU)**: Burstable CPU with 7+ containers causes starvation under load
4. **kubectl port-forward**: Not designed for concurrent load testing (serializes TCP connections)
5. **CarVision dual-container pod**: Streamlit sidecar competes for CPU/RAM with the API

### Fixes Applied
- **BankChurn**: SHAP is now lazy — skipped by default on `/predict`, available via `?explain=true`
- **NLPInsight**: TF-IDF vectorizer cached at startup (computed once, reused)
- **All services**: Uvicorn workers increased from 1 → 2 (K8s manifests + Dockerfiles)
- **Memory limits**: CarVision API increased to 1536Mi to support 2 workers
- **CPU requests**: Normalized to 300m across all services

### Recommended (Not Yet Applied)
- **Terraform GCP**: Upgrade `e2-medium` → `e2-standard-2` (2 dedicated vCPU, 8GB) for ~$24/mo more
- **Terraform GCP**: Consider `min_node_count = 2` for better pod distribution
- **Load testing**: Use Ingress IP mode (`INGRESS_HOST=34.120.120.57 locust -f tests/load/locustfile.py`) for production-grade metrics
- **CarVision**: Consider separating Streamlit into its own Deployment

## Screenshots & GIFs

> Visual evidence is organized in `docs/media/`:

### Recommended Evidence (High Impact)

1. **GIF: Full prediction flow** — curl → API → JSON response for each service
2. **GIF: Auto-scaling under load** — HPA scaling pods up, then back down
3. **Screenshot: Grafana dashboard** — Real-time ML metrics during load test
4. **Screenshot: GitHub Actions** — Full green CI/CD pipeline
5. **Screenshot: `kubectl get all`** — All pods, services, HPAs running
6. **GIF: MLflow experiment comparison** — Comparing model runs side-by-side
7. **Screenshot: Codecov** — Coverage badges and sunburst chart
8. **Screenshot: Multi-cloud** — Side-by-side GKE vs EKS terminal

### Media Directory Structure

```
docs/media/
├── screenshots/
│   ├── gcp-console/          # GKE cluster, Artifact Registry
│   ├── aws-console/          # EKS cluster, ECR
│   ├── terminal/             # kubectl, pods, services
│   ├── apis/                 # FastAPI docs, predictions
│   ├── monitoring/           # Grafana, Prometheus, MLflow
│   └── cicd/                 # GitHub Actions, Codecov
└── gifs/
    ├── prediction-flow.gif   # API request → response
    ├── autoscaling.gif       # HPA in action
    └── multi-cloud.gif       # GCP vs AWS side-by-side
```

> **Tip**: 5-8 high-quality GIFs are more impactful than 50+ static screenshots.
> Record with [Kap](https://getkap.co/) or [peek](https://github.com/phw/peek), optimize with `gifsicle`.
>
> **Tip**: Use high-quality GIFs over static screenshots for maximum recruiter impact.

---

## Deployment Commands Reference

```bash
# GCP
gcloud container clusters get-credentials ml-portfolio-gke-production --region us-central1
kubectl get pods -n ml-portfolio

# AWS
aws eks update-kubeconfig --name ml-portfolio-eks-production --region us-east-1
kubectl get pods -n ml-portfolio

# Verify all services
for svc in bankchurn carvision nlpinsight; do
  echo "--- $svc ---"
  kubectl exec -n ml-portfolio deploy/$svc-deployment -- curl -sf http://localhost:8000/health
done
```

---

**Last Updated**: March 2026 (v3.2.0 — OpenTelemetry, strict CI, fairness audits, CHANGELOG)
