variable "bucket_arn" {
  description = "ARN of the main S3 data lake bucket."
  type        = string
}

variable "database_arn" {
  description = "ARN of the Glue Catalog database."
  type        = string
}

variable "project" {
  description = "Project name used for governance resources."
  type        = string
}

variable "environment" {
  description = "Environment name used for governance resources."
  type        = string
}

variable "tags" {
  description = "Tags applied to governance-related resources."
  type        = map(string)
}
