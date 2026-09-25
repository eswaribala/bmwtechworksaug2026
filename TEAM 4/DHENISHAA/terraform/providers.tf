provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "BMW Serverless Data Lake"
      Participant = "P15"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
