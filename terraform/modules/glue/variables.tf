variable "project_name" {
  description = "Project name prefix."
  type        = string
}

variable "bucket_name" {
  description = "Name of the S3 data lake bucket."
  type        = string
}

variable "region" {
  description = "AWS region."
  type        = string
}

variable "account_id" {
  description = "AWS account ID."
  type        = string
}
