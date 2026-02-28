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
│  │TelecomAI │ │ MLflow   │     │  │TelecomAI │ │ MLflow │   │
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
| Monitoring (Prometheus) | Custom metrics | Custom metrics | `bankchurn_*`, `carvision_*`, `telecom_*` |
| Dashboards (Grafana) | ML Performance | ML Performance | Latency, throughput, error rates |
| Experiment tracking (MLflow) | Cloud SQL backend | RDS backend | Hyperparameter comparison |
| Infrastructure as Code | Terraform GCP | Terraform AWS | `infra/terraform/{gcp,aws}/` |
| CI/CD (GitHub Actions) | Build + Deploy | Build + Deploy | 10-job pipeline, GHCR publish |
| Container registry | Artifact Registry | ECR | Multi-arch images |
| Object storage (models) | GCS | S3 | Init containers download on boot |
| Data versioning | DVC + GCS | DVC + S3 | `dvc push/pull` |
| Security scanning | Trivy + Bandit + Gitleaks | Trivy + Bandit + Gitleaks | SARIF reports |
| Test coverage | 88-95% | 88-95% | Codecov integration |

## Key Metrics

| Service | Avg Latency (p50) | Throughput | Model Size | Memory |
|---------|-------------------|------------|------------|--------|
| BankChurn | ~23ms | 40 req/s | 1.2 MB | ~300Mi |
| CarVision | ~45ms | 22 req/s | 8.5 MB | ~550Mi |
| TelecomAI | ~12ms | 65 req/s | 0.4 MB | ~140Mi |

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
for svc in bankchurn carvision telecom; do
  echo "--- $svc ---"
  kubectl exec -n ml-portfolio deploy/$svc-deployment -- curl -sf http://localhost:8000/health
done
```

---

**Last Updated**: February 2026
