# Media Assets

Visual evidence of the ML-MLOps Portfolio deployed on **GCP (GKE)** and **AWS (EKS)** — multi-cloud production.

## Directory Structure

```
media/
├── screenshots/
│   ├── gcp-console/     # GKE cluster, workloads, Artifact Registry, GCS, Cloud Build, IAM
│   ├── aws-console/     # EKS cluster, workloads, ECR repos, S3 buckets
│   ├── aws-terminal/    # kubectl on EKS, health checks via ALB, multi-cloud side-by-side
│   ├── terminal/        # kubectl on GKE, terraform outputs, health checks, infra tests
│   ├── apis/            # FastAPI Swagger UIs, ML predictions, SHAP
│   ├── monitoring/      # Grafana dashboards, Prometheus, MLflow experiments
│   ├── cicd/            # GitHub Actions, Codecov, secrets
│   └── terraform/       # Multi-cloud IaC structure, AWS validation, K8s overlays
├── gifs/                # Animated demos extracted from portfolio video
├── thumbnails/          # Video thumbnail for YouTube
└── video/               # Portfolio demo video
```

## Key Screenshots

| # | File | Description |
|---|------|-------------|
| 36 | `aws-terminal/36-multicloud-side-by-side.png` | **HERO**: GKE vs EKS side-by-side |
| 05 | `gcp-console/05-gke-workloads-running.png` | 6 workloads running on GKE |
| 29 | `aws-console/29-eks-cluster-overview.png` | EKS cluster Active (AWS equivalent) |
| 35 | `aws-terminal/35-bankchurn-prediction-elb.png` | SHAP prediction on EKS |
| 38 | `aws-terminal/38-drift-detection-output.png` | Drift detection CronJob output |
| 48 | `cicd/48-deploy-aws-workflow-success.png` | AWS deploy workflow SUCCESS |
| 26 | `apis/26-bankchurn-prediccion-real.png` | ML prediction with SHAP explainability |
| 34 | `monitoring/34-grafana-dashboard.png` | Grafana ML dashboard with load test metrics |
| 39 | `monitoring/39-mlflow-experiments.png` | MLflow: 3 experiments, 14 runs |
| 46 | `cicd/46-workflow-completado.png` | CI/CD pipeline: 10 jobs green |

## GIFs

All GIFs extracted from [Portfolio Demo Video](https://youtu.be/7dFFqq2ROPw) with optimized palettes.

| GIF | Size | Duration | Content | Source Segment |
|-----|------|----------|---------|----------------|
| `portfolio-demo.gif` | 3.5MB | 10s, 800×450 | Hero overview | 0:00–1:20 |
| `ml-predictions.gif` | 1.9MB | 8s, 800×450 | SHAP + Sentiment + Demand | 0:11–0:46 |
| `monitoring-observability.gif` | 3.2MB | 8s, 800×450 | Grafana + Prometheus + Locust | 1:02–1:20 |
| `multicloud-parity.gif` | 1.5MB | 8s, 800×450 | GKE vs EKS side-by-side | 1:37–1:55 |

> All GIFs rendered at 800×450 native resolution for crisp quality. Display size controlled via `<img width="...">` in docs.

## Usage

```markdown
![GKE Workloads](media/screenshots/gcp-console/05-gke-workloads-running.png)
![Portfolio Demo](media/gifs/portfolio-demo.gif)
![ML Predictions](media/gifs/ml-predictions.gif)
![Multi-Cloud](media/screenshots/aws-terminal/36-multicloud-side-by-side.png)
```

---

*Last Updated: March 2026 — v3.5.3*
