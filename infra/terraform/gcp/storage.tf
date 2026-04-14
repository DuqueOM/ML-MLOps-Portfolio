# Cloud Storage Buckets
#tfsec:ignore:AVD-GCP-0066 -- Staging uses Google-managed encryption (default). CMEK adds $0.06/10K ops + key management overhead; reserved for production PII/PHI data. See ADR-012.
resource "google_storage_bucket" "ml_models" {
  name          = "${var.project_id}-ml-models-${var.environment}"
  location      = var.region
  force_destroy = var.environment != "production"

  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type = "Delete"
    }
  }

  logging {
    log_bucket        = google_storage_bucket.audit_logs.name
    log_object_prefix = "ml-models/"
  }
}

#tfsec:ignore:AVD-GCP-0066 -- Staging uses Google-managed encryption. CMEK reserved for production. See ADR-012.
resource "google_storage_bucket" "mlflow_artifacts" {
  name          = "${var.project_id}-mlflow-artifacts-${var.environment}"
  location      = var.region
  force_destroy = var.environment != "production"

  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type = "Delete"
    }
  }

  logging {
    log_bucket        = google_storage_bucket.audit_logs.name
    log_object_prefix = "mlflow-artifacts/"
  }
}

# Audit Logs Bucket (target for access logging from ml_models and mlflow_artifacts)
#tfsec:ignore:AVD-GCP-0066 -- Audit logs use Google-managed encryption. See ADR-012.
resource "google_storage_bucket" "audit_logs" {
  name          = "${var.project_id}-audit-logs-${var.environment}"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
}
