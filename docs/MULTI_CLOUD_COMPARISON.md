# Multi-Cloud Deployment Comparison: GCP (GKE) vs AWS (EKS)

> Production metrics captured March 12, 2026. Both clouds running identical Kubernetes manifests via Kustomize overlays.

## Architecture Overview

| Component | GCP | AWS |
|-----------|-----|-----|
| **Kubernetes** | GKE (e2-medium × 3) | EKS (t3.small × 3) |
| **Container Registry** | Artifact Registry | ECR |
| **Object Storage** | GCS | S3 |
| **IAM → Pods** | Workload Identity | IRSA |
| **Load Balancer** | nginx-ingress + GCP LB | nginx-ingress + NodePort¹ |
| **Ingress Controller** | nginx-ingress | nginx-ingress (portable) |
| **Monitoring** | Prometheus + Grafana | Prometheus + Grafana |
| **ML Tracking** | MLflow | MLflow |
| **HPA** | CPU-based (3 services) | CPU-based (3 services) |
| **Network Policies** | Applied | Applied |
| **PDB** | Applied | Applied |

¹ AWS account-level restriction on `CreateLoadBalancer` API. AWS Load Balancer Controller installed and configured; external access via NodePort + Security Group rule.

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

### Sequential Load Test (50 requests per service)

| Service | GCP avg | GCP p95 | AWS avg | AWS p95 |
|---------|---------|---------|---------|---------|
| BankChurn `/predict` | 130ms | 240ms | 15ms | 16ms |
| NLPInsight `/predict` | 87ms | 220ms | 7ms | 8ms |
| ChicagoTaxi `/demand` | 103ms | 150ms | 196ms | 220ms |

> Note: GCP metrics measured via external LB (includes network hop); AWS metrics measured in-cluster (service-to-service). ChicagoTaxi higher on AWS due to t3.small memory constraints.

### Stress Test (10 concurrent users, 30 seconds)

| Metric | BankChurn | NLPInsight | ChicagoTaxi |
|--------|-----------|------------|-------------|
| **Total requests** | 598 | 598 | 598 |
| **Success rate** | 100% | 100% | 14.5%¹ |
| **Avg latency** | 16ms | 8ms | 2,967ms |
| **p50 latency** | 15ms | 8ms | 2,595ms |
| **p95 latency** | 18ms | 9ms | 6,820ms |
| **Max latency** | 114ms | 12ms | 7,697ms |
| **Throughput** | 19.9 RPS | 19.9 RPS | 2.8 RPS |

¹ ChicagoTaxi `/demand` returns large result sets (~50 records per request) and is CPU-bound on t3.small (2 vCPU). The HPA correctly detected CPU spike and scaled to 3 replicas.

### GCP Stress Test Results (Locust, 10 users, 30s — previous session)

| Metric | BankChurn | NLPInsight | ChicagoTaxi |
|--------|-----------|------------|-------------|
| **Failure rate** | 0% | 0% | 0% |
| **Avg latency** | 130ms | 87ms | 103ms |
| **p95 latency** | 240ms | 220ms | 150ms |
| **Throughput** | 6.58 RPS | 7.32 RPS | 7.05 RPS |

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
4. **Init Container Pattern**: Same architecture, different storage SDK (boto3 vs google-cloud-storage)
5. **IRSA ↔ Workload Identity**: Cloud-native pod identity, same ServiceAccount pattern

## Infrastructure Details

### GCP
- **Project**: `ml-portfolio-duque-om-202602`
- **Region**: `us-central1`
- **Cluster**: `ml-portfolio-gke-production`
- **Nodes**: 3 × e2-medium (2 vCPU, 4GB RAM)
- **Ingress IP**: `136.111.152.72`

### AWS
- **Account**: `531948420830`
- **Region**: `us-east-1`
- **Cluster**: `ml-portfolio-eks`
- **Nodes**: 3 × t3.small (2 vCPU, 2GB RAM)
- **External Access**: `54.166.200.233:31963` (NodePort)
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
