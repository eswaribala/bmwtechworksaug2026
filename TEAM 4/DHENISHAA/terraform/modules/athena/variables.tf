variable "project" {
  description = "Project name used for the Athena workgroup."
  type        = string
}

variable "environment" {
  description = "Environment name used for the Athena workgroup."
  type        = string
}

variable "bucket_name" {
  description = "Name of the main data lake bucket."
  type        = string
}

variable "bucket_arn" {
  description = "ARN of the main data lake bucket."
  type        = string
}

variable "tags" {
  description = "Tags applied to the Athena workgroup."
  type        = map(string)
}
