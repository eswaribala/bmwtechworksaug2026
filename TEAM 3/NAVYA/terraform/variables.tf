variable "aws_region" {
  description = "AWS region for the BMW ETL platform"
  type        = string
  default     = "eu-north-1"
}

variable "bucket_name" {
  description = "S3 bucket for the BMW Enterprise Batch ETL platform"
  type        = string
  default     = "bmw-enterprise-etl-navya-2026"
}