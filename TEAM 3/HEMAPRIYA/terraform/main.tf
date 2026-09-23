

resource "aws_s3_bucket" "inventory" {
  bucket = var.bucket_name

  tags = {
    Name        = "BMW Dealer Inventory Recommendation"
    Project     = "BMW Dealer Inventory Recommendation"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}



resource "aws_s3_bucket_versioning" "inventory" {
  bucket = aws_s3_bucket.inventory.id

  versioning_configuration {
    status = "Enabled"
  }
}



resource "aws_s3_bucket_server_side_encryption_configuration" "inventory" {
  bucket = aws_s3_bucket.inventory.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "inventory" {
  bucket = aws_s3_bucket.inventory.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}