terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  required_version = ">= 1.0"
}

provider "aws" {
  region = var.aws_region
}

# --------------------------------
# S3 Bucket
# --------------------------------

resource "aws_s3_bucket" "bmw_bucket" {
  bucket = var.bucket_name

  tags = {
    Project     = "BMW Predictive Maintenance"
    Environment = "Dev"
  }
}

# --------------------------------
# CloudWatch Log Group
# --------------------------------

resource "aws_cloudwatch_log_group" "bmw_logs" {
  name              = "/aws/bmw-maintenance"
  retention_in_days = 7
}

# --------------------------------
# IAM Role
# --------------------------------

resource "aws_iam_role" "bmw_role" {

  name = "bmw-maintenance-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "ec2.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })
}

# --------------------------------
# Upload Curated Files To S3
# --------------------------------

resource "aws_s3_object" "maintenance_risk_score" {

  bucket = aws_s3_bucket.bmw_bucket.id

  key = "curated/maintenance_risk_score.csv"

  source = "../data/curated/maintenance_risk_score.csv"

  etag = filemd5("../data/curated/maintenance_risk_score.csv")
}

resource "aws_s3_object" "top10_risk_vehicles" {

  bucket = aws_s3_bucket.bmw_bucket.id

  key = "curated/top10_risk_vehicles.csv"

  source = "../data/curated/top10_risk_vehicles.csv"

  etag = filemd5("../data/curated/top10_risk_vehicles.csv")
}