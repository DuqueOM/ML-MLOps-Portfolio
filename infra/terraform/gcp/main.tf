terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  backend "gcs" {
    bucket = "ml-portfolio-duque-om-202602-terraform-state"
    prefix = "terraform/state"
  }
}

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

# GKE Cluster
#tfsec:ignore:AVD-GCP-0047 -- PodSecurityPolicy is deprecated since K8s 1.21; replaced by Pod Security Standards (PSS) enforced via namespace labels (baseline enforce, restricted warn). See ADR-012.
#tfsec:ignore:AVD-GCP-0048 -- Legacy metadata endpoint is disabled at node level via workload_metadata_config SECURE. GKE Metadata Server (GKE_METADATA) blocks legacy /computeMetadata/v1beta1. See ADR-012.
resource "google_container_cluster" "ml_portfolio" {
  name                = "${var.project_name}-gke-${var.environment}"
  location            = var.region
  deletion_protection = false

  # We can't create a cluster with no node pool defined, but we want to only use
  # separately managed node pools. So we create the smallest possible default
  # node pool and immediately delete it.
  remove_default_node_pool = true
  initial_node_count       = 1

  # Minimal config for default pool to avoid quota issues
  node_config {
    disk_size_gb = 20
    machine_type = "e2-medium"
  }

  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.subnet.name

  # Security: Master authorized networks
  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = "10.10.0.0/24"
      display_name = "VPC subnet"
    }
  }

  # Security: Private cluster (private nodes, public endpoint with authorized networks)
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  # Security: Network policy
  network_policy {
    enabled  = true
    provider = "CALICO"
  }

  # Security: IP aliasing (VPC-native cluster)
  ip_allocation_policy {
    cluster_secondary_range_name  = "pod-ranges"
    services_secondary_range_name = "services-range"
  }

  # Security: Resource labels
  resource_labels = {
    environment = var.environment
    project     = var.project_name
    managed_by  = "terraform"
  }

  # Enable Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Enable GKE monitoring and logging
  logging_config {
    enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]
  }

  monitoring_config {
    enable_components = ["SYSTEM_COMPONENTS"]
    managed_prometheus {
      enabled = true
    }
  }

  release_channel {
    channel = "REGULAR"
  }

  addons_config {
    http_load_balancing {
      disabled = false
    }
    horizontal_pod_autoscaling {
      disabled = false
    }
    network_policy_config {
      disabled = false
    }
  }
}

# GKE Node Pool
#tfsec:ignore:AVD-GCP-0048 -- Legacy metadata endpoint disabled via workload_metadata_config GKE_METADATA on node pool. See ADR-012.
resource "google_container_node_pool" "ml_services" {
  name       = "ml-services-pool"
  location   = var.region
  cluster    = google_container_cluster.ml_portfolio.name
  node_count = var.node_count

  autoscaling {
    min_node_count = var.min_node_count
    max_node_count = var.max_node_count
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  node_config {
    disk_size_gb = 30
    image_type   = "COS_CONTAINERD"
    preemptible  = var.environment != "production"
    machine_type = var.machine_type

    # Security: Use dedicated service account instead of default
    service_account = google_service_account.gke_workload.email

    labels = {
      env     = var.environment
      project = var.project_name
    }

    tags = ["ml-portfolio", var.environment]

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    metadata = {
      disable-legacy-endpoints = "true"
    }

    # Security: Protect node metadata from pods
    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }
}

# VPC
resource "google_compute_network" "vpc" {
  name                    = "${var.project_name}-vpc-${var.environment}"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = "${var.project_name}-subnet-${var.environment}"
  ip_cidr_range = "10.10.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc.id

  # Security: VPC Flow Logs
  log_config {
    aggregation_interval = "INTERVAL_10_MIN"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }

  secondary_ip_range {
    range_name    = "services-range"
    ip_cidr_range = "10.20.0.0/16"
  }

  secondary_ip_range {
    range_name    = "pod-ranges"
    ip_cidr_range = "10.30.0.0/16"
  }
}

# Private Service Connection for Cloud SQL
resource "google_compute_global_address" "private_ip_address" {
  name          = "${var.project_name}-private-ip-${var.environment}"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

# Cloud Storage Buckets
#tfsec:ignore:AVD-GCP-0066 -- Staging uses Google-managed encryption (default). CMEK adds $0.06/10K ops + key management overhead; reserved for production PII/PHI data. See ADR-012.
resource "google_storage_bucket" "ml_models" {
  name          = "${var.project_id}-ml-models-${var.environment}"
  location      = var.region
  force_destroy = var.environment != "production"

  uniform_bucket_level_access = true

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
}

#tfsec:ignore:AVD-GCP-0066 -- Staging uses Google-managed encryption. CMEK reserved for production. See ADR-012.
resource "google_storage_bucket" "mlflow_artifacts" {
  name          = "${var.project_id}-mlflow-artifacts-${var.environment}"
  location      = var.region
  force_destroy = var.environment != "production"

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }
}

# Cloud SQL for MLflow
resource "google_sql_database_instance" "mlflow" {
  depends_on       = [google_service_networking_connection.private_vpc_connection]
  name             = "${var.project_name}-mlflow-db-${var.environment}"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = var.db_tier

    backup_configuration {
      enabled    = true
      start_time = "03:00"
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc.id
      require_ssl     = true
    }

    # Security: Database logging flags
    database_flags {
      name  = "log_checkpoints"
      value = "on"
    }
    database_flags {
      name  = "log_connections"
      value = "on"
    }
    database_flags {
      name  = "log_disconnections"
      value = "on"
    }
    database_flags {
      name  = "log_lock_waits"
      value = "on"
    }
    database_flags {
      name  = "log_temp_files"
      value = "0"
    }
  }

  deletion_protection = var.environment == "production"
}

resource "google_sql_database" "mlflow" {
  name     = "mlflow"
  instance = google_sql_database_instance.mlflow.name
}

resource "google_sql_user" "mlflow" {
  name     = "mlflow"
  instance = google_sql_database_instance.mlflow.name
  password = local.db_password_resolved
}

# Artifact Registry
resource "google_artifact_registry_repository" "ml_services" {
  location      = var.region
  repository_id = "${var.project_name}-images"
  description   = "Docker repository for ML services"
  format        = "DOCKER"
}

# Service Account for GKE Workloads
resource "google_service_account" "gke_workload" {
  account_id   = "${var.project_name}-gke-workload"
  display_name = "GKE Workload Service Account"
}

resource "google_project_iam_member" "gke_workload_storage" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.gke_workload.email}"
}

resource "google_project_iam_member" "gke_workload_sql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.gke_workload.email}"
}

# Outputs
output "gke_cluster_name" {
  description = "Name of the GKE cluster"
  value       = google_container_cluster.ml_portfolio.name
}

output "gke_cluster_endpoint" {
  description = "Endpoint for GKE cluster"
  value       = google_container_cluster.ml_portfolio.endpoint
  sensitive   = true
}

output "ml_models_bucket" {
  description = "GCS bucket for ML models"
  value       = google_storage_bucket.ml_models.name
}

output "mlflow_artifacts_bucket" {
  description = "GCS bucket for MLflow artifacts"
  value       = google_storage_bucket.mlflow_artifacts.name
}

output "mlflow_db_connection_name" {
  description = "Cloud SQL connection name"
  value       = google_sql_database_instance.mlflow.connection_name
}

output "artifact_registry_url" {
  description = "Artifact Registry URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.ml_services.repository_id}"
}
