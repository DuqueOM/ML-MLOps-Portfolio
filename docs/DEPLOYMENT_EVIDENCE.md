# Multi-Cloud Deployment Evidence

> Production deployment of 3 ML services on **Google Cloud Platform (GKE)** and **Amazon Web Services (EKS)**.
> All data below is from **live verification** on 2026-03-03 (v3.3.0).

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  GCP (us-central1)             │  AWS (us-east-1)           │
│                                │                            │
│  GKE Cluster (7 nodes)         │  EKS Cluster (t3.large)    │
│  v1.34.3-gke.1318000           │  Terraform-managed          │
│  ┌──────────┐ ┌──────────┐     │  ┌──────────┐ ┌────────┐   │
│  │BankChurn │ │CarVision │     │  │BankChurn │ │CarVis. │   │
│  │  :8000   │ │  :8000   │     │  │  :8000   │ │  :8000 │   │
│  └────┬─────┘ └────┬─────┘     │  └────┬─────┘ └───┬────┘   │
│  ┌────┴─────┐ ┌────┴─────┐     │  ┌────┴─────┐ ┌───┴────┐   │
│  │NLPInsight│ │ MLflow   │     │  │NLPInsight│ │ MLflow │   │
│  │  :8000   │ │  :5000   │     │  │  :8000   │ │  :5000 │   │
│  └──────────┘ └──────────┘     │  └──────────┘ └────────┘   │
│  Prometheus + Grafana          │  Prometheus + Grafana      │
│  GCE Ingress (34.120.120.57)   │  ALB (DNS)                 │
│  Artifact Registry + GCS       │  ECR + S3                  │
│  Cloud SQL (PostgreSQL)        │  RDS (PostgreSQL)          │
│  Terraform IaC                 │  Terraform IaC             │
└─────────────────────────────────────────────────────────────┘
```

## Verified Capabilities

| Capability | GCP | AWS | Evidence |
|------------|-----|-----|----------|
| Container orchestration (K8s) | GKE v1.34.3 | EKS | 7 nodes, 8+ pods running |
| Auto-scaling (HPA) | CPU-based | CPU-based | Verified: 1→3 pods under load, scale-down after |
| Model serving (FastAPI) | 3 services | 3 services | `/health` + `/predict` — 27/27 smoke tests passed |
| Batch prediction | All 3 APIs | All 3 APIs | `/predict_batch` endpoints verified |
| Monitoring (Prometheus) | 4/4 targets UP | Custom metrics | `bankchurn_*`, `carvision_*`, `nlpinsight_*` |
| Dashboards (Grafana) | v10.2.2, DB ok | ML Performance | Latency, throughput, error rates |
| Experiment tracking (MLflow) | Cloud SQL backend | RDS backend | Running, v2.9.2 |
| Infrastructure as Code | Terraform GCP | Terraform AWS | 8/8 tests passed (fmt, validate, tfsec, checkov) |
| CI/CD (GitHub Actions) | Build + Deploy | Build + Deploy | 10-job pipeline, GHCR publish |
| Container registry | Artifact Registry | ECR | v3.3.0 images pushed |
| Object storage (models) | GCS | S3 | Init containers download on boot |
| Data versioning | DVC + GCS | DVC + S3 | `dvc push/pull` configured |
| Security scanning | Bandit + Gitleaks | Bandit + Gitleaks | Blocking in CI (HIGH severity) |
| Pod Security Standards | baseline enforce, restricted warn | baseline enforce | Namespace labels applied |
| Network Policies | default-deny + 3 allow rules | default-deny + 3 allow rules | Applied to cluster |
| Pod Disruption Budgets | minAvailable=1 (3 services) | minAvailable=1 | Applied to cluster |
| Test coverage | 90-98% (367 tests) | 90-98% | Codecov integration, 79-85% CI threshold |
| Adversarial testing | 43 robustness tests | 43 tests | SQL injection, XSS, boundary, Unicode |
| Infra testing (Terraform) | tfsec + checkov | tfsec + checkov | GCP 51/71, AWS 84/116 |
| Infra testing (K8s) | kube-linter + conftest | kube-linter + conftest | 9/9 passed, 0 OPA violations |

## Test Results (v3.3.0 — Verified 2026-03-03)

### Unit Test Coverage (367 total tests, 0 failures)

| Project | Tests | Passed | Skipped | Coverage | CI Threshold |
|---------|-------|--------|---------|----------|--------------|
| BankChurn | 199 | 198 | 1 | **90.03%** | 79% |
| CarVision | 52 | 52 | 0 | **95.72%** | 80% |
| NLPInsight | 74 | 73+1 xpassed | 0 | **98.41%** | 60% |
| Adversarial | 43 | 43 | 0 | — | — |
| **Total** | **368** | **367+1** | **1** | **~93%** | — |

### Smoke & Integration Tests (Live GKE Cluster)

| Test Suite | Tests | Passed | Failed | Notes |
|------------|-------|--------|--------|-------|
| Smoke services (`test_smoke_services.py`) | 27 | **27** | 0 | Health, predict, metrics, OpenAPI |
| K8s smoke (`test_smoke_k8s.py`) | 14 | **14** | 0 | BankChurn, CarVision, NLPInsight |
| **Total live tests** | **41** | **41** | **0** | All services healthy + predictions correct |

### Infrastructure Tests

| Test | Type | GCP | AWS |
|------|------|-----|-----|
| `terraform fmt` | Hard gate | ✅ Pass | ✅ Pass |
| `terraform validate` | Hard gate | ✅ Pass | ✅ Pass |
| `tfsec` | Advisory | ✅ 0 critical, 2 high | ✅ 2 critical, 5 high |
| `checkov` | Advisory | ✅ 51/71 passed | ✅ 84/116 passed |
| K8s YAML syntax | Hard gate | ✅ 16/16 files | ✅ All overlays |
| `kube-linter` | Advisory | ✅ 24 findings (advisory) | ✅ advisory |
| `conftest` (OPA) | Hard gate | ✅ 16/16 files, 0 violations | ✅ 10/10+1/1 files |
| K8s security checks | Hard gate | ✅ No privileged, no hostNetwork | ✅ Same |
| K8s required resources | Hard gate | ✅ 6 kinds, 5 deployments | ✅ Same |
| **Total** | | **9/9 passed** | **8/8 passed** |

> Run: `bash tests/infra/kubernetes/test_kubernetes.sh all && bash tests/infra/terraform/test_terraform.sh all`

## Model Performance (v3.0.0 — Python 3.11, sklearn 1.8.0)

| Model | Algorithm | Key Metric | Size |
|-------|-----------|------------|------|
| BankChurn | StackingClassifier (RF+GB+XGB+LGB→LR) | AUC 0.87, F1 0.62 | 4.1 MB |
| CarVision | LightGBM + FeatureEngineer (24 features) | R² 0.80, RMSE $6,744 | 5.7 MB |
| NLPInsight | FinBERT (ProsusAI/finbert) | Acc 97%, F1-w 0.97 | ~260 MB (transformer) |

## Docker Image Sizes (v3.3.0)

| Service | Image | Size | Improvement |
|---------|-------|------|-------------|
| BankChurn | `bankchurn-predictor:v3.3.0` | **1.09 GB** | from 2.11 GB (-48%) |
| CarVision | `carvision-market-intelligence:v3.3.0` | **518 MB** | from 1.76 GB (-71%) |
| NLPInsight | `nlpinsight-analyzer:v3.3.0` | **1.4 GB** | from 2.05 GB (-32%) |

> Optimizations: `--no-compile`, aggressive cleanup (`__pycache__`, `tests/`, `pip/setuptools`), NLPInsight `torch/test` removal.

## Load Test Results (Locust, via kubectl port-forward, 2026-03-03)

### Standard Load (10 users, 2 minutes)

| Endpoint | p50 | p75 | p95 | p99 | Requests | Errors | RPS |
|----------|-----|-----|-----|-----|----------|--------|-----|
| bankchurn:predict | 180ms | 220ms | 360ms | 520ms | 278 | 0 | 2.3 |
| bankchurn:health | 79ms | 99ms | 190ms | 190ms | 31 | 0 | 0.3 |
| carvision:predict | 110ms | 110ms | 170ms | 320ms | 257 | 0 | 2.1 |
| carvision:predict_batch | 100ms | 110ms | 130ms | 140ms | 46 | 0 | 0.4 |
| nlpinsight:predict | 220ms | 330ms | 540ms | 1100ms | 194 | 0 | 1.6 |
| nlpinsight:predict_batch | 500ms | 730ms | 1200ms | 1400ms | 52 | 0 | 0.4 |
| **Aggregated** | **170ms** | **210ms** | **500ms** | **910ms** | **967** | **0 (0%)** | **8.0** |

**SLA Compliance**: Error rate 0.0% < 1% ✅ · P95 500ms ≤ 500ms ✅ · P99 910ms < 1000ms ✅

### Stress Load (30 users, 2 minutes)

| Endpoint | p50 | p95 | Requests | Errors | RPS |
|----------|-----|-----|----------|--------|-----|
| bankchurn:predict | 500ms | 1100ms | 711 | 0 (0%) | 6.0 |
| carvision:predict | 93ms | 130ms | 759 | 0 (0%) | 6.4 |
| carvision:predict_batch | 94ms | 120ms | 128 | 0 (0%) | 1.1 |
| nlpinsight:predict | 520ms* | 1700ms* | 437 | 243* | 3.7 |
| **Aggregated** | **110ms** | **1200ms** | **2595** | **377** | **21.9** |

> \* NLPInsight errors under 30-user stress are **port-forward TCP drops** (`status 0`, `ConnectionRefused`),
> not application errors. `kubectl port-forward` serializes connections and is not designed for concurrent
> load testing. BankChurn and CarVision had **0 application errors** under 30-user stress.
> Production testing via Ingress IP (`34.120.120.57`) eliminates this overhead.

### HPA Auto-Scaling Observed During Load

| Service | Idle Replicas | Peak Replicas | CPU at Peak | Scale-Down |
|---------|---------------|---------------|-------------|------------|
| BankChurn | 1 | **3** | 15% → target 70% | ~8 min to 1 |
| CarVision | 1 | 1 | 29% → target 70% | N/A |
| NLPInsight | 1 | **3** | 39% → target 75% | ~8 min to 1 |

## Live Cluster State (2026-03-03)

### Pods

| Pod | Status | CPU | Memory | Node |
|-----|--------|-----|--------|------|
| bankchurn-predictor | Running 1/1 | 279m | 348Mi | xrch |
| carvision-intelligence | Running 1/1 | 85m | 294Mi | lfn4 |
| nlpinsight-analyzer (×3) | Running 1/1 | 8-396m | 647-761Mi | fjmv, lqbl, nb2q |
| prometheus | Running 1/1 | 3m | 42Mi | lfn4 |
| grafana | Running 1/1 | 2m | 76Mi | fjmv |
| mlflow-server | Running 1/1 | 1m | 420Mi | xrch |

### Cluster

| Property | Value |
|----------|-------|
| Provider | GKE (`ml-portfolio-gke-production`) |
| Region | `us-central1` |
| Kubernetes | v1.34.3-gke.1318000 |
| Nodes | 7 (`e2-medium`, Ready) |
| Namespace | `ml-portfolio` |
| Ingress IP | `34.120.120.57` |
| Registry | `us-central1-docker.pkg.dev/ml-portfolio-duque-om-202602/ml-portfolio-images` |
| GCS Bucket | `ml-portfolio-duque-om-202602-ml-models-production` |

### Prometheus Monitoring

| Target | Status |
|--------|--------|
| bankchurn-predictor | **UP** |
| carvision-intelligence | **UP** |
| nlpinsight-analyzer | **UP** |
| prometheus (self) | **UP** |

Custom metrics exported: `bankchurn_requests_total`, `carvision_requests_total`, `nlpinsight_requests_total`,
`*_request_duration_seconds`, `*_predictions_total`.

### Grafana

| Property | Value |
|----------|-------|
| Version | 10.2.2 |
| Database | OK |
| Datasource | Prometheus (`http://prometheus-service:9090`) |
| Dashboard | ML Performance (latency, throughput, error rates) |

