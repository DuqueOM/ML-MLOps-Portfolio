# Multi-Cloud Deployment Evidence

> Production deployment of 3 ML services on **Google Cloud Platform (GKE)** and **Amazon Web Services (EKS)**.
> All data below is from **live verification** on 2026-03-03 (v3.3.1).

---

## Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│  GCP (us-central1)                  │  AWS (us-east-1)             │
│                                     │                              │
│  GKE Cluster (7 nodes)              │  EKS Cluster (t3.large)      │
│  v1.34.3-gke.1318000                │  Terraform-managed           │
│                                     │                              │
│  ┌─── ML Services (HPA) ────────┐   │  ┌─── ML Services (HPA) ──┐  │
│  │ ┌──────────┐ ┌──────────┐    │   │  │ ┌────────┐ ┌────────┐  │  │
│  │ │BankChurn │ │CarVision │    │   │  │ │BankCh. │ │CarVis. │  │  │
│  │ │ API:8000 │ │ API:8000 │    │   │  │ │  :8000 │ │  :8000 │  │  │
│  │ └──────────┘ └──────────┘    │   │  │ └────────┘ └────────┘  │  │
│  │ ┌──────────┐ ┌──────────┐    │   │  │ ┌────────┐ ┌────────┐  │  │
│  │ │NLPInsight│ │CarVision │    │   │  │ │NLPIns. │ │CarVis. │  │  │
│  │ │ API:8000 │ │Dash:8501 │    │   │  │ │  :8000 │ │D.:8501 │  │  │
│  │ └──────────┘ └──────────┘    │   │  │ └────────┘ └────────┘  │  │
│  └──────────────────────────────┘   │  └────────────────────────┘  │
│                                     │                              │
│  ┌─── Observability Stack ──────┐   │  ┌─── Observability ──────┐  │
│  │ ┌──────────┐ ┌──────────┐    │   │  │ ┌────────┐ ┌────────┐  │  │
│  │ │Prometheus│ │ Grafana  │    │   │  │ │Prometh.│ │Grafana │  │  │
│  │ │  :9090   │ │  :3000   │    │   │  │ │  :9090 │ │  :3000 │  │  │
│  │ └──────────┘ └──────────┘    │   │  │ └────────┘ └────────┘  │  │
│  │ ┌──────────┐                 │   │  │ ┌────────┐             │  │
│  │ │  MLflow  │                 │   │  │ │ MLflow │             │  │
│  │ │  :5000   │                 │   │  │ │  :5000 │             │  │
│  │ └──────────┘                 │   │  │ └────────┘             │  │
│  └──────────────────────────────┘   │  └────────────────────────┘  │
│                                     │                              │
│  GCE Ingress (34.120.120.57)        │  ALB (DNS)                   │
│  Artifact Registry + GCS            │  ECR + S3                    │
│  Cloud SQL (PostgreSQL)             │  RDS (PostgreSQL)            │
│  Terraform IaC                      │  Terraform IaC               │
└────────────────────────────────────────────────────────────────────┘

