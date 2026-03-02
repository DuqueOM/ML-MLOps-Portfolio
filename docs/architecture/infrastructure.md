# Infrastructure

Terraform-managed, multi-cloud (GCP + AWS) infrastructure for the ML-MLOps Portfolio.

## Cloud Resources

### GCP (Live Production)

| Resource | Configuration |
|----------|---------------|
| **GKE Cluster** | `ml-portfolio-gke-production`, us-central1, 3 nodes (e2-medium) |
| **Artifact Registry** | 3 Docker images (bankchurn, carvision, nlpinsight) |
| **Cloud Storage** | Models bucket + Datasets bucket (versioned, lifecycle policies) |
| **Cloud SQL** | PostgreSQL for MLflow backend |
| **VPC** | Custom network with private subnets, VPC peering for Cloud SQL |
| **Cost** | ~$51/month (covered by Free Tier credits) |

### AWS (EKS-ready)

| Resource | Configuration |
|----------|---------------|
| **EKS Cluster** | `ml-mlops-cluster`, us-east-1, 2-5 nodes (t3.medium) |
| **ECR** | 3 Docker images |
| **S3** | Artifacts + datasets (versioned) |
| **RDS** | PostgreSQL for MLflow |
| **Estimated Cost** | ~$170-260/month |

![GKE Workloads](../media/screenshots/gcp-console/05-gke-workloads-running.png)

## Kubernetes

| Manifest | Purpose |
|----------|---------|
| `k8s/*-deployment.yaml` | 3 ML APIs + MLflow + Prometheus + Grafana |
| `k8s/ingress.yaml` | External access with path-based routing |
| `k8s/model-configmaps.yaml` | GCS model/dataset paths for init containers |
| `k8s/overlays/aws/` | AWS-specific Kustomize overlays |

### Resource Calibration (2 uvicorn workers)

| Service | Memory (real/limit) | CPU Target | HPA |
|---------|-------------------|-----------|-----|
| BankChurn | ~300Mi / 1Gi | 70% | 1–3 pods |
| CarVision | ~550Mi / 1.5Gi | 70% | 1–3 pods |
| NLPInsight | ~140Mi / 768Mi | 75% | 1–3 pods |

> CPU-only HPA: ML models have fixed memory footprint. Memory-based scaling would never scale down.

## Terraform Commands

```bash
cd infra/terraform/gcp    # or aws/
terraform init
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

## Security

- Encryption at rest (GCS, Cloud SQL, S3, RDS)
- Workload Identity (GCP) / IRSA (AWS) for pod-level IAM
- Non-root containers (UID 1000)
- Private database networking
- CI/CD scanning: Trivy, Bandit, Gitleaks, pip-audit
- Least-privilege: `storage.objectViewer` for GKE pods

---

*Last Updated: March 2026*
