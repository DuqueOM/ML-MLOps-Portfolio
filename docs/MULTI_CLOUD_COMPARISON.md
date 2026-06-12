<div class="portfolio-page" markdown="1">

# Multi-Cloud Deployment Comparison: GCP (GKE) vs AWS (EKS)

> Production metrics captured March 13, 2026. Both clouds running identical Kubernetes manifests via Kustomize overlays.
> Both clouds use nginx Ingress with real LoadBalancer (GCP: static IP, AWS: NLB).

## Architecture Overview

| Component | GCP | AWS |
|-----------|-----|-----|
| **Kubernetes** | GKE 1 node baseline, auto-scales to 5 (e2-medium) | EKS 1 node baseline, auto-scales to 5 (t3.small) |
| **Container Registry** | Artifact Registry | ECR |
| **Object Storage** | GCS | S3 |
| **IAM → Pods** | Workload Identity | IRSA |
| **Load Balancer** | nginx-ingress + GCE LB (static IP) | nginx-ingress + NLB (AWS Load Balancer Controller) |
| **Ingress Controller** | nginx-ingress | nginx-ingress (portable) |
| **Monitoring** | Prometheus + Grafana | Prometheus + Grafana |
| **ML Tracking** | MLflow | MLflow |
| **HPA** | CPU-based (3 services) | CPU-based (3 services) |
| **Drift Detection** | CronJob (daily, completing) | CronJob (daily, completing) |
| **Network Policies** | Applied | Applied |
| **PDB** | Applied | Applied |

> Both clouds: real LoadBalancer with nginx Ingress path routing. AWS NLB provisioned 2026-03-18 (IAM permission fix applied).

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

### Smoke Test — Idle Latencies (Locust, 6 users, 30s — 2026-03-18)

> Both tests run against real LoadBalancer IPs — GCP: `136.111.152.72`, AWS: NLB DNS (`k8s-ingressn-ingressn-6775b5d876-17e8cdb571a0f652.elb.us-east-1.amazonaws.com`).
> Same locustfile, same parameters. Results are directly comparable.

| Service | GCP p50 | GCP p95 | AWS p50 | AWS p95 | Delta p50 |
|---------|---------|---------|---------|---------|----------|
| BankChurn `/predict` | 200ms | 410ms | 110ms | 140ms | **-45%** |
| NLPInsight `/predict` | 78ms | 140ms | 100ms | 120ms | **+28%** |
| ChicagoTaxi `/demand` | 100ms | 400ms | 120ms | 230ms | **+20%** |

### Load Test (Locust, 50 users, 2 min — 2026-03-18)

| Service | GCP p50 | GCP p95 | GCP Errors | AWS p50 | AWS p95 | AWS Errors |
|---------|---------|---------|------------|---------|---------|------------|
| BankChurn `/predict` | 3100ms | 6500ms | 0% | 120ms | 200ms | 0% |
| NLPInsight `/predict` | 84ms | 570ms | 0% | 100ms | 180ms | 0% |
| ChicagoTaxi `/demand` | 110ms | 4900ms | 0% | 130ms | 210ms | 0% |

> **Key finding**: AWS EKS significantly outperforms GCP GKE under concurrent load. BankChurn 3100ms (GCP) vs 120ms (AWS) under 50 users suggests EC2 compute-optimized nodes handle StackingClassifier better than GKE e2-medium instances. NLPInsight and ChicagoTaxi are comparable on both clouds.

### Stress Test (Locust, 100 users, 2 min — 2026-03-18)

| Service | GCP p50 | GCP Errors | AWS p50 | AWS Errors |
|---------|---------|------------|---------|------------|
| BankChurn `/predict` | 8200ms | **0.02%** | 130ms | **0%** |
| NLPInsight `/predict` | 79ms | 0% | 100ms | 0% |
| ChicagoTaxi `/demand` | 100ms | 0% | 130ms | 0% |

> **Production readiness**: 0% failure rate on both clouds under 100 concurrent users (after async inference fix — [ADR-015](decisions/015-async-inference-threadpool.md)). Pre-fix BankChurn had 81% failure rate under the same load. See [full load test results](load-test-results.md).

### Why BankChurn is Faster on AWS

**Root cause**: BankChurn's `StackingClassifier` is CPU-bound (~100ms pure CPU per prediction). AWS `t3.medium` has better single-thread performance than GCP `e2-medium`:

