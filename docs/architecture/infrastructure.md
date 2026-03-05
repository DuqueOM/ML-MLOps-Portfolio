# Infrastructure

Terraform-managed, multi-cloud (GCP + AWS) infrastructure for the ML-MLOps Portfolio.

## Cloud Resources

### GCP (Live Production)

| Resource | Configuration |
|----------|---------------|
| **GKE Cluster** | `ml-portfolio-gke-production`, us-central1, 7 nodes (e2-medium) |
| **Artifact Registry** | 3 Docker images (bankchurn, nlpinsight, chicagotaxi) |
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
| `k8s/*-deployment.yaml` | 3 ML APIs + MLflow + Prometheus + Grafana (6 pods) |
| `k8s/ingress.yaml` | External access with path-based routing |
| `k8s/model-configmaps.yaml` | GCS model/dataset paths for init containers |
| `k8s/overlays/aws/` | AWS-specific Kustomize overlays |

### Resource Calibration (2 uvicorn workers)

| Service | Memory (real/limit) | CPU Target | HPA |
|---------|-------------------|-----------|-----|
| BankChurn | ~300Mi / 1Gi | 70% | 1–3 pods |
| NLPInsight | ~650Mi / 1Gi | 75% | 1–3 pods |
| ChicagoTaxi | ~150Mi / 512Mi | 70% | 1–3 pods |

> CPU-only HPA: ML models have fixed memory footprint. Memory-based scaling would never scale down.

## Terraform Commands

```bash
cd infra/terraform/gcp    # or aws/
terraform init
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

## Infrastructure Testing

Automated validation suite in `tests/infra/`:

| Test | Type | GCP | AWS |
|------|------|-----|-----|
| `terraform fmt` | Hard gate | ✅ | ✅ |
| `terraform validate` | Hard gate | ✅ | ✅ |
| `tfsec` | Advisory | ✅ (51/71) | ✅ (84/116) |
| `checkov` | Advisory | ✅ (51/71) | ✅ (84/116) |
| YAML syntax | Hard gate | ✅ 24/24 | ✅ 24/24 |
| `kube-linter` | Advisory | ✅ 17 findings | ✅ 17 findings |
| `conftest` (OPA) | Hard gate | ✅ 0 violations | ✅ 0 violations |

```bash
bash tests/infra/run_all_tests.sh
```

![Infrastructure Test Results](../media/screenshots/terminal/22b-infra-test-results.png)

## Security

- Encryption at rest (GCS, Cloud SQL, S3, RDS)
- Workload Identity (GCP) / IRSA (AWS) for pod-level IAM
- Non-root containers (UID 1000)
- Private database networking
- CI/CD scanning: Trivy, Bandit, Gitleaks, pip-audit
- Least-privilege: `storage.objectViewer` for GKE pods
- IaC scanning: tfsec, checkov (advisory findings documented in `.tfsec.yml`)

### Security Hardening (Terraform — Production-Grade)

The Terraform configuration includes **security hardening** that goes beyond what is applied to the running demo cluster:

| Feature | GCP (`main.tf`) | AWS (`main.tf`) |
|---------|-----------------|-----------------|
| Private cluster | `private_cluster_config` (private nodes, public endpoint) | `endpoint_private_access = true` |
| Authorized networks | `master_authorized_networks_config` (VPC CIDR only) | `endpoint_public_access_cidrs` |
| Network policy | Calico CNI | Calico CNI |
| VPC-native | `ip_allocation_policy` (secondary pod/service ranges) | VPC CNI (native) |
| Flow logs | VPC Flow Logs enabled | VPC Flow Logs enabled |
| Encryption | GCS/Cloud SQL at-rest | S3 KMS + public access blocks |

> **Architecture Decision**: The running GKE demo cluster was provisioned before the security hardening was added to the Terraform code. Applying these changes would **force cluster recreation** (`private_cluster_config` and `ip_allocation_policy` are ForceNew attributes in the GCP provider), destroying all 6 running pods and requiring full redeployment.
>
> Additionally, `master_authorized_networks_config` restricts API access to the VPC subnet (`10.10.0.0/24`), which would require a bastion host or Cloud Shell for kubectl access — appropriate for production but impractical for a portfolio demo that requires frequent local interaction.
>
> **The Terraform code represents the production-ready target state.** The running cluster demonstrates deployment capabilities (APIs, monitoring, autoscaling, CI/CD). Both are valid portfolio artifacts — the code shows security engineering, the cluster shows operational execution. A real production deployment would apply the hardened configuration from initial provisioning.

---

*Last Updated: March 2026 — v3.5.0*
