# GCP Terraform Variables — Staging Environment
# Reduced resources and preemptible nodes for cost optimization
# Deploy: terraform apply -var-file=staging.tfvars

project_id     = "ml-portfolio-YOUR_ID"
project_name   = "ml-portfolio"
environment    = "staging"
region         = "us-central1"
machine_type   = "e2-small"
node_count     = 1
min_node_count = 1
max_node_count = 2
db_tier        = "db-f1-micro"
db_password    = ""  # Use Secret Manager: gcloud secrets create mlflow-db-password-staging
