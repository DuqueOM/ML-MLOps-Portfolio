# AWS Terraform Outputs
# These values are exported after terraform apply for use in CI/CD and documentation.
# Sensitive values are marked accordingly and won't appear in logs.

output "eks_cluster_endpoint" {
  description = "Endpoint for EKS cluster API server"
  value       = module.eks.cluster_endpoint
  sensitive   = true
}

output "eks_cluster_name" {
  description = "Name of the EKS cluster"
  value       = module.eks.cluster_name
}

output "eks_cluster_certificate_authority" {
  description = "Base64 encoded certificate data for the EKS cluster"
  value       = module.eks.cluster_certificate_authority_data
  sensitive   = true
}

output "eks_node_group_name" {
  description = "Name of the EKS managed node group"
  value       = "ml-services-node-group"
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = module.vpc.private_subnets
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = module.vpc.public_subnets
}

output "mlflow_db_endpoint" {
  description = "RDS endpoint for MLflow backend"
  value       = aws_db_instance.mlflow_db.endpoint
  sensitive   = true
}

output "mlflow_db_name" {
  description = "Database name for MLflow"
  value       = aws_db_instance.mlflow_db.db_name
}

output "ml_models_bucket" {
  description = "S3 bucket for ML model artifacts"
  value       = aws_s3_bucket.ml_models.id
}

output "mlflow_artifacts_bucket" {
  description = "S3 bucket for MLflow experiment artifacts"
  value       = aws_s3_bucket.mlflow_artifacts.id
}

output "ml_datasets_bucket" {
  description = "S3 bucket for versioned ML datasets"
  value       = aws_s3_bucket.ml_datasets.id
}

output "ecr_repositories" {
  description = "ECR repository URLs for each ML service"
  value = {
    for k, v in aws_ecr_repository.ml_services : k => v.repository_url
  }
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group for EKS cluster"
  value       = aws_cloudwatch_log_group.ml_services.name
}

# Cost optimization summary
output "cost_optimization_notes" {
  description = "Summary of cost optimization decisions"
  value = {
    eks_node_type     = "t3.medium (2 vCPU burstable, 4 GiB — matches GCP e2-medium; upgrade to t3.large for sustained inference)"
    rds_instance      = "db.t3.micro (burstable, 1 vCPU, 1 GiB — sufficient for MLflow)"
    nat_gateway       = "single (non-production saves ~$32/month vs multi-AZ)"
    s3_lifecycle      = "Glacier after 90 days, expire after 365 days"
    ecr_lifecycle     = "Keep 10 tagged images, expire untagged after 7 days"
    cloudwatch_retention = "30 days"
  }
}
