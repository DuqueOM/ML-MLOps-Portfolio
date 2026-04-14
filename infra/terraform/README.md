# Terraform Infrastructure as Code — ML Portfolio

> **Summary**: IaC for the MLOps portfolio on AWS (EKS) and GCP (GKE).
> Terraform ≥ 1.5 | Remote state on both clouds | KMS + Secrets Manager | tfsec + checkov in CI.
>
> For the architectural decision to run GCP + AWS in parity, see [ADR-016](../../docs/decisions/016-gcp-aws-performance-parity.md).
> For the decision to use custom FastAPI + K8s over SageMaker/Vertex AI, see [ADR-017](../../docs/decisions/017-custom-vs-managed-ml-platforms.md).

---

## ⚡ Quick-Start — Day 1

```bash
# Step 1: Verify required versions
terraform version   # ≥ 1.5.0
aws --version       # ≥ 2.x (for AWS)
gcloud version      # ≥ 450.0 (for GCP)

# Step 2: Clone and navigate
git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git
cd ML-MLOps-Portfolio/infra/terraform

# Step 3: Create the state backend BEFORE terraform init
# AWS:
aws s3api create-bucket --bucket ml-portfolio-terraform-state --region us-east-1
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# GCP:
gsutil mb -l us-central1 gs://ml-portfolio-terraform-state/

# Step 4: Create secrets BEFORE terraform apply
aws secretsmanager create-secret \
  --name ml-portfolio-mlflow-db-password-production \
  --secret-string "$(openssl rand -base64 24)"

gcloud secrets create mlflow-db-password \
  --data-file=<(openssl rand -base64 24)

# Step 5: Deploy
cd aws && terraform init && terraform plan && terraform apply
cd ../gcp && terraform init && terraform plan && terraform apply
```

---

## 📋 Required Versions

| Tool | Minimum version | Notes |
|---|---|---|
| Terraform | ≥ 1.5.0 | `required_version = ">= 1.5.0"` in versions.tf |
| AWS Provider | ≥ 5.0 | hashicorp/aws |
| GCP Provider | ≥ 5.0 | hashicorp/google |
| AWS CLI | ≥ 2.x | For post-deploy commands |
| gcloud CLI | ≥ 450.0 | For GCP commands |
| kubectl | ≥ 1.28 | For post-deploy verification |

---

## 📁 Directory Structure

```
terraform/
├── aws/                          # AWS infrastructure
│   ├── versions.tf              # Terraform block, providers, S3 backend
│   ├── main.tf                  # Provider config + Secrets Manager locals
│   ├── network.tf               # VPC, subnets, NAT, security groups
│   ├── compute.tf               # EKS cluster (v1.28), node groups, CloudWatch
│   ├── storage.tf               # S3 buckets (ml-models, datasets, mlflow-artifacts)
│   ├── database.tf              # RDS PostgreSQL for MLflow (IAM auth)
│   ├── registry.tf              # ECR repos (3 services, immutable tags + scan)
│   ├── route53.tf               # DNS + ACM TLS certificate
│   ├── variables.tf
│   ├── outputs.tf               # Exported values for CI/CD and K8s overlays
│   ├── staging.tfvars
│   └── README.md                # AWS-specific docs (S3, IRSA, KMS)
│
└── gcp/                          # GCP infrastructure
    ├── versions.tf              # Terraform block, providers, GCS backend
    ├── main.tf                  # Provider config + Secret Manager locals
    ├── network.tf               # VPC, subnets, private service connection
    ├── compute.tf               # GKE cluster (auto-upgrade), node pools
    ├── storage.tf               # GCS buckets (ml-models, mlflow-artifacts, audit-logs)
    ├── database.tf              # Cloud SQL PostgreSQL for MLflow (SSL required)
    ├── registry.tf              # Artifact Registry
    ├── iam.tf                   # Service accounts, Workload Identity, bucket-level IAM
    ├── variables.tf
    ├── outputs.tf
    ├── terraform.tfvars
    ├── staging.tfvars
    └── README.md                # GCP-specific docs (secrets, Workload Identity, Vertex AI)
```

