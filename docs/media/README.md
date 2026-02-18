# Media Assets — GCP Production Deployment

Visual evidence of the ML-MLOps Portfolio running in production on Google Cloud Platform.

## 📺 Video Demo

[![YouTube Demo](https://img.shields.io/badge/YouTube-Watch%20Demo-red?style=for-the-badge&logo=youtube)](https://youtu.be/qmw9VlgUcn8)

**Full Portfolio Walkthrough**: [https://youtu.be/qmw9VlgUcn8](https://youtu.be/qmw9VlgUcn8)

---

## Directory Structure

```
media/
├── screenshots/
│   ├── gcp-console/               # GCP Console UI captures
│   │   ├── 01-project-dashboard.png
│   │   ├── 03-gke-clusters-lista.png
│   │   ├── 05-gke-workloads-running.png   ⭐ Critical
│   │   ├── 08-gke-ingress-ip.png
│   │   ├── 09-artifact-registry-imagenes.png
│   │   └── ...                    # 16 screenshots total
│   │
│   ├── terminal/                  # kubectl & CLI captures
│   │   ├── 17-kubectl-pods-running.png    ⭐ Critical
│   │   ├── 18-kubectl-services-ingress.png
│   │   ├── 23-health-checks-apis.png      ⭐ Critical
│   │   └── ...                    # 8 screenshots total
│   │
│   ├── apis/                      # FastAPI Swagger & predictions
│   │   ├── 25-fastapi-swagger-bankchurn.png
│   │   ├── 26-bankchurn-prediccion-real.png  ⭐ Critical
│   │   ├── 27-fastapi-swagger-carvision.png
│   │   ├── 29-fastapi-swagger-telecom.png
│   │   └── ...                    # 9 screenshots total
│   │
│   ├── monitoring/                # Grafana, Prometheus, MLflow
│   │   ├── 34-grafana-dashboard.png       ⭐ Critical
│   │   ├── 37-prometheus-targets-up.png   ⭐ Critical
│   │   ├── 39-mlflow-experiments.png
│   │   └── ...                    # 8 screenshots total
│   │
│   ├── cicd/                      # GitHub Actions pipeline
│   │   ├── 41-github-repositorio.png
│   │   ├── 46-workflow-completado.png     ⭐ Critical
│   │   └── ...                    # 7 screenshots total
│   │
│   └── terraform/                 # Infrastructure as Code
│       ├── 48-terraform-main-gke.png
│       ├── 51-terraform-state-list.png
│       ├── 53-terraform-plan-no-changes.png  ⭐ Critical
│       └── ...                    # 7 screenshots total
│
├── gifs/                          # Animated demonstrations
│   ├── 01-demo-prediccion.gif     # ⭐ BankChurn prediction demo
│   ├── 02-gke-workloads.gif       # GKE workloads in GCP Console
│   ├── 03-grafana-monitoring.gif  # Grafana dashboard navigation
│   ├── 04-cicd-pipeline.gif       # GitHub Actions pipeline run
│   └── 05-tres-apis-simultaneas.gif  # 3 APIs responding simultaneously
│
└── videos/                        # Source recordings (gitignored)
    ├── portfolio-demo.mp4         # Main demo (uploaded to YouTube)
    └── linkedin-clip.mp4          # 60-second LinkedIn version
```

---

## Screenshot Assets

### Critical Captures (8 must-have)

| # | Folder | File | Description |
|---|--------|------|-------------|
| 05 | `gcp-console/` | `05-gke-workloads-running.png` | 6 pods running — heart of the deployment |
| 17 | `terminal/` | `17-kubectl-pods-running.png` | CLI evidence of all services |
| 23 | `terminal/` | `23-health-checks-apis.png` | APIs responding with models loaded |
| 26 | `apis/` | `26-bankchurn-prediccion-real.png` | Real ML prediction in production |
| 34 | `monitoring/` | `34-grafana-dashboard.png` | Real-time monitoring dashboard |
| 37 | `monitoring/` | `37-prometheus-targets-up.png` | All monitoring targets active |
| 46 | `cicd/` | `46-workflow-completado.png` | CI/CD pipeline completed |
| 53 | `terraform/` | `53-terraform-plan-no-changes.png` | IaC perfectly synchronized |

### High Impact Captures (10 recommended)

| # | Folder | File | Description |
|---|--------|------|-------------|
| 01 | `gcp-console/` | `01-project-dashboard.png` | GCP project overview |
| 08 | `gcp-console/` | `08-gke-ingress-ip.png` | Public IP assigned by GCP |
| 09 | `gcp-console/` | `09-artifact-registry-imagenes.png` | 3 Docker images in registry |
| 13 | `gcp-console/` | `13-cloud-build-history.png` | Cloud Build runs |
| 25 | `apis/` | `25-fastapi-swagger-bankchurn.png` | Auto-generated API docs |
| 39 | `monitoring/` | `39-mlflow-experiments.png` | MLflow experiment tracking |
| 43 | `cicd/` | `43-github-secrets.png` | Secure CI/CD configuration |
| 48 | `terraform/` | `48-terraform-main-gke.png` | IaC code for GKE cluster |
| 51 | `terraform/` | `51-terraform-state-list.png` | All resources under Terraform |
| 52 | `terraform/` | `52-terraform-outputs.png` | Programmatic output values |

**Total**: 55 screenshots across 6 sessions + 5 GIFs + 1 video

---

## GIF Assets

| GIF | Description | Duration | Used In |
|-----|-------------|----------|---------|
| `01-demo-prediccion.gif` | BankChurn real prediction flow | ~15s | Main README, BankChurn README |
| `02-gke-workloads.gif` | GKE Console showing 6 workloads | ~10s | Main README |
| `03-grafana-monitoring.gif` | Grafana dashboard navigation | ~15s | Operations docs |
| `04-cicd-pipeline.gif` | GitHub Actions pipeline execution | ~12s | Architecture docs |
| `05-tres-apis-simultaneas.gif` | 3 APIs responding simultaneously | ~20s | Main README |

---

## Video Demo

The full portfolio demonstration is hosted on YouTube:

- **Title**: ML MLOps Portfolio — GCP Production Deployment (GKE + Terraform + CI/CD)
- **URL**: [https://youtu.be/qmw9VlgUcn8](https://youtu.be/qmw9VlgUcn8)
- **Duration**: ~4 minutes
- **Content**:
  1. Architecture overview
  2. GCP Console — 6 services running on GKE
  3. Terraform Infrastructure as Code
  4. 3 ML APIs with real predictions (BankChurn, CarVision, TelecomAI)
  5. Monitoring stack (Grafana + Prometheus + MLflow)
  6. CI/CD pipeline (GitHub Actions → GKE)

Source video files are in `videos/` (gitignored — too large for Git).

---

## GCP Deployment Details

| Component | Technology | Status |
|-----------|-----------|--------|
| **Cluster** | GKE (`ml-portfolio-gke-production`, us-central1) | ✅ Running |
| **Pods** | 6 services (3 ML APIs + MLflow + Prometheus + Grafana) | ✅ 6/6 Running |
| **Registry** | Artifact Registry (3 Docker images, versioned) | ✅ Ready |
| **Storage** | Cloud Storage (3 ML models: .pkl, .joblib) | ✅ Uploaded |
| **IaC** | Terraform (10+ resources, `No changes` plan) | ✅ Synchronized |
| **CI/CD** | GitHub Actions → Artifact Registry → GKE | ✅ Configured |
| **Ingress** | GCE Load Balancer (IP: 34.120.120.57) | ✅ Active |
| **Monitoring** | Prometheus scraping 3 APIs, Grafana dashboards | ✅ Active |

---

## Usage in Documentation

### Embedding Screenshots

```markdown
<!-- GCP workloads running -->
![GKE Workloads](media/screenshots/gcp-console/05-gke-workloads-running.png)

<!-- API prediction -->
![BankChurn Prediction](media/screenshots/apis/26-bankchurn-prediccion-real.png)

<!-- Monitoring -->
![Grafana Dashboard](media/screenshots/monitoring/34-grafana-dashboard.png)
```

### Embedding GIFs

```markdown
![Prediction Demo](media/gifs/01-demo-prediccion.gif)
```

### YouTube Video with Thumbnail

```markdown
[![Portfolio Demo](media/screenshots/gcp-console/05-gke-workloads-running.png)](https://youtu.be/qmw9VlgUcn8)
```
