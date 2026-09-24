variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-north-1"
}

variable "project_name" {
  type    = string
  default = "bmw-commercial analytics"
}

variable "environment" {
  type    = string
  default = "dev"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging or prod."
  }
}

variable "bucket_name" {
  description = "Name of the S3 bucket for raw and processed BMW data"
  type        = string
  default     = "anshul-ki-balti"
}
