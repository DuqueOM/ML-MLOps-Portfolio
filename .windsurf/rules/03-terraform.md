---
trigger: glob
globs: "**/*.tf,**/*.tfvars"
---

# Terraform Conventions

## File Structure (split-file layout per cloud)
- versions.tf — terraform block, required_providers, backend config
- main.tf — provider config, secrets lookup (locals)
- variables.tf — all input variables with description + type
- network.tf — VPC, subnets, private service connection
- compute.tf — GKE/EKS cluster + node pool
- storage.tf — GCS/S3 buckets (models, datasets, mlflow)
- database.tf — Cloud SQL / RDS for MLflow
- registry.tf — Artifact Registry / ECR repositories
- iam.tf — service accounts, Workload Identity / IRSA bindings (GCP only)
- route53.tf — DNS + ACM certificate (AWS only)
- outputs.tf — all output values

## Variables
- ALL variables MUST have `description` and `type`
- Use compatible release pinning (~=) for provider versions
- Sensitive variables must be marked `sensitive = true`
- Default values only when there is a safe, obvious default

## Resource Tagging (required on all resources)
```hcl
labels = {
  project     = "ml-portfolio"
  environment = var.environment
  managed-by  = "terraform"
  service     = var.service_name
}
```

## State Management
- Remote state in GCS (GCP) or S3 (AWS) with state locking
- Never commit .tfstate files to Git
- Use workspaces or directory-based environments (dev/staging/prod)

## Security
- NEVER hardcode credentials, tokens, or secrets in .tf files
- Use Workload Identity (GCP) or IRSA (AWS) for service authentication
- Service accounts with minimal required permissions (least privilege)

## Workflow
1. `terraform fmt` before commit
2. `terraform validate` in CI
3. `terraform plan` reviewed before apply
4. `terraform apply` only from CI/CD or with explicit approval
