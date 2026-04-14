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
