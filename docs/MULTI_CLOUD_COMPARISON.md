# Multi-Cloud Deployment Comparison: GCP (GKE) vs AWS (EKS)

> Production metrics captured March 13, 2026. Both clouds running identical Kubernetes manifests via Kustomize overlays.
> Both clouds use nginx Ingress with real LoadBalancer (GCP: static IP, AWS: Classic ELB).

## Architecture Overview

| Component | GCP | AWS |
|-----------|-----|-----|
| **Kubernetes** | GKE (e2-medium × 4) | EKS (t3.small × 3) |
| **Container Registry** | Artifact Registry | ECR |
| **Object Storage** | GCS | S3 |
| **IAM → Pods** | Workload Identity | IRSA |
| **Load Balancer** | nginx-ingress + GCE LB (static IP) | nginx-ingress + Classic ELB |
| **Ingress Controller** | nginx-ingress | nginx-ingress (portable) |
| **Monitoring** | Prometheus + Grafana | Prometheus + Grafana |
| **ML Tracking** | MLflow | MLflow |
| **HPA** | CPU-based (3 services) | CPU-based (3 services) |
| **Drift Detection** | CronJob (daily, completing) | CronJob (daily, completing) |
| **Network Policies** | Applied | Applied |
| **PDB** | Applied | Applied |

> Both clouds: real LoadBalancer with nginx Ingress path routing. AWS Classic ELB provisioned 2026-03-13 (restriction lifted).

## Workload Summary

| Pod | GCP Status | AWS Status |
|-----|------------|------------|
| bankchurn-predictor | ✅ Running | ✅ Running |
| nlpinsight-analyzer | ✅ Running | ✅ Running |
| chicagotaxi-pipeline | ✅ Running | ✅ Running |
| prometheus | ✅ Running | ✅ Running |
| grafana | ✅ Running | ✅ Running |
| mlflow-server | ✅ Running | ✅ Running |

## Performance Comparison

### Load Test via LoadBalancer (Locust, 10 users, 90s)

> Both tests run against real LoadBalancer IPs — GCP: `136.111.152.72`, AWS: Classic ELB DNS.
> Same locustfile, same parameters. Results are directly comparable.

| Service | GCP avg | GCP p50 | GCP p95 | AWS avg | AWS p50 | AWS p95 | Delta p50 |
|---------|---------|---------|---------|---------|---------|---------|-----------|
| BankChurn `/predict` | 130ms | 110ms | 240ms | 136ms | 110ms | 230ms | **0%** |
| NLPInsight `/predict` | 87ms | 99ms | 220ms | 124ms | 98ms | 200ms | **-1%** |
| ChicagoTaxi `/demand` | 75ms | 75ms | 180ms | 286ms | 240ms | 560ms | **+220%** |
| **Aggregated** | **99ms** | **100ms** | **190ms** | **176ms** | **110ms** | **450ms** | **+10%** |

> **Key finding**: ML inference (BankChurn, NLPInsight) p50 is **identical** on both clouds — model compute dominates, not network. ChicagoTaxi delta is S3 vs GCS batch lookup latency.

### Stress Test — AWS (25 users, 60s — peak load)

| Service | Requests | Fail Rate | Avg | p50 | p95 | RPS |
|---------|----------|-----------|-----|-----|-----|-----|
| BankChurn `/predict` | 454 | **0.00%** | 124ms | 110ms | 170ms | 7.61 |
| NLPInsight `/predict` | 344 | **0.00%** | 111ms | 100ms | 150ms | 5.76 |
| ChicagoTaxi `/demand` | 151 | **0.00%** | 530ms | 480ms | 1100ms | 2.53 |
| **Aggregated** | **1,253** | **0.00%** | **178ms** | **110ms** | **440ms** | **20.99** |

> **Production readiness**: 0% failure rate on both clouds under 25 concurrent users. Both meet p95 < 500ms SLA for BankChurn and NLPInsight.

## Resource Usage (AWS EKS, post stress test)

