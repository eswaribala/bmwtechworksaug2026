variable "log_group_name" {
  description = "CloudWatch log group name."
  type        = string
}

variable "retention_days" {
  description = "Days to retain log events."
  type        = number
  default     = 90
}

variable "alarm_low_quality_threshold" {
  description = "Quality score threshold that triggers the alarm."
  type        = number
  default     = 70
}

variable "project_name" {
  description = "Project name prefix."
  type        = string
}

variable "bucket_name" {
  description = "S3 bucket name (used in dashboard queries)."
  type        = string
}

variable "region" {
  description = "AWS region (used in dashboard widget regions)."
  type        = string
}
