terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "ml-portfolio-terraform-state"
    key            = "ml-portfolio/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "ML-Portfolio"
      Owner       = "DuqueOM"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# EKS Cluster
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "${var.project_name}-eks-${var.environment}"
  cluster_version = "1.28"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  cluster_endpoint_public_access       = true
  cluster_endpoint_public_access_cidrs = var.allowed_cidr_blocks
  cluster_endpoint_private_access      = true

  cluster_enabled_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  eks_managed_node_groups = {
    ml_services = {
      name = "ml-services-node-group"

      instance_types = [var.node_instance_type]
      capacity_type  = "ON_DEMAND"

      min_size     = 1
      max_size     = 5
      desired_size = 1

      labels = {
        role = "ml-services"
      }

      tags = {
        NodeGroup = "ml-services"
      }
    }
  }

  tags = {
    Name = "${var.project_name}-eks-${var.environment}"
  }
}

# VPC
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.project_name}-vpc-${var.environment}"
  cidr = var.vpc_cidr

  azs             = data.aws_availability_zones.available.names
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs

  enable_nat_gateway   = true
  single_nat_gateway   = var.environment != "production"
  enable_dns_hostnames = true
  enable_dns_support   = true

  public_subnet_tags = {
    "kubernetes.io/role/elb" = "1"
  }

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = "1"
  }

  tags = {
    Name = "${var.project_name}-vpc-${var.environment}"
  }
}

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

# RDS for MLflow Backend
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
  password = var.db_password

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

# Security Group for RDS
resource "aws_security_group" "mlflow_db" {
  name        = "${var.project_name}-mlflow-db-sg-${var.environment}"
  description = "Security group for MLflow database"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description     = "PostgreSQL from EKS"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [module.eks.cluster_security_group_id]
  }

  egress {
    description = "Allow outbound to VPC"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [var.vpc_cidr]
  }

  tags = {
    Name = "${var.project_name}-mlflow-db-sg"
  }
}

# ECR Repositories
resource "aws_ecr_repository" "ml_services" {
  for_each = toset([
    "bankchurn-predictor",
    "nlpinsight-analyzer",
    "carvision-intelligence",
  ])

  name                 = "${var.project_name}/${each.key}"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = {
    Name        = "${var.project_name}-${each.key}"
    Service     = each.key
    Environment = var.environment
  }
}

resource "aws_ecr_lifecycle_policy" "ml_services" {
  for_each   = aws_ecr_repository.ml_services
  repository = each.value.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["v"]
          countType     = "imageCountMoreThan"
          countNumber   = 10
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2
        description  = "Remove untagged images after 7 days"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 7
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "ml_services" {
  name              = "/aws/eks/${var.project_name}-${var.environment}"
  retention_in_days = 30

  tags = {
    Name        = "${var.project_name}-logs"
    Environment = var.environment
  }
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

# Outputs are defined in outputs.tf
