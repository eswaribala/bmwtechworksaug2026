variable "aws_region" {
  description = "AWS region for the BMW Dealer Inventory Recommendation project"
  type        = string
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "S3 bucket for the BMW Dealer Inventory Recommendation project"
  type        = string
  default     = "bmw-dealer-inventory-recommendation-2026"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "Development"
}