variable "project" {
  description = "Project name used for Glue resources."
  type        = string
}

variable "environment" {
  description = "Environment name used for Glue resources."
  type        = string
}

variable "bucket_name" {
  description = "Name of the S3 bucket used for the raw and curated data zones."
  type        = string
}

variable "bucket_arn" {
  description = "ARN of the S3 bucket used for the raw and curated data zones."
  type        = string
}

variable "role_arn" {
  description = "ARN of the IAM role used by the Glue ETL job."
  type        = string
}

variable "tags" {
  description = "Tags applied to Glue resources."
  type        = map(string)
}
