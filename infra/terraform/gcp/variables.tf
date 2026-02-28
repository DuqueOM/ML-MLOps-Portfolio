variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "ml-portfolio"
}

variable "environment" {
  description = "Environment (dev, staging, production)"
  type        = string
  default     = "production"

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "machine_type" {
  description = "Machine type for GKE nodes. e2-medium (1 shared vCPU, 4GB) works for dev. For production load, upgrade to e2-standard-2 (2 dedicated vCPU, 8GB) — ~$24/mo more but eliminates CPU throttling under concurrent inference."
  type        = string
  default     = "e2-medium"
}

variable "node_count" {
  description = "Initial number of nodes (1 node handles full portfolio workload)"
  type        = number
  default     = 1
}

variable "min_node_count" {
  description = "Minimum number of nodes for autoscaling"
  type        = number
  default     = 1
}

variable "max_node_count" {
  description = "Maximum number of nodes for autoscaling"
  type        = number
  default     = 5
}

variable "db_tier" {
  description = "Cloud SQL tier"
  type        = string
  default     = "db-f1-micro"
}

variable "db_password" {
  description = "Password for MLflow database"
  type        = string
  sensitive   = true
}
