# EKS Cluster
#tfsec:ignore:AVD-AWS-0040 -- Public API access restricted to allowed_cidr_blocks (not 0.0.0.0/0). Required for CI/CD and developer kubectl access. Private access also enabled. See ADR-012.
#tfsec:ignore:AVD-AWS-0104 -- Node egress to internet required for ECR image pulls, S3 model downloads, and CloudWatch logs. NAT Gateway restricts to private subnets only. See ADR-012.
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

# CloudWatch Log Group
#tfsec:ignore:AVD-AWS-0017 -- Log group uses AWS-managed encryption (default). CMK encryption adds key management overhead; reserved for production with audit requirements. See ADR-012.
resource "aws_cloudwatch_log_group" "ml_services" {
  name              = "/aws/eks/${var.project_name}-${var.environment}"
  retention_in_days = 30

  tags = {
    Name        = "${var.project_name}-logs"
    Environment = var.environment
  }
}
