# Provider configuration and shared locals
# Resources split into domain-specific files:
#   versions.tf  — terraform block, required_providers, backend
#   network.tf   — VPC, subnets, NAT, security groups
#   compute.tf   — EKS cluster, node groups, CloudWatch
#   storage.tf   — S3 buckets (ml-models, datasets, mlflow-artifacts)
#   database.tf  — RDS PostgreSQL for MLflow
#   registry.tf  — ECR repositories
#   route53.tf   — DNS + ACM TLS certificate
#   variables.tf — input variables
#   outputs.tf   — exported values

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "ML-Portfolio"
      Owner       = "DuqueOM"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Optional: Read db_password from Secrets Manager instead of tfvars
# To use: aws secretsmanager create-secret --name ml-portfolio-mlflow-db-password-{env} --secret-string "$(openssl rand -base64 24)"
# Then set var.db_password = "" in tfvars to trigger Secrets Manager lookup
data "aws_secretsmanager_secret_version" "db_password" {
  count     = var.db_password == "" ? 1 : 0
  secret_id = "${var.project_name}-mlflow-db-password-${var.environment}"
}

locals {
  # Use Secrets Manager if db_password is empty, otherwise use tfvars value
  db_password_resolved = var.db_password != "" ? var.db_password : data.aws_secretsmanager_secret_version.db_password[0].secret_string
}