| Factor | GCP `e2-medium` | AWS `t3.medium` | Impact |
|--------|-----------------|-----------------|--------|
| CPU | AMD EPYC Rome 2.2 GHz, **shared** | Intel Xeon Platinum 2.5-3.1 GHz, burstable | Critical |
| vCPU allocation | 2 shared (multi-tenant) | 2 burstable (better credits) | High |
| Cost | $24/mo | $30/mo | Minimal |

**Why NLPInsight/ChicagoTaxi don't improve**: They're I/O-bound or use lightweight models (~5ms CPU) — not CPU-saturated.

**Trade-off decision**: Accepted the performance difference ([ADR-016](decisions/016-gcp-aws-performance-parity.md)). Upgrading GCP to `c2-standard-4` (4 vCPU @ 3.8 GHz) would cost $145/mo (6x increase) for marginal portfolio value. Both clouds meet SLAs (<500ms idle, 0% errors under load).

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
|:---:|:---:|:---:|
| ![Side-by-Side](media/screenshots/aws-terminal/36-multicloud-side-by-side.png) | ![EKS](media/screenshots/aws-console/30-eks-workloads-running.png) | ![SHAP](media/screenshots/aws-terminal/35-bankchurn-prediction-elb.png) |

| GKE Workloads | EKS Cluster | kubectl Pods (EKS) |
|:---:|:---:|:---:|
| ![GKE](media/screenshots/gcp-console/05-gke-workloads-running.png) | ![EKS Cluster](media/screenshots/aws-console/29-eks-cluster-overview.png) | ![EKS Pods](media/screenshots/aws-terminal/33-kubectl-pods-eks.png) |

| ECR Repositories | S3 Buckets | Artifact Registry |
|:---:|:---:|:---:|
| ![ECR](media/screenshots/aws-console/31-ecr-repositories.png) | ![S3](media/screenshots/aws-console/32-s3-buckets-models.png) | ![AR](media/screenshots/gcp-console/09-artifact-registry-imagenes.png) |

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

## Managed ML Platforms: Custom vs Managed

In addition to custom FastAPI on K8s, the portfolio deploys BankChurn on both SageMaker (AWS) and Vertex AI (GCP) managed endpoints to demonstrate multi-paradigm serving.

| Dimension | Custom FastAPI (K8s) | AWS SageMaker | GCP Vertex AI |
|-----------|---------------------|---------------|---------------|
| **Deployed in portfolio** | ✅ GKE + EKS | ✅ BankChurn endpoint | ✅ BankChurn endpoint |
| **Deploy time** | ~15 min (CI/CD) | ~5 min | ~5 min |
| **Latency p50** | ~103ms | ~150-200ms | ~150-200ms (est.) |
| **SHAP support** | ✅ `?explain=true` | ❌ | ❌ |
| **Custom metrics** | ✅ Prometheus | ❌ CloudWatch only | ❌ Cloud Monitoring only |
| **Multi-cloud** | ✅ Kustomize overlays | ❌ AWS-only | ❌ GCP-only |
| **Auto-scaling** | HPA (CPU target) | Built-in (invocations) | Built-in (CPU/GPU) |
| **Vendor lock-in** | Low | High | High |

> **Decision**: Custom FastAPI is primary (SHAP, Prometheus, multi-cloud). SageMaker + Vertex AI are complementary (demonstrates managed platform skills on both clouds). See [ADR-017](decisions/017-custom-vs-managed-ml-platforms.md) and [Managed ML Guide](MANAGED_ML_GUIDE.md).

## Deployment Commands

```bash
# GCP — Kubernetes
kubectl config use-context gke_ml-portfolio-duque-om-202602_us-central1_ml-portfolio-gke-production
kubectl apply -k k8s/overlays/gcp/

# AWS — Kubernetes
AWS_PROFILE=ml-portfolio kubectl apply -k k8s/overlays/aws/

# AWS — SageMaker Endpoint (on-demand, delete after demo)
python scripts/sagemaker/deploy_endpoint.py          # Deploy + test
python scripts/sagemaker/deploy_endpoint.py delete    # Stop charges

# GCP — Vertex AI Endpoint (on-demand, delete after demo)
python scripts/vertex_ai/deploy_endpoint.py           # Deploy + test
python scripts/vertex_ai/deploy_endpoint.py delete     # Stop charges
```

</div>
