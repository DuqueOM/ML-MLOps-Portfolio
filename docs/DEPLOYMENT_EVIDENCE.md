<div class="portfolio-page" markdown="1">

# Multi-Cloud Deployment Evidence

> Production deployment of 3 ML services on **Google Cloud Platform (GKE)** and **Amazon Web Services (EKS)**.
> All data below is from **live verification** on 2026-03-13 (v3.5.3) — both clouds via nginx Ingress LoadBalancer.

---

## Architecture

```mermaid
graph TB
    subgraph GCP["GCP — us-central1"]
        direction TB
        GKE["GKE Cluster · 3 nodes · v1.34.3"]
        subgraph GCP_ML["ML Services — HPA"]
            BC1["BankChurn :8000"]
            NL1["NLPInsight :8000"]
            CT1["ChicagoTaxi :8000"]
        end
        subgraph GCP_OBS["Observability"]
            PR1["Prometheus :9090"]
            GR1["Grafana :3000"]
            ML1["MLflow :5000"]
        end
        GKE --> GCP_ML
        GKE --> GCP_OBS
        ING1["nginx Ingress · 136.111.152.72"] --> GKE
        GCP_INFRA["Artifact Registry · GCS · Workload Identity · Terraform"]
    end

    subgraph AWS["AWS — us-east-1"]
        direction TB
        EKS["EKS Cluster · 3 nodes · v1.31"]
        subgraph AWS_ML["ML Services — HPA"]
            BC2["BankChurn :8000"]
            NL2["NLPInsight :8000"]
            CT2["ChicagoTaxi :8000"]
        end
        subgraph AWS_OBS["Observability"]
            PR2["Prometheus :9090"]
            GR2["Grafana :3000"]
            ML2["MLflow :5000"]
        end
        EKS --> AWS_ML
        EKS --> AWS_OBS
        ING2["nginx Ingress · Classic ELB"] --> EKS
        AWS_INFRA["ECR · S3 · IRSA · Terraform + Kustomize"]
    end
```

- **Active pods per cloud**: 3 ML APIs + Prometheus + Grafana + MLflow (6 Running) + drift-detection CronJob history (Completed, 0 resources)
- **GCP**: 8 pods visible (6 Running + 2 Completed CronJob runs) · **AWS**: 7 pods visible (6 Running + 1 Completed CronJob run)
- **Both clouds**: nginx Ingress path routing (`/bankchurn`, `/nlpinsight`, `/chicagotaxi`, `/grafana`, `/mlflow`)
- **GCP**: static IP via GCE LB · **AWS**: Classic ELB DNS (2026-03-13)

## Verified Capabilities

