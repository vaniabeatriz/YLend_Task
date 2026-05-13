variable "aws_region" {
  description = "AWS region where the ECS/RDS demo environment will run."
  type        = string
}

variable "project_name" {
  description = "Short project name used as an AWS resource prefix."
  type        = string
  default     = "yl-loans"
}

variable "environment" {
  description = "Environment label, for example demo."
  type        = string
  default     = "demo"
}

variable "image_uri" {
  description = "Versioned ECR image URI to run in ECS."
  type        = string
}

variable "auth0_domain" {
  description = "Auth0 tenant domain."
  type        = string
}

variable "auth0_client_id" {
  description = "Auth0 application client ID."
  type        = string
}

variable "auth0_audience" {
  description = "Auth0 API audience."
  type        = string
}

variable "auth0_client_secret" {
  description = "Auth0 application client secret."
  type        = string
  sensitive   = true
}

variable "app_secret_key" {
  description = "Flask session secret key."
  type        = string
  sensitive   = true
}

variable "desired_count" {
  description = "Number of ECS tasks to run. Keep 1 for the demo."
  type        = number
  default     = 1
}

variable "task_cpu" {
  description = "Fargate CPU units for the Flask container."
  type        = number
  default     = 256
}

variable "task_memory" {
  description = "Fargate memory in MiB for the Flask container."
  type        = number
  default     = 512
}

variable "db_instance_class" {
  description = "Small RDS instance class for the demo database."
  type        = string
  default     = "db.t4g.micro"
}
