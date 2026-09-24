resource "aws_s3_bucket" "bmw_bucket" {
  bucket        = var.bucket_name
  force_destroy = true

  tags = {
    Project = "BMW Capstone"
  }
}

# Create folder-like prefixes in S3 so the structure is managed by Terraform.
resource "aws_s3_object" "processed_prefix" {
  bucket  = aws_s3_bucket.bmw_bucket.id
  key     = "processed/"
  content = ""
}

resource "aws_s3_object" "athena_results_prefix" {
  bucket  = aws_s3_bucket.bmw_bucket.id
  key     = "athena-results/"
  content = ""
}

# Upload Cleaned Maintenance File

resource "aws_s3_object" "maintenance_cleaned" {

  bucket = aws_s3_bucket.bmw_bucket.id

  key = "processed/maintenance_cleaned/maintenance_cleaned.csv"

  source = "../maintenance_cleaned.csv"

  etag = filemd5("../maintenance_cleaned.csv")
}

# Upload Joined Dataset

resource "aws_s3_object" "maintenance_joined" {

  bucket = aws_s3_bucket.bmw_bucket.id

  key = "processed/maintenance_dealer_joined/maintenance_dealer_joined.csv"

  source = "../maintenance_dealer_joined.csv"

  etag = filemd5("../maintenance_dealer_joined.csv")
}