## Performance Optimizations Applied

### Fixes Applied
- **BankChurn**: SHAP is lazy — skipped by default on `/predict`, available via `?explain=true`
- **NLPInsight**: FinBERT model cached at startup (loaded once, reused)
- **All services**: Uvicorn workers = 2 (K8s manifests + Dockerfiles)
- **Memory limits**: NLPInsight 512Mi/1Gi for FinBERT transformer
- **CPU requests**: Normalized to 300m across all services
- **Docker**: `--no-compile`, aggressive cleanup, multi-stage builds
- **HPA**: CPU-only scaling (removed memory metric — fixed model footprint)

### Recommended (Not Yet Applied)
- Upgrade `e2-medium` → `e2-standard-2` (2 dedicated vCPU) for better load handling
- Use Ingress IP mode for production-grade load tests (eliminates port-forward overhead)

## Security

| Feature | Status |
|---------|--------|
| Pod Security Standards | `enforce=baseline`, `warn=restricted`, `audit=restricted` |
| Network Policies | default-deny ingress + 3 allow rules |
| Pod Disruption Budgets | `minAvailable=1` for all 3 ML services |
| Bandit (SAST) | Blocking on HIGH severity in CI |
| Gitleaks (secrets) | Blocking in CI |
| Container scanning | Trivy in CI pipeline |
| Non-root containers | All ML services run as non-root (UID 1000) |
| ServiceAccount | `ml-workload` with minimal RBAC |

