variable "project" {
  description = "Project name used for CloudWatch log groups."
  type        = string
}

variable "environment" {
  description = "Environment name used for CloudWatch log groups."
  type        = string
}

variable "tags" {
  description = "Tags applied to CloudWatch resources."
  type        = map(string)
}