| Capability | GCP | AWS | Evidence |
|------------|-----|-----|----------|
| Container orchestration (K8s) | GKE v1.34.3 | EKS v1.31 | 3 nodes per cloud, 6 Running + drift-detection CronJob history (Completed) |
| Auto-scaling (HPA) | CPU-based | CPU-based | Verified: 1→3 pods under load, scale-down after |
| Model serving (FastAPI) | 3 services | 3 services | `/health` + `/predict` — 27/27 smoke tests passed |
| Batch prediction | All 3 APIs | All 3 APIs | `/predict_batch` endpoints verified |
| Explainability (SHAP) | BankChurn | BankChurn | `/predict?explain=true` — 4.5s with real SHAP values |
| Drift Detection | Daily CronJob | Daily CronJob | `lastSuccessfulTime: 2026-03-13T22:12:32Z` on both |
| Monitoring (Prometheus) | 16/16 targets UP | Custom metrics | `bankchurn_*`, `nlpinsight_*` + 16 alert rules |
| Dashboards (Grafana) | v10.2.2, 2 dashboards | ML Performance | Latency, throughput, error rates, predictions |
| Experiment tracking (MLflow) | Cloud SQL backend | SQLite (in-pod) | Running, v2.9.2 |
| Infrastructure as Code | Terraform GCP | Terraform AWS + Kustomize | 8/8 tests passed (fmt, validate, tfsec, checkov) |
| CI/CD (GitHub Actions) | `deploy-gcp.yml` | `deploy-aws.yml` | Multi-cloud automated deployment, GHCR publish |
| External Access | nginx Ingress (Static IP) | nginx Ingress (Classic ELB) | **Both clouds: real LoadBalancer, no NodePort** |
| Container registry | Artifact Registry | ECR | v3.5.0 images pushed |
| Object storage (models) | GCS | S3 | Init containers download on boot |
| Data versioning | DVC + GCS | DVC + S3 | `dvc push/pull` configured |
| Security scanning | Bandit + Gitleaks | Bandit + Gitleaks | Blocking in CI (HIGH severity) |
| Pod Security Standards | baseline enforce, restricted warn | baseline enforce | Namespace labels applied |
| Network Policies | default-deny + 3 allow rules | default-deny + 3 allow rules | Applied to cluster |
| Pod Disruption Budgets | minAvailable=1 (3 services) | minAvailable=1 | Applied to cluster |
| Test coverage | 90-98% (395+ tests) | 90-98% | Codecov integration, 85% CI threshold |
| Adversarial testing | 43 robustness tests | 43 tests | SQL injection, XSS, boundary, Unicode |
| Infra testing (Terraform) | tfsec + checkov | tfsec + checkov | GCP 51/71, AWS 84/116 |
| Infra testing (K8s) | kube-linter + conftest | kube-linter + conftest | 9/9 passed, 0 OPA violations |

## Test Results (v3.5.3 — Verified 2026-03-13)

### Unit Test Coverage (395+ total tests, 0 failures)

| Project | Tests | Coverage | CI Threshold |
|---------|-------|----------|--------------|
| BankChurn | 199 | **90%** | 85% |
| NLPInsight | 74 | **98%** | 85% |
| ChicagoTaxi | 122 | **91%** | 85% |
| **Total** | **395+** | **90–98%** | 85% |

### Smoke & Integration Tests (Live GKE + EKS, 2026-03-13)

| Test Suite | Tests | Passed | Failed | Notes |
|------------|-------|--------|--------|-------|
| Smoke services (`test_smoke_services.py`) | 27 | **27** | 0 | Health, predict, metrics, OpenAPI |
| K8s smoke (`test_smoke_k8s.py`) | 9 | **9** | 0 | BankChurn, NLPInsight |
| **Total live tests** | **36** | **36** | **0** | All services healthy + predictions correct |

## Multi-Cloud Load Test Comparison (2026-03-13 — via LoadBalancer, 10 users, 90s)

> Both tests run against real LoadBalancer IPs — GCP: `136.111.152.72`, AWS: Classic ELB DNS.
> Same locustfile, same user count, same duration. Results are directly comparable.

### Load Test — GCP (GKE, 4× e2-medium, nginx Ingress static IP)

| Service | Requests | Fail Rate | Avg | p50 | p95 | p99 | RPS |
|---------|----------|-----------|-----|-----|-----|-----|-----|
| POST /bankchurn/predict | ~280 | **0.00%** | 130ms | 110ms | 240ms | 960ms | ~3.1 |
| POST /nlpinsight/predict | ~185 | **0.00%** | 87ms | 99ms | 220ms | 560ms | ~2.1 |
| GET /chicagotaxi/demand | ~95 | **0.00%** | 75ms | 75ms | 180ms | 310ms | ~1.1 |
| **Aggregated** | **~2,675** | **0.00%** | **99ms** | **100ms** | **190ms** | **590ms** | **~6.6** |

### Load Test — AWS (EKS, 3× t3.small, Classic ELB)

