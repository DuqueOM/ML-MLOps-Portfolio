# ECR Repositories
resource "aws_ecr_repository" "ml_services" {
  for_each = toset([
    "bankchurn-predictor",
    "nlpinsight-analyzer",
    "chicagotaxi-pipeline",
  ])

  name                 = "${var.project_name}/${each.key}"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  #tfsec:ignore:AVD-AWS-0033 -- ECR uses AES256 (AWS-managed). KMS encryption adds $1/month/key per repo; reserved for production with compliance requirements. See ADR-012.
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
