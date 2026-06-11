---
trigger: glob
globs: ["**/*.tf", "**/*.tfvars"]
description: Terraform IaC patterns for multi-cloud ML infrastructure
---

# Terraform Rules

## Remote State (MANDATORY)

NEVER commit `terraform.tfstate` to the repository. Always use remote backends:

- **GCP**: `backend "gcs" { bucket = "...-terraform-state" }`
- **AWS**: `backend "s3" { bucket = "...-terraform-state", dynamodb_table = "...-lock" }`

## Secrets Management

- NEVER put secrets in `.tfvars` or committed files
- Use `google_secret_manager_secret` (GCP) or `aws_secretsmanager_secret` (AWS)
- Reference secrets via data sources or environment variables

## Variable Conventions

Every variable MUST have:
```hcl
variable "machine_type" {
  description = "GKE node pool machine type"
  type        = string
  default     = "e2-medium"
}
```

## Environment Separation

- `staging.tfvars` — smaller instances, preemptible/spot nodes, 1 replica
- `terraform.tfvars` (production) — on-demand nodes, autoscaling, HA configuration
- Same modules, different scale parameters

## File Organization

```
infra/terraform/
├── gcp/
│   ├── main.tf          # Provider, backend
│   ├── compute.tf       # GKE cluster, node pools
│   ├── storage.tf       # GCS buckets, Artifact Registry
│   ├── database.tf      # Cloud SQL
│   ├── network.tf       # VPC, subnets, firewall
│   ├── iam.tf           # Service accounts, Workload Identity
│   ├── secrets.tf       # Secret Manager
│   ├── outputs.tf       # Cluster endpoint, registry URL
│   ├── variables.tf     # All variables
│   ├── terraform.tfvars # Production values
│   └── staging.tfvars   # Staging values
└── aws/
    ├── main.tf          # Provider, backend
    ├── compute.tf       # EKS cluster, node groups
    ├── storage.tf       # S3 buckets, ECR
    ├── database.tf      # RDS PostgreSQL
    ├── network.tf       # VPC, subnets, security groups
    ├── iam.tf           # IRSA, OIDC provider
    ├── secrets.tf       # Secrets Manager
    ├── outputs.tf
    ├── variables.tf
    ├── terraform.tfvars
    └── staging.tfvars
```

## Security Baseline (NON-NEGOTIABLE)

- KMS encryption on all storage (S3: `aws:kms`, GCS: CMEK where applicable)
- Public access blocked on all buckets
- Access logging to dedicated bucket (not self-referential)
- Versioning enabled on data and model buckets
- IAM least privilege (read-only for serving, read-write for MLflow)
- Network policies in K8s
- Private nodes in GKE
- Database: SSL required, IAM auth enabled

## Security Scanning

- `tfsec` for static analysis of Terraform configurations
- `checkov` for compliance checks
- Both run in CI (`ci-infra.yml`) on every change to `infra/`

## Budget Alerts

Always include budget alerting:
```hcl
resource "google_billing_budget" "ml_budget" {
  amount { specified_amount { units = var.monthly_budget } }
  threshold_rules { threshold_percent = 0.5 }
  threshold_rules { threshold_percent = 0.9 }
}
```

## Lifecycle Rules

```hcl
lifecycle_rule {
  condition { age = var.archive_after_days }
  action    { type = "SetStorageClass", storage_class = "NEARLINE" }
}
lifecycle_rule {
  condition { age = var.delete_after_days }
  action    { type = "Delete" }
}
```
