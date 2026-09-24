terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "ev_analytics" {
  bucket = var.bucket_name

  tags = {
    Project = "EV Range Analytics"
  }
}

resource "aws_s3_bucket_versioning" "ev_analytics" {
  bucket = aws_s3_bucket.ev_analytics.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "ev_analytics" {
  bucket = aws_s3_bucket.ev_analytics.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_glue_catalog_database" "ev" {
  name = var.glue_database_name
}