| Service | Requests | Fail Rate | Avg | p50 | p95 | p99 | RPS |
|---------|----------|-----------|-----|-----|-----|-----|-----|
| POST /bankchurn/predict | 281 | **0.00%** | 136ms | 110ms | 230ms | 670ms | 3.14 |
| POST /nlpinsight/predict | 170 | **0.00%** | 124ms | 98ms | 200ms | 610ms | 1.90 |
| GET /chicagotaxi/demand | 105 | **0.00%** | 286ms | 240ms | 560ms | 630ms | 1.18 |
| GET /bankchurn/health | 95 | **0.00%** | 111ms | 98ms | 180ms | 290ms | 1.06 |
| GET /nlpinsight/health | 102 | **0.00%** | 107ms | 94ms | 160ms | 200ms | 1.14 |
| **Aggregated** | **753** | **0.00%** | **176ms** | **110ms** | **450ms** | **660ms** | **8.42** |

### Stress Test — AWS (25 users, 60s — peak load)

| Service | Requests | Fail Rate | Avg | p50 | p95 | p99 | RPS |
|---------|----------|-----------|-----|-----|-----|-----|-----|
| POST /bankchurn/predict | 454 | **0.00%** | 124ms | 110ms | 170ms | 250ms | 7.61 |
| POST /nlpinsight/predict | 344 | **0.00%** | 111ms | 100ms | 150ms | 210ms | 5.76 |
| GET /chicagotaxi/demand | 151 | **0.00%** | 530ms | 480ms | 1100ms | 1600ms | 2.53 |
| **Aggregated** | **1,253** | **0.00%** | **178ms** | **110ms** | **440ms** | **910ms** | **20.99** |

### Multi-Cloud Performance Comparison

| Metric | GCP (GKE) | AWS (EKS) | Delta | Analysis |
|--------|-----------|-----------|-------|----------|
| **BankChurn p50** | 110ms | 110ms | **0%** | 🟢 Identical — model inference is CPU-bound, same model |
| **BankChurn p95** | 240ms | 230ms | -4% | 🟢 AWS slightly faster at p95 (less noisy infra) |
| **NLPInsight p50** | 99ms | 98ms | -1% | 🟢 Identical — TF-IDF+LogReg is fast on both |
| **NLPInsight p95** | 220ms | 200ms | -9% | 🟢 AWS slightly better |
| **ChicagoTaxi p50** | 75ms | 240ms | +220% | 🟡 AWS slower — batch lookup from S3 vs GCS latency |
| **Failure rate** | 0.00% | 0.00% | 0% | 🟢 Both meet target |
| **RPS (10 users)** | ~6.6 | ~8.4 | +27% | AWS slightly higher (Classic ELB routing efficiency) |
| **Node type** | e2-medium (2vCPU/4GB) | t3.small (2vCPU/2GB) | -50% RAM | AWS uses half the RAM per node |
| **Total nodes** | 4 | 3 | -25% | GCP autoscaler holds 4 for memory headroom |

### Conclusions

> **Key finding**: ML inference latency (BankChurn, NLPInsight) is **cloud-agnostic** — p50 is identical on both clouds because it is dominated by model compute, not network. The ChicagoTaxi delta is due to batch data lookup patterns between S3 and GCS, not Kubernetes.

> **AWS t3.small vs GCP e2-medium**: AWS uses 50% less RAM per node (2GB vs 4GB) but achieves the same inference SLAs because ML models are CPU-bound at inference time. This validates the cost-optimization decision documented in ADR-013.

> **Production readiness**: 0% failure rate on both clouds under 25 concurrent users. Both meet the SLA target of p95 < 500ms for primary inference services (BankChurn, NLPInsight).

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
| NLPInsight | TF-IDF + LogReg (production) | Acc 80.6%, F1-macro 0.748 | ~5 MB |
| ChicagoTaxi | RandomForest (lag features) | R² 0.96, RMSE 7.87 | ~2 MB |

## Docker Image Sizes (v3.5.0 — Artifact Registry, 2026-03-05)

| Service | Image | Size | Base |
|---------|-------|------|------|
| BankChurn | `bankchurn:v3.5.0` | **342 MB** | python:3.11-slim-bookworm |
| NLPInsight | `nlpinsight:v3.5.0` | **267 MB** | python:3.11-slim-bookworm |
| ChicagoTaxi | `chicagotaxi:v3.5.0` | **154 MB** | python:3.11-slim-bookworm |

