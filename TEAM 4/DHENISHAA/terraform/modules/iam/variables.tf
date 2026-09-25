variable "project" {
  description = "Project name used for IAM role names."
  type        = string
}

variable "environment" {
  description = "Environment name used for IAM role names."
  type        = string
}

variable "tags" {
  description = "Tags applied to IAM resources."
  type        = map(string)
}
