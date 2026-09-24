variable "aws_region" {
  description = "AWS region for the data bucket."
  type        = string
  default     = "eu-north-1"
}

variable "bucket_name" {
  description = "Globally unique S3 bucket name used by the pipeline."
  type        = string
  default     = "ev-battery-health-data"
}

variable "data_directory" {
  description = "Local directory containing the raw CSV files."
  type        = string
  default     = "../src/datas"
}

variable "tags" {
  description = "Tags applied to AWS resources."
  type        = map(string)
  default = {
    Project   = "ev-battery-health-intelligence"
    ManagedBy = "terraform"
  }
}