8 pods total: 3 ML APIs + Streamlit Dashboard + Prometheus + Grafana + MLflow.
CarVision dashboard is a separate K8s pod (multi-target Dockerfile:
--target api | --target dashboard). Separate pods allow independent
scaling, health checks, and resource limits.
```

## Verified Capabilities

| Capability | GCP | AWS | Evidence |
|------------|-----|-----|----------|
| Container orchestration (K8s) | GKE v1.34.3 | EKS | 7 nodes, 8 pods running (incl. Streamlit dashboard) |
| Auto-scaling (HPA) | CPU-based | CPU-based | Verified: 1→3 pods under load, scale-down after |
| Model serving (FastAPI) | 3 services | 3 services | `/health` + `/predict` — 27/27 smoke tests passed |
| Batch prediction | All 3 APIs | All 3 APIs | `/predict_batch` endpoints verified |
| Monitoring (Prometheus) | 16/16 targets UP | Custom metrics | `bankchurn_*`, `carvision_*`, `nlpinsight_*` + 16 alert rules |
| Dashboards (Grafana) | v10.2.2, 2 dashboards | ML Performance | Latency, throughput, error rates, predictions, resource usage |
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

### Unit Test Coverage (368 total tests, 0 failures)

| Project | Tests | Passed | Skipped | Coverage | CI Threshold |
|---------|-------|--------|---------|----------|--------------|
| BankChurn | 199 | 198 | 1 | **90.03%** | 79% |
| CarVision | 52 | 52 | 0 | **95.72%** | 80% |
| NLPInsight | 74 | 73+1 xpassed | 0 | **98.41%** | 60% |
| Adversarial | 43 | 43 | 0 | — | — |
| **Total** | **368** | **367+1 xpassed** | **1** | **~93%** | — |

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
| CarVision API | `carvision-market-intelligence:v3.3.0` | **518 MB** | from 1.76 GB (-71%) |
| CarVision Dashboard | `carvision-dashboard:latest` | **950 MB** | Multi-target Dockerfile |
| NLPInsight | `nlpinsight-analyzer:v3.3.0` | **1.4 GB** | from 2.05 GB (-32%) |

> Optimizations: `--no-compile`, aggressive cleanup (`__pycache__`, `tests/`, `pip/setuptools`), NLPInsight `torch/test` removal.
> CarVision uses multi-target Dockerfile: `docker build --target api` (518 MB) or `--target dashboard` (950 MB).

## Load Test Results (Locust, via kubectl port-forward, 2026-03-03)

### Standard Load (10 users, 2 minutes)

| Endpoint | p50 | p75 | p95 | p99 | Requests | Errors | RPS |
|----------|-----|-----|-----|-----|----------|--------|-----|
| bankchurn:predict | 170ms | 190ms | 350ms | 450ms | 260 | 0 | 2.2 |
| bankchurn:health | 64ms | 69ms | 560ms | 640ms | 37 | 0 | 0.3 |
| carvision:predict | 91ms | 98ms | 130ms | 300ms | 265 | 0 | 2.2 |
| carvision:predict_batch | 92ms | 97ms | 140ms | 240ms | 45 | 0 | 0.4 |
| nlpinsight:predict | 180ms | 270ms | 450ms | 2400ms | 184 | 0 | 1.5 |
| nlpinsight:predict_batch | 530ms | 670ms | 850ms | 2300ms | 67 | 0 | 0.6 |
| **Aggregated** | **160ms** | **190ms** | **480ms** | **820ms** | **973** | **0 (0%)** | **8.1** |

**SLA Compliance**: Error rate 0.0% < 1% ✅ · P95 480ms < 500ms ✅ · P99 820ms < 1000ms ✅

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
| bankchurn-predictor | Running 1/1 | 10m | 348Mi | xrch |
| carvision-intelligence | Running 1/1 | 10m | 294Mi | mf2h |
| carvision-dashboard | Running 1/1 | — | ~512Mi | 6ls9 |
| nlpinsight-analyzer | Running 1/1 | 9m | 927Mi | lqbl |
| prometheus | Running 1/1 | 3m | 29Mi | t8v4 |
| grafana | Running 1/1 | 3m | 76Mi | lqbl |
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

### Prometheus Monitoring (16/16 targets UP, 0 DOWN)

| Target | Status | Metrics |
|--------|--------|--------|
| bankchurn-predictor | **UP** | `bankchurn_requests_total`, `_duration_seconds`, `_predictions_total{risk_level}` |
| carvision-intelligence | **UP** | `carvision_requests_total`, `_duration_seconds`, `_predictions_total` |
| nlpinsight-analyzer | **UP** | `nlpinsight_requests_total`, `_duration_seconds`, `_predictions_total{sentiment}` |
| prometheus (self) | **UP** | `prometheus_tsdb_*`, `process_*` |
| kubernetes-apiservers | **UP** | K8s API server metrics |
| kubernetes-pods (10) | **UP** | Auto-discovered via annotations |

> MLflow is intentionally NOT scraped (no `/metrics` endpoint). Health monitored via K8s liveness probes.
> Node-exporter removed (not deployed; unnecessary for portfolio-scale cluster).

### Alert Rules (16 rules loaded, all healthy)

| Group | Rules | Examples |
|-------|-------|----------|
| `ml_services_alerts` | 11 | `HighErrorRate` (>5% 5xx), `*HighLatency` (P95 >2s), `ServiceDown`, `*HighMemory` |
| `ml_model_alerts` | 3 | `*PredictionRateDrop` (<50% of normal rate for 10m) |
| `infrastructure_alerts` | 2 | `ScrapeTargetDown` (5m), `PrometheusStorageHigh` (>2GB TSDB) |

All rules use **real metrics** from deployed APIs (`process_resident_memory_bytes`, per-service `*_requests_total`).
No rules reference non-existent metrics (kube-state-metrics, cAdvisor, model_drift_score).

### Grafana (2 Dashboards, all panels functional)

| Property | Value |
|----------|-------|
| Version | 10.2.2 |
| Database | OK |
| Datasource | Prometheus (`http://prometheus-service:9090`) |
| Dashboard 1 | **ML Performance** — request rate, P95 latency, predictions, avg latency, error rate (6 panels) |
| Dashboard 2 | **ML Portfolio Production** — service health, request rate, latency, predictions/hr, error gauges, CPU, memory (19 panels) |

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

**Last Updated**: 2026-03-03 (v3.3.1 — Observability fixes: 16/16 Prometheus targets UP, 16 alert rules, 2 Grafana dashboards with all panels functional, cleaned scrape config)
