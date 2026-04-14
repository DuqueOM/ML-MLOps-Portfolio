# S3 Bucket for ML Models
resource "aws_s3_bucket" "ml_models" {
  bucket = "${var.project_name}-ml-models-${var.environment}"

  tags = {
    Name        = "${var.project_name}-ml-models"
    Purpose     = "ML Model Storage"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "ml_models" {
  bucket = aws_s3_bucket.ml_models.id

  versioning_configuration {
    status = "Enabled"
  }
}

#tfsec:ignore:AVD-AWS-0132 -- Uses AWS-managed KMS key (aws:kms). Customer-managed CMK adds $1/month/key + rotation management; reserved for production PII data. See ADR-012.
resource "aws_s3_bucket_server_side_encryption_configuration" "ml_models" {
  bucket = aws_s3_bucket.ml_models.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "ml_models" {
  bucket = aws_s3_bucket.ml_models.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_logging" "ml_models" {
  bucket        = aws_s3_bucket.ml_models.id
  target_bucket = aws_s3_bucket.ml_models.id
  target_prefix = "access-logs/ml-models/"
}

resource "aws_s3_bucket_lifecycle_configuration" "ml_models" {
  bucket = aws_s3_bucket.ml_models.id

  rule {
    id     = "transition-old-models"
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

# S3 Bucket for Datasets (equivalent to GCP datasets-production bucket)
resource "aws_s3_bucket" "ml_datasets" {
  bucket = "${var.project_name}-datasets-${var.environment}"

  tags = {
    Name        = "${var.project_name}-datasets"
    Purpose     = "Versioned ML Datasets"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "ml_datasets" {
  bucket = aws_s3_bucket.ml_datasets.id

  versioning_configuration {
    status = "Enabled"
  }
}

#tfsec:ignore:AVD-AWS-0132 -- Uses AWS-managed KMS key (aws:kms). CMK reserved for production. See ADR-012.
resource "aws_s3_bucket_server_side_encryption_configuration" "ml_datasets" {
  bucket = aws_s3_bucket.ml_datasets.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "ml_datasets" {
  bucket = aws_s3_bucket.ml_datasets.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_logging" "ml_datasets" {
  bucket        = aws_s3_bucket.ml_datasets.id
  target_bucket = aws_s3_bucket.ml_datasets.id
  target_prefix = "access-logs/datasets/"
}

# S3 Bucket for MLflow Artifacts
resource "aws_s3_bucket" "mlflow_artifacts" {
  bucket = "${var.project_name}-mlflow-artifacts-${var.environment}"

  tags = {
    Name        = "${var.project_name}-mlflow-artifacts"
    Purpose     = "MLflow Artifact Storage"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "mlflow_artifacts" {
  bucket = aws_s3_bucket.mlflow_artifacts.id

  versioning_configuration {
    status = "Enabled"
  }
}

#tfsec:ignore:AVD-AWS-0132 -- Uses AWS-managed KMS key (aws:kms). CMK reserved for production. See ADR-012.
resource "aws_s3_bucket_server_side_encryption_configuration" "mlflow_artifacts" {
  bucket = aws_s3_bucket.mlflow_artifacts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "mlflow_artifacts" {
  bucket = aws_s3_bucket.mlflow_artifacts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_logging" "mlflow_artifacts" {
  bucket        = aws_s3_bucket.mlflow_artifacts.id
  target_bucket = aws_s3_bucket.mlflow_artifacts.id
  target_prefix = "access-logs/mlflow/"
}

resource "aws_s3_bucket_lifecycle_configuration" "mlflow_artifacts" {
  bucket = aws_s3_bucket.mlflow_artifacts.id

  rule {
    id     = "transition-old-artifacts"
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
