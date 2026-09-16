variable "role_name" {
  description = "Name of the IAM role."
  type        = string
}

variable "bucket_arn" {
  description = "ARN of the S3 data lake bucket."
  type        = string
}

variable "bucket_name" {
  description = "Name of the S3 data lake bucket (used for Athena results path)."
  type        = string
}

variable "cloudwatch_log_group" {
  description = "Name of the CloudWatch log group."
  type        = string
}

variable "project_name" {
  description = "Project prefix for naming policies."
  type        = string
}

variable "account_id" {
  description = "AWS account ID."
  type        = string
}

variable "region" {
  description = "AWS region."
  type        = string
}
