data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  bucket_name = var.bucket_name
}

resource "aws_s3_bucket" "demo" {
  bucket = local.bucket_name
}

resource "aws_s3_bucket_public_access_block" "demo" {
  bucket                  = aws_s3_bucket.demo.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "demo" {
  bucket = aws_s3_bucket.demo.id
  rule {
    apply_server_side_encryption_by_default { sse_algorithm = "AES256" }
  }
}

# Upload the original raw CSV into the raw/bmw/ folder
resource "aws_s3_object" "raw_sales_csv" {
  bucket       = aws_s3_bucket.demo.id
  key          = "raw/bmw/bmw_sales_records.csv"
  source       = "${path.module}/../bmw_sales_records.csv"
  etag         = filemd5("${path.module}/../bmw_sales_records.csv")
  content_type = "text/csv"
  acl          = "private"
}

# Upload the cleaned parquet file into the processed/bmw/ folder
resource "aws_s3_object" "processed_sales_parquet" {
  bucket       = aws_s3_bucket.demo.id
  key          = "processed/bmw/bmw_sales_cleaned.parquet"
  source       = "${path.module}/../../pysparkws/src/pysparkmodule/data/bmw_sales_cleaned.parquet"
  etag         = filemd5("${path.module}/../../pysparkws/src/pysparkmodule/data/bmw_sales_cleaned.parquet")
  content_type = "application/octet-stream"
  acl          = "private"
}
