# Service Account for GKE Workloads
resource "google_service_account" "gke_workload" {
  account_id   = "${var.project_name}-gke-workload"
  display_name = "GKE Workload Service Account"
}

# Bucket-level IAM (least-privilege — replaces project-level objectAdmin)
# GKE workload SA can read models (inference) and read/write mlflow artifacts (tracking)
resource "google_storage_bucket_iam_member" "gke_workload_models_viewer" {
  bucket = google_storage_bucket.ml_models.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.gke_workload.email}"
}

resource "google_storage_bucket_iam_member" "gke_workload_mlflow_admin" {
  bucket = google_storage_bucket.mlflow_artifacts.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.gke_workload.email}"
}

resource "google_project_iam_member" "gke_workload_sql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.gke_workload.email}"
}
