terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

# Main project region
provider "aws" {
  region = var.aws_region
}

# QuickSight region
provider "aws" {
  alias  = "quicksight"
  region = "us-west-2"
}