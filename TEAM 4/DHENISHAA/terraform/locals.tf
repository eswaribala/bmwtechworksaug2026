locals {
  common_tags = {
    Project     = "BMW Serverless Data Lake"
    Participant = var.participant
    Environment = var.environment
    ManagedBy   = "Terraform"
  }

  resource_prefix = "${var.project_name}-${var.environment}"
  bucket_name     = "${var.project_name}-${var.environment}-${var.bucket_suffix}"
}
