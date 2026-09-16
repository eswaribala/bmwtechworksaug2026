terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.50"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  # Uncomment to store state in S3 (recommended for team use)
  # backend "s3" {
  #   bucket         = "bmw-terraform-state"
  #   key            = "data-quality/terraform.tfstate"
  #   region         = "eu-central-1"
  #   dynamodb_table = "terraform-state-lock"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "BMW-DataQuality"
      Participant = "Participant12"
      Pod         = "PodD"
      ManagedBy   = "Terraform"
    }
  }
}
