# Media Assets

Visual evidence of the ML-MLOps Portfolio deployed on GCP (GKE) and AWS (EKS).

[![YouTube Demo](https://img.shields.io/badge/YouTube-Watch%20Demo-red?style=for-the-badge&logo=youtube)](https://youtu.be/qmw9VlgUcn8)

## Directory Structure

```
media/
├── screenshots/
│   ├── gcp-console/     # 16 captures: GKE, Artifact Registry, GCS, IAM
│   ├── terminal/        # 8 captures: kubectl pods, services, top
│   ├── apis/            # 10 captures: FastAPI Swagger, predictions, SHAP
│   ├── monitoring/      # 8 captures: Grafana, Prometheus, MLflow
│   ├── cicd/            # 7 captures: GitHub Actions, Codecov
│   ├── terraform/       # 7 captures: plan, state, outputs
│   ├── dvc/             # 8 captures: init, push, pull, status
│   └── aws-*/           # ~82 captures: EKS, ECR, S3, ALB, RDS
├── gifs/                # 13 GIFs (5 GCP + 5 AWS + 3 multi-cloud)
└── videos/              # Source recordings (gitignored)
```

**Total**: 168+ screenshots, 13 GIFs, 1 YouTube video

## Critical Screenshots

| # | File | Description |
|---|------|-------------|
| 05 | `gcp-console/05-gke-workloads-running.png` | 6 pods running on GKE |
| 17 | `terminal/17-kubectl-pods-running.png` | CLI evidence of all services |
| 26 | `apis/26-bankchurn-prediccion-real.png` | Real ML prediction |
| 31 | `apis/31-tres-apis-pestanas.png` | 3 APIs simultaneously |
| 34 | `monitoring/34-grafana-dashboard.png` | Real-time monitoring |
| 46 | `cicd/46-workflow-completado.png` | CI/CD pipeline completed |

## Usage

```markdown
![GKE Workloads](media/screenshots/gcp-console/05-gke-workloads-running.png)
![Prediction Demo](media/gifs/01-demo-prediccion.gif)
```

---

*Last Updated: March 2026*