---

## 🚀 AWS Deployment

### Resources Created

| Resource | Configuration | Estimated cost/mo |
|---|---|---|
| EKS Cluster | v1.28, managed node groups | $73 (control plane) |
| EC2 Instances | 3× t3.small (node group) | ~$45 |
| RDS PostgreSQL | db.t3.micro, IAM auth, MLflow backend | ~$15 |
| S3 Buckets | 3 buckets, KMS encryption, versioning | ~$0.30 |
| ECR | 3 repos, immutable tags, image scanning | ~$0.50 |
| Classic ELB | nginx-ingress | ~$5 |
| Secrets Manager | mlflow-db-password | ~$0.40 |
| **Total production** | | **~$124/mo** |
| **Total staging** | Smaller instances | **~$60/mo** |

> Source: actual costs measured 2026-03-13. See [ADR-016](../../docs/decisions/016-gcp-aws-performance-parity.md) for the full cost/performance trade-off analysis between GCP and AWS.

### Deploy

```bash
cd infra/terraform/aws

# Create terraform.tfvars (gitignored)
cat > terraform.tfvars <<EOF
project_name = "ml-portfolio"
environment  = "production"
aws_region   = "us-east-1"
db_username  = "mlflow"
db_password  = ""  # Uses Secrets Manager when empty
EOF

terraform init
terraform plan
terraform apply

# Get cluster credentials
aws eks update-kubeconfig --name ml-portfolio-eks-production --region us-east-1
kubectl get nodes
```

### IRSA — IAM Roles for Service Accounts (EKS)

IRSA allows EKS pods to access AWS services (S3, Secrets Manager, ECR) using IAM identities without hardcoded credentials. It is the equivalent of Workload Identity in GCP.

```bash
# Verify IRSA is configured
kubectl describe serviceaccount ml-workload -n ml-portfolio | grep "Annotations"
# Expected output:
# Annotations: eks.amazonaws.com/role-arn: arn:aws:iam::{account}:role/ml-portfolio-ml-workload-production

# Verify pods can access S3
kubectl exec -it -n ml-portfolio deploy/bankchurn-predictor -- \
  aws s3 ls s3://ml-portfolio-ml-models-production/
# Should list models without credentials error

# The IAM role (created in compute.tf) has permissions:
# - s3:GetObject on ml-models bucket
# - s3:PutObject on mlflow-artifacts bucket
# - secretsmanager:GetSecretValue for mlflow-db-password
```

---

## ☁️ GCP Deployment

### Resources Created

| Resource | Configuration | Estimated cost/mo |
|---|---|---|
| GKE Cluster | Auto-upgrade, Workload Identity, network policy | $13.35 (management fee) |
| Compute Engine | 4× e2-medium (2 vCPU, 4GB RAM, shared) | ~$20.50 |
| Cloud SQL | db-f1-micro PostgreSQL 15, SSL, audit flags | ~$1.70 |
| Artifact Registry | Docker images, 3 repositories | ~$9.10 |
| GCS Buckets | ml-models, mlflow-artifacts, audit-logs | ~$0.30 |
| Networking | GCE LB + egress | ~$6.15 |
| **Total production** | | **~$51/mo** |
| **Total staging** | Preemptible VMs, smaller SQL | **~$25/mo** |

> Why e2-medium and not c2-standard-4: the portfolio prioritizes cost efficiency over maximum latency. A c2-standard-4 ($145/mo) would deliver <100ms on BankChurn, but the e2-medium ($24/mo) meets the <500ms idle SLA. Documented in [ADR-016](../../docs/decisions/016-gcp-aws-performance-parity.md).

### Deploy

```bash
cd infra/terraform/gcp

cat > terraform.tfvars <<EOF
project_id   = "your-gcp-project-id"
project_name = "ml-portfolio"
environment  = "production"
region       = "us-central1"
db_password  = ""  # Uses GCP Secret Manager when empty
EOF

terraform init
terraform plan
terraform apply

# Get cluster credentials
gcloud container clusters get-credentials ml-portfolio-gke-production --region us-central1
kubectl get nodes
```

