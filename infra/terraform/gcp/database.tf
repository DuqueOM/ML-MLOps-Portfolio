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
