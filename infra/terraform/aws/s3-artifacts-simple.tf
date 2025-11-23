# Simplified S3 Artifact Store Module
# Staff Engineer Demo: Infrastructure as Code for ML Model Storage
# This demonstrates best practices for versioned, secure artifact storage

resource "aws_s3_bucket" "ml_models_artifact_store" {
  bucket = "${var.project_name}-mlops-models-store-${var.environment}"

  tags = {
    Name        = "ML Models Artifact Store"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
    Purpose     = "MLOps model versioning and storage"
  }
}

# Enable versioning for model reproducibility
resource "aws_s3_bucket_versioning" "artifact_versioning" {
  bucket = aws_s3_bucket.ml_models_artifact_store.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Server-side encryption for compliance
resource "aws_s3_bucket_server_side_encryption_configuration" "artifact_encryption" {
  bucket = aws_s3_bucket.ml_models_artifact_store.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block public access (security best practice)
resource "aws_s3_bucket_public_access_block" "artifact_security" {
  bucket = aws_s3_bucket.ml_models_artifact_store.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lifecycle policy to manage costs (transition old versions to Glacier)
resource "aws_s3_bucket_lifecycle_configuration" "artifact_lifecycle" {
  bucket = aws_s3_bucket.ml_models_artifact_store.id

  rule {
    id     = "archive-old-model-versions"
    status = "Enabled"

    noncurrent_version_transition {
      noncurrent_days = 90
      storage_class   = "GLACIER"
    }

    noncurrent_version_expiration {
      noncurrent_days = 365
    }
  }

  rule {
    id     = "expire-incomplete-multipart-uploads"
    status = "Enabled"

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# Bucket for MLflow experiment artifacts
resource "aws_s3_bucket" "mlflow_artifacts_store" {
  bucket = "${var.project_name}-mlflow-artifacts-${var.environment}"

  tags = {
    Name        = "MLflow Artifacts Store"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
    Purpose     = "MLflow experiment tracking artifacts"
  }
}

resource "aws_s3_bucket_versioning" "mlflow_versioning" {
  bucket = aws_s3_bucket.mlflow_artifacts_store.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "mlflow_encryption" {
  bucket = aws_s3_bucket.mlflow_artifacts_store.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "mlflow_security" {
  bucket = aws_s3_bucket.mlflow_artifacts_store.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Outputs for use in CI/CD and applications
output "models_bucket_name" {
  description = "S3 bucket name for ML model artifacts"
  value       = aws_s3_bucket.ml_models_artifact_store.bucket
}

output "models_bucket_arn" {
  description = "ARN of the ML models artifact store"
  value       = aws_s3_bucket.ml_models_artifact_store.arn
}

output "mlflow_bucket_name" {
  description = "S3 bucket name for MLflow artifacts"
  value       = aws_s3_bucket.mlflow_artifacts_store.bucket
}

output "mlflow_bucket_arn" {
  description = "ARN of the MLflow artifacts store"
  value       = aws_s3_bucket.mlflow_artifacts_store.arn
}
