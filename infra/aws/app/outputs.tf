output "service_url" {
  description = "Public base URL for the deployed website and API."
  value       = local.service_url
}

output "ecs_cluster_name" {
  description = "ECS cluster name used by verification and rollback commands."
  value       = aws_ecs_cluster.app.name
}

output "ecs_service_name" {
  description = "ECS service name used by verification and rollback commands."
  value       = aws_ecs_service.app.name
}

output "rds_endpoint" {
  description = "RDS endpoint for operator visibility. It is not publicly reachable."
  value       = aws_db_instance.loans.address
}

output "image_uri" {
  description = "Image URI currently configured in the ECS task definition."
  value       = var.image_uri
}