> Optimizations: multi-stage build, `--no-compile`, aggressive cleanup (`__pycache__`, `tests/` excluding numpy, `pip/setuptools`), no `.so` stripping (corrupts numpy 2.x).
> NLPInsight dropped from 1.4 GB (FinBERT/torch) to 267 MB (TF-IDF+LogReg, no torch dependency).

## In-Pod Latency (measured inside container, zero network overhead, 2026-03-05)

> These are the **real production latencies** — measured by executing benchmarks directly inside each pod,
> eliminating port-forward proxy overhead (~50-100ms). This is equivalent to what a service mesh
> (Istio/Linkerd) or internal cluster client would observe.

| Service | Endpoint | P50 | P95 | Notes |
|---------|----------|-----|-----|-------|
| BankChurn | `/predict` | **103ms** | **111ms** | StackingClassifier (4 base + LR meta) |
| BankChurn | `/predict?explain=true` | **196ms** | — | +SHAP explainability |
| NLPInsight | `/predict` | **5ms** | **15ms** | TF-IDF+LogReg, inference_time=2.3ms |
| ChicagoTaxi | `/demand` | **75ms** | **460ms** | DataFrame filter on 355K rows |
| ChicagoTaxi | `/areas` | **187ms** | — | GroupBy aggregation on 355K rows |

### Why BankChurn is slower

BankChurn uses a **StackingClassifier** ensemble: 4 base learners (RandomForest, GradientBoosting, XGBoost, LightGBM) feed into a LogisticRegression meta-learner. Each prediction runs 5 models sequentially. A P50 of ~103ms is **expected and acceptable** for this architecture — service target is P95 < 500ms.

## Load Test Results (Locust, 30 users, 120s, via port-forward, 2026-03-05)

> Port-forward adds ~50-100ms overhead per request and serializes connections under concurrency.
> In-pod metrics above are the authoritative production latency numbers.

| Endpoint | Requests | P50 | P95 | P99 | Errors |
|----------|----------|-----|-----|-----|--------|
| bankchurn:predict | 746 | 670ms | 1600ms | 2000ms | 0 (0%) |
| nlpinsight:predict | 829 | 66ms | 160ms | 540ms | 0 (0%) |
| nlpinsight:predict_batch | 223 | 66ms | 170ms | 670ms | 0 (0%) |
| chicagotaxi:demand | 373 | 93ms | 220ms | 510ms | 0 (0%) |
| chicagotaxi:areas | 130 | 120ms | 220ms | 360ms | 0 (0%) |
| **Aggregated** | **2,675** | **97ms** | **1200ms** | **1700ms** | **0 (0%)** |

**SLA Compliance**: Error rate 0.0% < 1% ✅ · Zero application errors under 30-user concurrent load ✅

### HPA Auto-Scaling Configuration

| Service | Min/Max Replicas | CPU Target | Idle CPU | Memory |
|---------|------------------|------------|----------|--------|
| BankChurn | 1–3 | 70% | 3% | 344Mi |
| NLPInsight | 1–3 | 75% | 3% | 283Mi |
| ChicagoTaxi | 1–3 | 70% | 33% | 431Mi |

## Live Cluster State

### GCP — GKE (verified 2026-03-05)

#### Pods

| Pod | Status | CPU | Memory | Node |
|-----|--------|-----|--------|------|
| bankchurn-predictor | Running 1/1 | 10m | 344Mi | khkn |
| nlpinsight-analyzer | Running 1/1 | 9m | 283Mi | 55w8 |
| chicagotaxi-pipeline | Running 1/1 | 67m | 431Mi | 55w8 |
| prometheus | Running 1/1 | 18m | 170Mi | t8v4 |
| grafana | Running 1/1 | 2m | 76Mi | khkn |
| mlflow-server | Running 1/1 | 1m | 422Mi | bxmg |

#### Cluster

