resource "aws_s3_bucket" "bmw_data" {
  bucket = "${var.project_name}-${var.environment}-data"

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Owner       = "Participant-13"
    Purpose     = "BMW Incremental Data Warehouse"
  }
}

resource "aws_s3_bucket_versioning" "bmw_data" {
  bucket = aws_s3_bucket.bmw_data.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "bmw_data" {
  bucket = aws_s3_bucket.bmw_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "bmw_data" {
  bucket = aws_s3_bucket.bmw_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_object" "telemetry_folder" {
  bucket = aws_s3_bucket.bmw_data.id
  key    = "raw/telemetry/"
}

resource "aws_s3_object" "sales_folder" {
  bucket = aws_s3_bucket.bmw_data.id
  key    = "raw/sales/"
}

resource "aws_s3_object" "vehicle_folder" {
  bucket = aws_s3_bucket.bmw_data.id
  key    = "raw/vehicle/"
}

resource "aws_s3_object" "dealer_folder" {
  bucket = aws_s3_bucket.bmw_data.id
  key    = "raw/dealer/"
}