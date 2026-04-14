# Provider configuration and shared locals
# Resources split into domain-specific files:
#   versions.tf  — terraform block, required_providers, backend
#   network.tf   — VPC, subnets, private service connection
#   compute.tf   — GKE cluster, node pools
#   storage.tf   — GCS buckets (ml-models, mlflow-artifacts, audit-logs)
#   database.tf  — Cloud SQL PostgreSQL for MLflow
#   registry.tf  — Artifact Registry
#   iam.tf       — Service accounts, bucket-level IAM, Workload Identity
#   variables.tf — input variables
#   outputs.tf   — exported values

provider "google" {
  project = var.project_id
  region  = var.region
}

# Optional: Read db_password from Secret Manager instead of tfvars
# To use: Create secret with `gcloud secrets create mlflow-db-password --data-file=<(openssl rand -base64 24)`
# Then set var.db_password = "" in tfvars to trigger Secret Manager lookup
data "google_secret_manager_secret_version" "db_password" {
  count   = var.db_password == "" ? 1 : 0
  secret  = "mlflow-db-password"
  project = var.project_id
}

locals {
  # Use Secret Manager if db_password is empty, otherwise use tfvars value
  db_password_resolved = var.db_password != "" ? var.db_password : data.google_secret_manager_secret_version.db_password[0].secret_data
}
