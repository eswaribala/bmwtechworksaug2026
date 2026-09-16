variable "bucket_name" {
  description = "Name of the S3 bucket to create."
  type        = string
}

variable "force_destroy" {
  description = "If true, the bucket can be destroyed even if it still contains objects."
  type        = bool
  default     = false
}

variable "versioning_enabled" {
  description = "Enable S3 object versioning."
  type        = bool
  default     = true
}

variable "lifecycle_quarantine_days" {
  description = "Days before quarantine objects are transitioned to Glacier."
  type        = number
  default     = 90
}

variable "lifecycle_logs_days" {
  description = "Days before log objects are automatically deleted."
  type        = number
  default     = 365
}

variable "project_name" {
  description = "Project name used for tagging."
  type        = string
}