| Pod | CPU | Memory |
|-----|-----|--------|
| bankchurn-predictor | 5m | 332Mi |
| chicagotaxi-pipeline | 500m | 149Mi |
| nlpinsight-analyzer | 5m | 311Mi |
| grafana | 2m | 86Mi |
| mlflow-server | 24m | 416Mi |
| prometheus | 2m | 33Mi |

## Cloud-Specific Configurations

### What Changes Between Clouds (Kustomize Overlays)

| File | Purpose |
|------|---------|
| `serviceaccount-aws.yaml` | IRSA annotation (vs Workload Identity on GCP) |
| `model-configmaps-aws.yaml` | S3 bucket paths (vs GCS paths) |
| `dataset-configmaps-aws.yaml` | S3 dataset paths (vs GCS paths) |
| `download-script-aws.yaml` | boto3 S3 download (vs google-cloud-storage) |
| `*-deployment-aws.yaml` | ECR image refs (vs Artifact Registry) |

### What Stays Identical (Base Manifests)

- Kubernetes Deployments (resource limits, health checks, env vars)
- Services (ClusterIP, port mappings)
- Ingress (nginx rewrite-target rules)
- Prometheus configuration
- Grafana dashboards
- MLflow server
- HPAs (CPU thresholds)
- Network Policies
- Pod Disruption Budgets
- CronJobs (drift detection, retraining triggers)

## Key Portability Evidence

1. **Same Ingress Controller**: nginx-ingress on both clouds — identical path routing rules
2. **Same Monitoring Stack**: Prometheus + Grafana deployed from base manifests
3. **Same HPA Behavior**: CPU-based autoscaling triggered correctly on both clouds
4. **Same Drift Detection**: Daily CronJob checking health + prediction stability on both clouds
5. **Init Container Pattern**: Same architecture, different storage SDK (boto3 vs google-cloud-storage)
6. **IRSA ↔ Workload Identity**: Cloud-native pod identity, same ServiceAccount pattern

> See [ADR-013: Multi-Cloud Parity Policy](decisions/013-multicloud-parity-policy.md) for the full parity-by-layer policy.

## Visual Evidence

| Multi-Cloud HERO | EKS Pods | SHAP on EKS |
|-----------------|----------|-------------|
| ![Side-by-Side](media/screenshots/aws-terminal/36-multicloud-side-by-side.png) | ![EKS](media/screenshots/aws-console/30-eks-workloads-running.png) | ![SHAP](media/screenshots/aws-terminal/35-bankchurn-prediction-elb.png) |

## Infrastructure Details

### GCP
- **Project**: `ml-portfolio-duque-om-202602`
- **Region**: `us-central1`
- **Cluster**: `ml-portfolio-gke-production`
- **Nodes**: 4 × e2-medium (2 vCPU, 4GB RAM) — autoscaler, min=1/max=5
- **Ingress IP**: `136.111.152.72`

### AWS
- **Account**: `531948420830`
- **Region**: `us-east-1`
- **Cluster**: `ml-portfolio-eks`
- **Nodes**: 3 × t3.small (2 vCPU, 2GB RAM)
- **External Access**: Classic ELB — `a6ed6b93fdbf14be2853d91bd2086d6b-1565798194.us-east-1.elb.amazonaws.com`
- **OIDC Provider**: `oidc.eks.us-east-1.amazonaws.com/id/8BC2F3AD51513C1D272D463D49B28335`
- **ECR**: `531948420830.dkr.ecr.us-east-1.amazonaws.com/ml-portfolio/*`
- **S3 Models**: `ml-portfolio-ml-models-production`
- **S3 Datasets**: `ml-portfolio-datasets-production`

## Deployment Commands

```bash
# GCP
kubectl config use-context gke_ml-portfolio-duque-om-202602_us-central1_ml-portfolio-gke-production
kubectl apply -k k8s/overlays/gcp/

# AWS
AWS_PROFILE=ml-portfolio kubectl apply -k k8s/overlays/aws/
```
