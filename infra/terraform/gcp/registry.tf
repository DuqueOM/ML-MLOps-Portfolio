# Artifact Registry
resource "google_artifact_registry_repository" "ml_services" {
  location      = var.region
  repository_id = "${var.project_name}-images"
  description   = "Docker repository for ML services"
  format        = "DOCKER"
}
