/**
 * S3 Module — BMW Data Quality Data Lake Bucket
 * Creates the S3 bucket, versioning, encryption, lifecycle rules, and
 * placeholder objects that represent the logical folder structure.
 *
 * Folder structure:
 *   raw/vehicle_master/
 *   raw/telemetry/
 *   curated/
 *   quarantine/
 *   reports/
 *   logs/
 */

# ────────────────────────────────────────────────
# Bucket
# ────────────────────────────────────────────────

resource "aws_s3_bucket" "data_lake" {
  bucket        = var.bucket_name
  force_destroy = var.force_destroy

  tags = {
    Name = var.bucket_name
    Role = "DataLake"
  }
}

# ────────────────────────────────────────────────
# Block all public access
# ────────────────────────────────────────────────

resource "aws_s3_bucket_public_access_block" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ────────────────────────────────────────────────
# Versioning
# ────────────────────────────────────────────────

resource "aws_s3_bucket_versioning" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  versioning_configuration {
    status = var.versioning_enabled ? "Enabled" : "Suspended"
  }
}

# ────────────────────────────────────────────────
# Server-Side Encryption (AES-256)
# ────────────────────────────────────────────────

resource "aws_s3_bucket_server_side_encryption_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

# ────────────────────────────────────────────────
# Lifecycle Rules
# ────────────────────────────────────────────────

resource "aws_s3_bucket_lifecycle_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  # Quarantine → Glacier after N days
  rule {
    id     = "quarantine-to-glacier"
    status = "Enabled"

    filter {
      prefix = "quarantine/"
    }

    transition {
      days          = var.lifecycle_quarantine_days
      storage_class = "GLACIER"
    }

    expiration {
      days = var.lifecycle_quarantine_days * 3
    }
  }

  # Logs → expire after N days
  rule {
    id     = "logs-expiration"
    status = "Enabled"

    filter {
      prefix = "logs/"
    }

    expiration {
      days = var.lifecycle_logs_days
    }
  }

  # Reports → move to STANDARD_IA after 30 days
  rule {
    id     = "reports-to-ia"
    status = "Enabled"

    filter {
      prefix = "reports/"
    }

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 180
      storage_class = "GLACIER"
    }
  }

  # Noncurrent (old) versions → delete after 30 days
  rule {
    id     = "delete-old-versions"
    status = "Enabled"

    filter {}

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}

# ────────────────────────────────────────────────
# Folder Placeholder Objects
# Creates the logical folder structure inside S3 (per spec §7).
# ────────────────────────────────────────────────

locals {
  folders = [
    "raw/vehicle_master/",
    "raw/telemetry/",
    "curated/",
    "quarantine/",
    "reports/",
    "reports/athena-results/",
    "logs/",
  ]
}

resource "aws_s3_object" "folders" {
  for_each = toset(local.folders)

  bucket  = aws_s3_bucket.data_lake.id
  key     = each.value
  content = ""

  tags = {
    CreatedBy = "Terraform"
  }
}

# ────────────────────────────────────────────────
# CORS (for frontend direct uploads)
# ────────────────────────────────────────────────

resource "aws_s3_bucket_cors_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST", "HEAD"]
    allowed_origins = ["*"] # Restrict to your domain in production
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}
