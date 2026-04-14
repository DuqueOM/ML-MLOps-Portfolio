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
