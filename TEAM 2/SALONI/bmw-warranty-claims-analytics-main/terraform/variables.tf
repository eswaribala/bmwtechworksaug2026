variable "aws_region" {
  description = "AWS region for the BMW warranty analytics project"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "bmw-warranty-claims"
}