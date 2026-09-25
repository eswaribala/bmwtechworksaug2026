variable "bucket_name" {
  description = "Name of the S3 bucket used for the BMW data lake."
  type        = string
}

variable "environment" {
  description = "Environment name used in tags."
  type        = string
}

variable "project" {
  description = "Project name used in tags."
  type        = string
}

variable "tags" {
  description = "Tags to apply to the bucket resources."
  type        = map(string)
}
