output "ecr_repository_url" {
  description = "Repository URL used by docker tag and docker push."
  value       = aws_ecr_repository.app.repository_url
}
