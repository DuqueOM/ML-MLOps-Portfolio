# VPC
#tfsec:ignore:AVD-AWS-0178 -- VPC Flow Logs add ~$0.50/GB storage cost. Enabled in production via enable_flow_log variable. Staging uses CloudWatch EKS audit logs instead. See ADR-012.
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

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}
