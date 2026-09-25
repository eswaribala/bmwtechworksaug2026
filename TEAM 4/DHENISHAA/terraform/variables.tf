variable "aws_region" {
  description = "AWS region used for all deployment resources."
  type        = string
  default     = "us-east-1"

  validation {
    condition     = length(trimspace(var.aws_region)) > 0
    error_message = "aws_region must not be empty."
  }
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "test", "prod"], var.environment)
    error_message = "environment must be one of: dev, test, prod."
  }
}

variable "project_name" {
  description = "Name prefix used for AWS resources."
  type        = string
  default     = "bmw-serverless-data-lake"
}

variable "participant" {
  description = "Participant identifier for resource tags."
  type        = string
  default     = "P15"
}

variable "bucket_suffix" {
  description = "Suffix appended to the data lake bucket name."
  type        = string
  default     = "bmw-data-lake-dev"

  validation {
    condition     = length(trimspace(var.bucket_suffix)) > 0
    error_message = "bucket_suffix must not be empty."
  }
}

variable "quicksight_enabled" {
  description = "Whether QuickSight resources are enabled for the account."
  type        = bool
  default     = false
}
