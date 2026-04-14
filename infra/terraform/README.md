# Terraform Infrastructure as Code

This directory contains Terraform configurations for deploying the ML Portfolio infrastructure on AWS and GCP.

## 📁 Structure

```
terraform/
├── aws/                          # AWS infrastructure (split-file layout)
│   ├── versions.tf              # Terraform block, providers, S3 backend
│   ├── main.tf                  # Provider config + Secrets Manager locals
│   ├── network.tf               # VPC, subnets, NAT, security groups
│   ├── compute.tf               # EKS cluster, node groups, CloudWatch
│   ├── storage.tf               # S3 buckets (ml-models, datasets, mlflow-artifacts)
│   ├── database.tf              # RDS PostgreSQL for MLflow
│   ├── registry.tf              # ECR repositories (3 services)
│   ├── route53.tf               # DNS + ACM TLS certificate
│   ├── variables.tf             # Input variables
│   ├── outputs.tf               # Exported values for CI/CD
│   ├── staging.tfvars           # Staging env values (no hardcoded secrets)
│   └── S3_ARTIFACTS_README.md   # Storage documentation
│
└── gcp/                          # GCP infrastructure (split-file layout)
    ├── versions.tf              # Terraform block, providers, GCS backend
    ├── main.tf                  # Provider config + Secret Manager locals
    ├── network.tf               # VPC, subnets, private service connection
    ├── compute.tf               # GKE cluster, node pools
    ├── storage.tf               # GCS buckets (ml-models, mlflow-artifacts, audit-logs)
    ├── database.tf              # Cloud SQL PostgreSQL for MLflow
    ├── registry.tf              # Artifact Registry
    ├── iam.tf                   # Service accounts, bucket-level IAM
    ├── variables.tf             # Input variables
    ├── outputs.tf               # Exported values
    ├── terraform.tfvars         # Production env values
    ├── staging.tfvars           # Staging env values
    └── README.md                # GCP-specific docs (secret rotation)
```

## 🚀 AWS Deployment

### Prerequisites

```bash
# Install Terraform
brew install terraform  # macOS
# or
sudo apt-get install terraform  # Linux

# Configure AWS credentials
aws configure
```

### Resources Created

- **EKS Cluster**: Managed Kubernetes cluster (v1.28)
- **VPC**: Networking with public/private subnets
- **S3 Buckets**: 3 buckets (ml-models, datasets, mlflow-artifacts) with:
  - `aws:kms` encryption, versioning, lifecycle (Glacier 90d, expire 365d)
  - Access logging, public access blocked
- **AWS Secrets Manager**: Database password lookup (parity with GCP)
- **RDS PostgreSQL**: Backend for MLflow (IAM auth enabled)
- **ECR Repositories**: 3 repos (bankchurn, nlpinsight, chicagotaxi) — IMMUTABLE tags + scan
- **ACM Certificate**: TLS for api.{domain} (when Route53 enabled)
- **CloudWatch**: Centralized logging (30d retention)

### Deploy

```bash
cd infra/terraform/aws

# Create terraform.tfvars
cat > terraform.tfvars <<EOF
project_name = "ml-portfolio"
environment  = "production"
aws_region   = "us-east-1"

db_username = "mlflow"
db_password = "" # Uses AWS Secrets Manager when empty
EOF

# Create secret in AWS Secrets Manager
aws secretsmanager create-secret \
  --name ml-portfolio-mlflow-db-password-production \
  --secret-string "$(openssl rand -base64 24)"

# Initialize Terraform
terraform init

# Review plan
terraform plan

# Apply changes
terraform apply
```

### Outputs

After successful deployment:

```bash
# Get cluster credentials
aws eks update-kubeconfig --name ml-portfolio-eks-production --region us-east-1

# Verify connection
kubectl get nodes
```

## ☁️ GCP Deployment

### Prerequisites

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth application-default login

# Set project
gcloud config set project YOUR_PROJECT_ID
```

### Resources Created

- **GKE Cluster**: Managed Kubernetes cluster (auto-upgrade enabled)
- **VPC & Subnets**: Networking with secondary ranges for pods/services
- **Cloud Storage**: 3 buckets (ml-models, mlflow-artifacts, audit-logs) with:
  - `public_access_prevention = enforced`, lifecycle (NEARLINE 90d, delete 365d)
  - Access logging to dedicated audit-logs bucket
- **GCP Secret Manager**: Database password lookup
- **Cloud SQL PostgreSQL**: Backend for MLflow (SSL required, audit flags enabled)
- **Artifact Registry**: Container image registry
- **Workload Identity**: Secure SA bindings
- **Bucket-level IAM**: Least-privilege (objectViewer for models, objectAdmin for mlflow only)

### Deploy

```bash
cd infra/terraform/gcp

# Create terraform.tfvars
cat > terraform.tfvars <<EOF
project_id   = "your-gcp-project-id"
project_name = "ml-portfolio"
environment  = "production"
region       = "us-central1"

db_password = "" # Uses GCP Secret Manager when empty
EOF