---

## 🔗 Terraform → Kubernetes Connection

Terraform outputs feed directly into the Kubernetes overlays in `k8s/overlays/`. This section documents the complete flow.

### AWS (EKS → k8s/overlays/aws/)

```bash
# Get Terraform outputs
cd infra/terraform/aws
terraform output -json > /tmp/aws_outputs.json

# Most-used outputs by K8s:
terraform output eks_cluster_name        # → configmap: cluster-name
terraform output ecr_repositories        # → deployment: image URLs (map)
terraform output ml_models_bucket        # → deployment: env var MODEL_BUCKET
terraform output mlflow_db_endpoint      # → secret: DATABASE_URL for MLflow
terraform output ml_datasets_bucket      # → DVC remote: aws-prod

# The CI/CD script uses these outputs automatically:
# .github/workflows/deploy-model.yml
```

### GCP (GKE → k8s/overlays/gcp/)

```bash
cd infra/terraform/gcp
terraform output -json > /tmp/gcp_outputs.json

terraform output gke_cluster_name           # → kubectl config
terraform output artifact_registry_url     # → deployment: image URL
terraform output ml_models_bucket          # → deployment: env var MODEL_BUCKET
terraform output mlflow_db_connection_name # → secret: DATABASE_URL for MLflow
terraform output mlflow_artifacts_bucket   # → MLflow artifact store
```

### Coordinated Update Pattern

When you change infrastructure (for example, upgrading the Cloud SQL instance), the flow is:

1. Update `terraform/gcp/database.tf`
2. `terraform plan` → review changes
3. `terraform apply` → new endpoint in outputs
4. Update `k8s/overlays/gcp/configmap.yaml` with the new endpoint
5. `kubectl apply -k k8s/overlays/gcp/` → rolling restart picks up new config

---

## 🔒 Security and Secrets Management

### Never commit credentials in tfvars

```bash
# AWS: Secrets Manager (auto-lookup when db_password = "")
aws secretsmanager create-secret \
  --name ml-portfolio-mlflow-db-password-production \
  --secret-string "$(openssl rand -base64 24)"

# GCP: Secret Manager (auto-lookup when db_password = "")
gcloud secrets create mlflow-db-password \
  --data-file=<(openssl rand -base64 24)

# Alternative: environment variable (local dev)
export TF_VAR_db_password="$(openssl rand -base64 24)"
```

### Remote State

Create backends before `terraform init`:

```bash
# AWS backend
aws s3api create-bucket --bucket ml-portfolio-terraform-state --region us-east-1
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# GCP backend
gsutil mb -l us-central1 gs://ml-portfolio-terraform-state/
```

---

## 💰 Budget Alerts and Governance

Budget alerts are **not yet managed by Terraform** in this portfolio (Phase 8). Currently configured manually via console/CLI:

```bash
# GCP: Set up a budget alert via gcloud
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="ML Portfolio Monthly" \
  --budget-amount=100USD \
  --threshold-rule=percent=0.5 \
  --threshold-rule=percent=0.9 \
  --threshold-rule=percent=1.0,basis=FORECASTED_SPEND

# AWS: Set up a budget alert via CLI
aws budgets create-budget \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --budget '{
    "BudgetName": "ml-portfolio-monthly",
    "BudgetLimit": {"Amount": "150", "Unit": "USD"},
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST"
  }'
```

---

## 🧪 Infrastructure Testing

```bash
# Run all Terraform tests
bash tests/infra/terraform/test_terraform.sh all

# By provider
bash tests/infra/terraform/test_terraform.sh gcp
bash tests/infra/terraform/test_terraform.sh aws
```

| Test | Type | GCP | AWS | Description |
|---|---|:---:|:---:|---|
| `terraform fmt` | Hard gate | ✅ | ✅ | Consistent formatting |
| `terraform validate` | Hard gate | ✅ | ✅ | Valid syntax and references |
| `tfsec` | Advisory | ✅ 51/71 | ✅ 84/116 | IaC security |
| `checkov` | Advisory | ✅ 51/71 | ✅ 84/116 | Best practices |