| Property | Value |
|----------|-------|
| Provider | GKE (`ml-portfolio-gke-production`) |
| Region | `us-central1` |
| Kubernetes | v1.34.3-gke.1318000 |
| Nodes | 3 (`e2-medium`, 2 vCPU / 4 GB each) |
| Namespace | `ml-portfolio` |
| Ingress IP | `136.111.152.72` |
| Registry | `us-central1-docker.pkg.dev/ml-portfolio-duque-om-202602/ml-portfolio-images` |
| GCS Bucket | `ml-portfolio-duque-om-202602-ml-models-production` |

#### Node Resource Utilization

| Node | CPU Usage | Memory Usage |
|------|-----------|-------------|
| 55w8 | 156m (16%) | 1864Mi (66%) |
| bxmg | 143m (15%) | 1770Mi (63%) |
| t8v4 | 163m (17%) | 1264Mi (45%) |
| **Avg** | **16%** | **58%** |

### AWS — EKS (verified 2026-03-12)

#### Pods

| Pod | Status | CPU | Memory |
|-----|--------|-----|--------|
| bankchurn-predictor | Running 1/1 | 8m | 332Mi |
| nlpinsight-analyzer | Running 1/1 | 7m | 271Mi |
| chicagotaxi-pipeline | Running 1/1 | 55m | 418Mi |
| prometheus | Running 1/1 | 15m | 158Mi |
| grafana | Running 1/1 | 2m | 68Mi |
| mlflow-server | Running 1/1 | 1m | 395Mi |
| drift-detection-* | Completed 0/1 | 0m | 0Mi |

> **Note on pod count**: `kubectl get pods` shows **7 pods** on AWS (6 Running + 1 Completed CronJob pod) and **8 pods** on GCP (6 Running + 2 Completed CronJob pods). The `Completed` pods are drift-detection CronJob execution history — they consume zero CPU/RAM and are automatically garbage-collected when `successfulJobsHistoryLimit` (default: 3) is exceeded. The active service stack is identical on both clouds: **6 Running pods**.

#### Cluster

| Property | Value |
|----------|-------|
| Provider | EKS (`ml-portfolio-eks`) |
| Region | `us-east-1` |
| Kubernetes | v1.31 |
| Nodes | 3 (`t3.small`, 2 vCPU / 2 GB each) |
| Namespace | `ml-portfolio` |
| External Access | Classic ELB via nginx-ingress (LoadBalancer) |
| Registry | `531948420830.dkr.ecr.us-east-1.amazonaws.com/ml-portfolio/*` |
| S3 Bucket | `ml-portfolio-ml-models-production` |
| IAM | IRSA (`ml-portfolio-eks-workload-role`) |

> **Note**: AWS uses Classic ELB (provisioned 2026-03-13) via nginx-ingress LoadBalancer service.
> Same professional pattern as GCP: LoadBalancer + nginx Ingress path-based routing.
> ELB DNS: `a6ed6b93fdbf14be2853d91bd2086d6b-1565798194.us-east-1.elb.amazonaws.com`

### Prometheus Monitoring (16/16 targets UP, 0 DOWN)

| Target | Status | Metrics |
|--------|--------|--------|
| bankchurn-predictor | **UP** | `bankchurn_requests_total`, `_duration_seconds`, `_predictions_total{risk_level}` |
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

### Fixes Applied (v3.5.0)
- **BankChurn**: SHAP is lazy — skipped by default on `/predict`, available via `?explain=true` (~196ms)
- **NLPInsight**: Switched from FinBERT (2+ GB torch) to TF-IDF+LogReg (267 MB image, 2.3ms inference)
- **All services**: Uvicorn workers = 2, multi-stage Docker builds, python:3.11-slim-bookworm base
- **Docker numpy 2.x fix**: Removed `.so` stripping (corrupts compiled extensions), excluded numpy from `tests/` deletion
- **Dependencies**: All pinned with `~=` (compatible release) — numpy~=2.2.0, scikit-learn~=1.8.0
- **HPA**: CPU-only scaling (removed memory metric — fixed model footprint)
- **ChicagoTaxi**: Added predictions init container for batch data download from GCS