# Create secret in GCP Secret Manager
gcloud secrets create mlflow-db-password \
  --data-file=<(openssl rand -base64 24)

# Initialize Terraform
terraform init

# Review plan
terraform plan

# Apply changes
terraform apply
```

### Outputs

After successful deployment:

```bash
# Get cluster credentials
gcloud container clusters get-credentials ml-portfolio-gke-production --region us-central1

# Verify connection
kubectl get nodes
```

## 📊 Cost Estimation

### AWS (Actual Production — 2026-03-13)

| Resource | Type | Monthly Cost |
|----------|------|-------------|
| EKS Cluster | Control plane | $73 |
| EC2 Instances | 3× t3.small | ~$45 |
| S3 Storage | ~165MB | ~$0.05 |
| ECR | ~5GB images | ~$0.50 |
| Classic ELB | nginx-ingress | ~$5 |
| **Total** | | **~$124/month** |

### GCP (Actual Production — 2026-03-13)

| Resource | Type | Monthly Cost |
|----------|------|-------------|
| GKE Cluster | Management fee | $13.35 |
| Compute Engine | 4× e2-medium | ~$20.50 |
| Cloud SQL | db-f1-micro (MLflow) | ~$1.70 |
| Container Scanning | Artifact Registry | ~$9.10 |
| Networking | GCE LB + egress | ~$6.15 |
| **Total** | | **~$51/month** |

### Development Environment

For dev/staging, set `environment = "dev"` in `terraform.tfvars`:
- Uses smaller instance types
- Single NAT gateway (AWS)
- Preemptible VMs (GCP)
- **Estimated cost: ~$100-150/month**

## 🔒 Security Best Practices

### Secrets Management

Both clouds use managed secret stores — **never commit passwords to tfvars**:

```bash
# AWS: Secrets Manager (auto-lookup when db_password = "")
aws secretsmanager create-secret \
  --name ml-portfolio-mlflow-db-password-production \
  --secret-string "$(openssl rand -base64 24)"

# GCP: Secret Manager (auto-lookup when db_password = "")
gcloud secrets create mlflow-db-password \
  --data-file=<(openssl rand -base64 24)

# Fallback: environment variable
export TF_VAR_db_password="$(openssl rand -base64 24)"
```

### State Management

Both configurations use remote state storage:
- **AWS**: S3 + DynamoDB for locking
- **GCP**: Cloud Storage bucket

Create state backends before running terraform:

```bash
# AWS
aws s3api create-bucket \
  --bucket ml-portfolio-terraform-state \
  --region us-east-1

aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# GCP
gsutil mb -l us-central1 gs://ml-portfolio-terraform-state/
```

## � Infrastructure Testing

Automated validation and security scanning for all Terraform configurations.

```bash
# Run all Terraform tests (fmt, validate, tfsec, checkov)
bash tests/infra/terraform/test_terraform.sh all

# Run per provider
bash tests/infra/terraform/test_terraform.sh gcp
bash tests/infra/terraform/test_terraform.sh aws
```

| Test | Type | GCP | AWS |
|------|------|-----|-----|
| `terraform fmt` | Hard gate | ✅ | ✅ |
| `terraform validate` | Hard gate | ✅ | ✅ |
| `tfsec` | Advisory | ✅ (51/71) | ✅ (84/116) |
| `checkov` | Advisory | ✅ (51/71) | ✅ (84/116) |

CI: `.github/workflows/ci-infra.yml` runs on push to `main`/`develop` when `infra/` or `k8s/` files change.

See [tests/infra/README.md](../../tests/infra/README.md) for full details.

## �🧹 Cleanup

To destroy all infrastructure:

```bash
# AWS
cd infra/terraform/aws
terraform destroy

# GCP
cd infra/terraform/gcp
terraform destroy
```

## 🔄 DVC Integration

Training datasets are versioned with DVC, connected to both cloud storage backends:

```bash
# Pull data from AWS (default)
dvc pull data/raw/

# Switch to GCP
dvc remote default gcp-prod
dvc pull data/raw/
```

See `.dvc/config` for remote configuration.

## 📚 Additional Resources

- [Terraform AWS Provider Docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform GCP Provider Docs](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)
- [GKE Best Practices](https://cloud.google.com/kubernetes-engine/docs/best-practices)

## 🔧 Customization

### Change Instance Types

Edit `variables.tf` and set:

```hcl
# AWS
variable "eks_node_instance_type" {
  default = "t3.xlarge"  # More powerful
}

# GCP
variable "machine_type" {
  default = "e2-standard-8"  # More powerful
}
```

### Add More Services

Add to ECR/Artifact Registry in `main.tf`:

```hcl
resource "aws_ecr_repository" "new_service" {
  name = "${var.project_name}/new-service"
  # ... rest of config
}
```

## 📞 Support

For issues or questions:
- Check Terraform logs: `TF_LOG=DEBUG terraform apply`
- Validate syntax: `terraform validate`
- Format code: `terraform fmt -recursive`
