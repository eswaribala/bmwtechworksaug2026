locals {
  raw_files = fileset(var.data_directory, "*.csv")

  content_types = {
    "csv" = "text/csv"
  }
}

resource "aws_s3_bucket" "data" {
  bucket        = var.bucket_name
  force_destroy = false
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket = aws_s3_bucket.data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "data" {
  bucket = aws_s3_bucket.data.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_object" "raw_files" {
  for_each = local.raw_files

  bucket       = aws_s3_bucket.data.id
  key          = "raw/${trimsuffix(each.value, ".csv")}/${each.value}"
  source       = "${var.data_directory}/${each.value}"
  etag         = filemd5("${var.data_directory}/${each.value}")
  content_type = lookup(local.content_types, "csv", "application/octet-stream")
}
