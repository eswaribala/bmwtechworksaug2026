variable "aws_region" {
  description = "AWS region where resources will be created"
  type        = string
  default     = "eu-north-1"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "snowflake-data-warehousing"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}