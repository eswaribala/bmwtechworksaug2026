variable "aws_region" {
  description = "AWS deployment region"
  type        = string
  default     = "eu-central-1"
}

variable "bucket_name" {
  description = "Globally unique S3 bucket name"
  type        = string
}
