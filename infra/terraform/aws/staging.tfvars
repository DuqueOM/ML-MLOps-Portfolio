# AWS Terraform Variables — Staging Environment
# Reduced resources for cost optimization
# Deploy: terraform apply -var-file=staging.tfvars

project_name = "ml-portfolio"
environment  = "staging"
aws_region   = "us-east-1"

# VPC networking (separate CIDR from production)
vpc_cidr             = "10.1.0.0/16"
private_subnet_cidrs = ["10.1.1.0/24", "10.1.2.0/24", "10.1.3.0/24"]
public_subnet_cidrs  = ["10.1.101.0/24", "10.1.102.0/24", "10.1.103.0/24"]

# Smaller instance for staging
node_instance_type = "t3.small"

# RDS database for MLflow
db_instance_class = "db.t3.micro"
db_username       = "mlflow"
db_password       = "CHANGE_ME_TO_A_SECURE_PASSWORD" # Use: openssl rand -base64 24

# Route 53 — Custom Domain (optional)
# Set enable_route53 = true and provide your domain to get clean URLs:
#   api.<domain_name>/bankchurn/docs
#   api.<domain_name>/nlpinsight/docs
#   api.<domain_name>/chicagotaxi/docs
enable_route53 = false
domain_name    = "" # e.g. "duqueom.dev"
