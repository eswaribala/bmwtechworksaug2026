variable "aws_region" {
  description = "AWS region for the scorecard resources."
  type        = string
}

variable "project_name" {
  description = "Project name used for resource naming and tags."
  type        = string
}

variable "environment" {
  description = "Deployment environment used for resource tags."
  type        = string
}

variable "bucket_name" {
  description = "Requested bucket name. Underscores are converted to hyphens because S3 bucket names cannot contain underscores."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9_.-]{1,61}[a-z0-9]$", var.bucket_name)) && !strcontains(var.bucket_name, "..")
    error_message = "bucket_name must use lowercase letters, numbers, underscores, hyphens, or periods and be 3-63 characters long."
  }
}

variable "quicksight_role_name" {
  description = "Optional QuickSight role name reserved for manual QuickSight configuration."
  type        = string
  default     = ""
}