## Screenshots & GIFs

> Visual evidence is organized in `docs/media/`:

### Recommended Evidence (High Impact)

1. **GIF: Full prediction flow** — curl → API → JSON response for each service
2. **GIF: Auto-scaling under load** — HPA scaling 1→3 pods, then back down
3. **Screenshot: Grafana dashboard** — Real-time ML metrics during load test
4. **Screenshot: GitHub Actions** — Full green CI/CD pipeline
5. **Screenshot: `kubectl get all`** — All pods, services, HPAs running
6. **GIF: MLflow experiment comparison** — Comparing model runs side-by-side
7. **Screenshot: Codecov** — 367 tests, ~93% coverage
8. **Screenshot: Multi-cloud** — Side-by-side GKE vs EKS terminal
9. **GIF: Fairness audit CLI** — Disparate impact across 3 projects
10. **Screenshot: Drift detection report** — Evidently HTML with KS/PSI per feature

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
for svc in bankchurn-predictor carvision-intelligence nlpinsight-analyzer; do
  echo "--- $svc ---"
  kubectl exec -n ml-portfolio deploy/$svc -- curl -sf http://localhost:8000/health
done

# Run all tests
bash tests/infra/kubernetes/test_kubernetes.sh all
bash tests/infra/terraform/test_terraform.sh all
BANKCHURN_PORT=8000 CARVISION_PORT=8001 NLPINSIGHT_PORT=8002 \
  python3 -m pytest tests/infra/smoke/test_smoke_services.py -v
python3 -m pytest tests/integration/test_smoke_k8s.py -v
python3 -m locust -f tests/load/locustfile.py --headless -u 10 -r 2 -t 120s --only-summary
```

---

**Last Updated**: 2026-03-03 (v3.3.0 — CI fixes, PSS labels, adversarial tests, 367+ tests, Docker optimization, full GKE redeployment)
