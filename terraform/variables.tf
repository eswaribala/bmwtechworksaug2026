# ────────────────────────────────────────────────────────────────
# AWS Settings
# ────────────────────────────────────────────────────────────────

variable "aws_region" {
  description = "AWS region to deploy resources into."
  type        = string
  default     = "eu-central-1"
}

# ────────────────────────────────────────────────────────────────
# Project Metadata
# ────────────────────────────────────────────────────────────────

variable "project_name" {
  description = "Prefix used for all resource names."
  type        = string
  default     = "bmw-data-quality"
}

variable "environment" {
  description = "Deployment environment (dev | staging | prod)."
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of: dev, staging, prod."
  }
}

# ────────────────────────────────────────────────────────────────
# S3
# ────────────────────────────────────────────────────────────────

variable "s3_bucket_name" {
  description = "Name of the primary data lake S3 bucket. Leave empty to auto-generate."
  type        = string
  default     = ""
}

variable "s3_force_destroy" {
  description = "Allow Terraform to delete the bucket even if it contains objects. Only set true in dev."
  type        = bool
  default     = false
}

variable "s3_versioning_enabled" {
  description = "Enable S3 object versioning on the data lake bucket."
  type        = bool
  default     = true
}

variable "s3_lifecycle_quarantine_days" {
  description = "Days after which quarantine objects are transitioned to Glacier."
  type        = number
  default     = 90
}

variable "s3_lifecycle_logs_days" {
  description = "Days after which log objects expire (deleted automatically)."
  type        = number
  default     = 365
}

# ────────────────────────────────────────────────────────────────
# IAM
# ────────────────────────────────────────────────────────────────

variable "pipeline_role_name" {
  description = "Name of the IAM role used by the data quality pipeline."
  type        = string
  default     = ""
}

# ────────────────────────────────────────────────────────────────
# CloudWatch
# ────────────────────────────────────────────────────────────────

variable "cloudwatch_log_group" {
  description = "CloudWatch log group name for the pipeline."
  type        = string
  default     = "/bmw/data-quality"
}

variable "cloudwatch_retention_days" {
  description = "Days to retain CloudWatch logs."
  type        = number
  default     = 90
}

variable "alarm_low_quality_threshold" {
  description = "Quality score below which a CloudWatch alarm fires (0-100)."
  type        = number
  default     = 70
}
