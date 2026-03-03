# ML Portfolio Helm Chart

Deploys the full ML/MLOps portfolio stack to Kubernetes.

## Components

- **BankChurn Predictor** — StackingClassifier ensemble (AUC 0.87)
- **CarVision Market Intelligence** — LightGBM regression (R² 0.80)
- **NLPInsight Analyzer** — FinBERT transformer (Acc 97%)
- **Drift Detection CronJob** — Daily PSI-based monitoring
- **HPA** — CPU-based autoscaling per service

## Quick Start

```bash
# Install
helm install ml-portfolio ./helm/ml-portfolio -n ml-portfolio --create-namespace

# Override values (e.g., for AWS)
helm install ml-portfolio ./helm/ml-portfolio -f helm/values-aws.yaml

# Upgrade
helm upgrade ml-portfolio ./helm/ml-portfolio

# Uninstall
helm uninstall ml-portfolio -n ml-portfolio
```

## Key Values

| Parameter | Default | Description |
|-----------|---------|-------------|
| `namespace` | `ml-portfolio` | K8s namespace |
| `registry.url` | GCP Artifact Registry | Container image registry |
| `modelStorage.bucket` | GCS bucket | Model storage bucket |
| `bankchurn.enabled` | `true` | Deploy BankChurn service |
| `carvision.enabled` | `true` | Deploy CarVision service |
| `nlpinsight.enabled` | `true` | Deploy NLPInsight service |
| `driftDetection.enabled` | `true` | Enable drift detection CronJob |
| `driftDetection.schedule` | `0 6 * * *` | Cron schedule (daily 6am UTC) |

## Architecture

All services use init containers to download models from GCS at pod startup.
HPA scales on CPU utilization (70% target). Memory is fixed (model footprint).
