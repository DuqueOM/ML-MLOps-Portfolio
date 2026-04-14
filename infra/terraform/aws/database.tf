# RDS for MLflow Backend
#tfsec:ignore:AVD-AWS-0133 -- Performance Insights not needed for staging MLflow DB (minimal query load). Enable in production via performance_insights_enabled variable. See ADR-012.
resource "aws_db_instance" "mlflow_db" {
  identifier     = "${var.project_name}-mlflow-db-${var.environment}"
  engine         = "postgres"
  engine_version = "15.4"
  instance_class = var.db_instance_class

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_encrypted     = true

  db_name  = "mlflow"
  username = var.db_username
  password = local.db_password_resolved

  vpc_security_group_ids = [aws_security_group.mlflow_db.id]
  db_subnet_group_name   = aws_db_subnet_group.mlflow.name

  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "mon:04:00-mon:05:00"

  deletion_protection                 = var.environment == "production"
  iam_database_authentication_enabled = true

  skip_final_snapshot       = var.environment != "production"
  final_snapshot_identifier = var.environment == "production" ? "${var.project_name}-mlflow-db-final-${formatdate("YYYY-MM-DD-hhmm", timestamp())}" : null

  tags = {
    Name        = "${var.project_name}-mlflow-db"
    Environment = var.environment
  }
}

resource "aws_db_subnet_group" "mlflow" {
  name       = "${var.project_name}-mlflow-db-subnet-${var.environment}"
  subnet_ids = module.vpc.private_subnets

  tags = {
    Name = "${var.project_name}-mlflow-db-subnet"
  }
}
