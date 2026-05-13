variable "aws_region" {
  description = "AWS region where the ECR repository will be created."
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