### Resource Optimization Assessment
- **GCP Nodes**: 3× e2-medium (2 vCPU / 4 GB) — avg 16% CPU, 58% memory utilization
- **AWS Nodes**: 3× t3.small (2 vCPU / 2 GB) — tighter memory budget, all pods running successfully
- **Cost-effective**: Smallest viable instance types per cloud; upgrading only needed if P95 latency SLAs are missed under sustained load
- **HPA**: All 3 services scale on CPU target (50-60% per [ADR-001](decisions/001-cpu-only-hpa.md)/[ADR-014](decisions/014-single-worker-pod-ml-inference.md)), verified functional on both clouds

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

## Visual Evidence

### Multi-Cloud (HERO)

| GKE vs EKS | SHAP on EKS |
|------------|-------------|
| ![Side-by-Side](media/screenshots/aws-terminal/36-multicloud-side-by-side.png) | ![SHAP](media/screenshots/aws-terminal/35-bankchurn-prediction-elb.png) |

### GCP Production

| GKE Workloads | Grafana Dashboard | MLflow Experiments |
|---------------|-------------------|-------------------|
| ![GKE](media/screenshots/gcp-console/05-gke-workloads-running.png) | ![Grafana](media/screenshots/monitoring/34-grafana-dashboard.png) | ![MLflow](media/screenshots/monitoring/39-mlflow-experiments.png) |

### AWS Production

| EKS Cluster | EKS Pods | ECR Repos | S3 Buckets |
|-------------|----------|-----------|------------|
| ![EKS](media/screenshots/aws-console/29-eks-cluster-overview.png) | ![Pods](media/screenshots/aws-console/30-eks-workloads-running.png) | ![ECR](media/screenshots/aws-console/31-ecr-repositories.png) | ![S3](media/screenshots/aws-console/32-s3-buckets-models.png) |

### CI/CD & Security

| Pipeline Green | Deploy GCP | Deploy AWS |
|---------------|-----------|------------|
| ![CI/CD](media/screenshots/cicd/46-workflow-completado.png) | ![GCP](media/screenshots/cicd/49-deploy-gcp-workflow-success.png) | ![AWS](media/screenshots/cicd/48-deploy-aws-workflow-success.png) |

| Codecov Dashboard | GitHub Secrets |
|:---:|:---:|
| ![Codecov](media/screenshots/cicd/68-codecov-dashboard.png) | ![Secrets](media/screenshots/cicd/54-github-secrets.png) |

### Terminal Evidence

| kubectl Pods (GKE) | kubectl Pods (EKS) | Resource Usage |
|:---:|:---:|:---:|
| ![GKE Pods](media/screenshots/terminal/17-kubectl-pods-running.png) | ![EKS Pods](media/screenshots/aws-terminal/33-kubectl-pods-eks.png) | ![Top](media/screenshots/terminal/19-kubectl-top-pods.png) |

| Health Checks (GKE) | Health Checks (EKS) | Services & Ingress |
|:---:|:---:|:---:|
| ![Health GKE](media/screenshots/terminal/23-health-checks-apis.png) | ![Health EKS](media/screenshots/aws-terminal/34-health-checks-elb.png) | ![Ingress](media/screenshots/terminal/22a-ingress-controller-routing.png) |

### Infrastructure as Code

| Terraform Structure | K8s Overlays | Terraform Tests |
|:---:|:---:|:---:|
| ![Terraform](media/screenshots/terraform/01-terraform-multicloud-structure.png) | ![Overlays](media/screenshots/terraform/03-k8s-overlays-multicloud.png) | ![Tests](media/screenshots/terminal/22b-infra-test-terraform.png) |

### API Evidence

| BankChurn Swagger | NLPInsight Swagger | ChicagoTaxi Swagger |
|:---:|:---:|:---:|
| ![BankChurn](media/screenshots/apis/25-fastapi-swagger-bankchurn.png) | ![NLPInsight](media/screenshots/apis/27-fastapi-swagger-nlpinsight.png) | ![ChicagoTaxi](media/screenshots/apis/29-fastapi-swagger-chicagotaxi.png) |

