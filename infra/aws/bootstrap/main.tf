locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

# Bootstrap is intentionally tiny: create only the ECR repository first so an
# image can be pushed before the ECS service is created.
resource "aws_ecr_repository" "app" {
  name                 = "${local.name_prefix}-app"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_lifecycle_policy" "app" {
  repository = aws_ecr_repository.app.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep the last 10 demo images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}