**Accepted findings (risk-accepted):** Failed checks correspond mainly to: (a) CloudWatch log retention < 365 days (we use 30d for cost — accepted for portfolio), (b) RDS without Multi-AZ (cost — portfolio does not need database HA), (c) GKE without Binary Authorization (complexity — out of scope for 3 services). These findings are documented in `tests/infra/README.md`.

CI/CD: `.github/workflows/ci-infra.yml` runs on push to `main`/`develop` when `infra/` or `k8s/` changes.

---

## 🗺️ Related Architecture Decisions

| ADR | Decision | Impact on this infrastructure |
|---|---|---|
| [ADR-016](../../docs/decisions/016-gcp-aws-performance-parity.md) | Accept GCP vs AWS latency difference as a cost trade-off | Justifies e2-medium on GCP vs t3.medium on AWS |
| [ADR-017](../../docs/decisions/017-custom-vs-managed-ml-platforms.md) | Custom FastAPI + K8s as primary, SageMaker/Vertex AI as complement | Justifies GKE/EKS instead of pure Vertex AI/SageMaker endpoints |
| [ADR-001](../../docs/decisions/001-cpu-only-hpa.md) | CPU-only HPA | Implies node groups only need to scale on CPU, not memory |
| [ADR-006](../../docs/decisions/006-drift-triggered-retraining.md) | CronJob + GitHub Actions for retraining | K8s CronJob accesses GCS/S3 via Workload Identity/IRSA |

---

## 🔧 Troubleshooting

### Error: `Backend initialization required`
```bash
# Cause: The state bucket does not exist yet
# Fix: Create the bucket before terraform init
aws s3api create-bucket --bucket ml-portfolio-terraform-state --region us-east-1
terraform init
```

### Error: `Error reading Secret Manager secret`
```bash
# Cause: The secret does not exist or the SA lacks permissions
gcloud secrets list  # Verify it exists
gcloud secrets add-iam-policy-binding mlflow-db-password \
  --member="serviceAccount:terraform@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Error: `Workload Identity binding failed`
```bash
# Verify the K8s SA has the correct annotation
kubectl describe serviceaccount ml-workload -n ml-portfolio
# Must show: eks.amazonaws.com/role-arn or iam.gke.io/gcp-service-account

# Re-create the binding if needed
terraform taint google_service_account_iam_binding.workload_identity
terraform apply
```

### Error: `Terraform state lock`
```bash
# Cause: A previous apply failed and the lock was not released
# AWS:
aws dynamodb delete-item \
  --table-name terraform-state-lock \
  --key '{"LockID": {"S": "ml-portfolio-terraform-state/gcp/terraform.tfstate"}}'

# GCP (alternative):
terraform force-unlock LOCK_ID
```

### Error: `tfsec/checkov failing in CI`
```bash
# View the full tfsec report
tfsec infra/terraform/gcp --format markdown
tfsec infra/terraform/aws --format markdown

# Advisory checks do not block CI (only hard gates do)
# See tests/infra/README.md for the list of risk-accepted findings
```

---

## 🔄 DVC Integration

```bash
# Pull training data from AWS (default)
dvc pull data/raw/

# Push new data versions
dvc push

# Switch to the GCP remote
dvc remote default gcp-prod
dvc pull data/raw/
```

Config in `.dvc/config`. DVC buckets use the same IRSA/Workload Identity authentication as K8s pods.

---

## 🧹 Cleanup

```bash
# AWS
cd infra/terraform/aws
terraform destroy

# GCP
cd infra/terraform/gcp
terraform destroy

# IMPORTANT: Verify no orphaned resources remain
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State.Name]'
gcloud compute instances list --project=YOUR_PROJECT_ID
```

---

## 📚 References

- [AWS Terraform Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [GCP Terraform Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)
- [GKE Best Practices](https://cloud.google.com/kubernetes-engine/docs/best-practices)
- [IRSA Documentation](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html)
- [GKE Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)