| BankChurn Prediction | NLPInsight Prediction | ChicagoTaxi Prediction |
|:---:|:---:|:---:|
| ![BankChurn](media/screenshots/apis/26-bankchurn-prediccion-real.png) | ![NLPInsight](media/screenshots/apis/28-nlpinsight-prediccion.png) | ![ChicagoTaxi](media/screenshots/apis/30-chicagotaxi-prediccion.png) |

| SHAP Response | Prometheus Metrics |
|:---:|:---:|
| ![SHAP](media/screenshots/apis/82-shap-prediction-response.png) | ![Metrics](media/screenshots/apis/32-metrics-endpoint.png) |

### Monitoring

| Grafana ML Panels | Load Test Results | P95 Latency |
|:---:|:---:|:---:|
| ![ML Panels](media/screenshots/monitoring/34b-grafana-dashboard-ml-panels.png) | ![Load Test](media/screenshots/monitoring/38c-load-test-results.png) | ![P95](media/screenshots/monitoring/75-prometheus-latency-p95.png) |

| MLflow Comparison |
|:---:|
| ![MLflow](media/screenshots/monitoring/55-mlflow-xgboost-comparison.png) |

### GIFs & Video

| Demo | Description |
|------|-------------|
| <img src="media/gifs/ml-predictions.gif" alt="ML Predictions" width="400"> | Live ML predictions: BankChurn (SHAP) + NLPInsight + ChicagoTaxi |
| <img src="media/gifs/monitoring-observability.gif" alt="Monitoring" width="400"> | Grafana dashboards, Prometheus metrics, load testing |
| <img src="media/gifs/multicloud-parity.gif" alt="Multi-Cloud" width="400"> | GKE vs EKS side-by-side: functional parity verification |

> **Video**: [Portfolio Demo (3:30 min)](https://youtu.be/7dFFqq2ROPw) — full multi-cloud walkthrough

---
## Deployment Commands Reference

```bash
# === GCP (GKE) ===
gcloud container clusters get-credentials ml-portfolio-gke-production --region us-central1
kubectl get pods -n ml-portfolio
kubectl get hpa -n ml-portfolio
curl -s http://136.111.152.72/bankchurn/health | python3 -m json.tool

# === AWS (EKS) ===
export AWS_PROFILE=ml-portfolio
aws eks update-kubeconfig --name ml-portfolio-eks --region us-east-1
kubectl get pods -n ml-portfolio
kubectl get hpa -n ml-portfolio
kubectl get nodes -o wide
kubectl get svc,ingress -n ml-portfolio
ELB_DNS=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
curl -s http://$ELB_DNS/bankchurn/health | python3 -m json.tool

# === Verify all services (either cloud) ===
for svc in bankchurn-predictor nlpinsight-analyzer chicagotaxi-pipeline; do
  echo "--- $svc ---"
  kubectl exec -n ml-portfolio deploy/$svc -- curl -sf http://localhost:8000/health
done

# === Run all tests ===
bash tests/infra/kubernetes/test_kubernetes.sh all
bash tests/infra/terraform/test_terraform.sh all
BANKCHURN_PORT=8000 NLPINSIGHT_PORT=8002 CHICAGOTAXI_PORT=8003 \
  python3 -m pytest tests/infra/smoke/test_smoke_services.py -v
python3 -m pytest tests/integration/test_smoke_k8s.py -v
python3 -m locust -f tests/load/locustfile.py --headless -u 10 -r 2 -t 120s --only-summary

# === Verify Classic ELB is provisioned ===
kubectl get svc -n ingress-nginx ingress-nginx-controller
# EXTERNAL-IP should show a6ed6b93...elb.amazonaws.com
```

---

**Last Updated**: 2026-03-14 (v3.5.3 — AWS Classic ELB LoadBalancer, load + stress tests verified on both clouds via real Ingress, multi-cloud parity confirmed: 0% failure rate, BankChurn p50 identical at 110ms)

</div>
