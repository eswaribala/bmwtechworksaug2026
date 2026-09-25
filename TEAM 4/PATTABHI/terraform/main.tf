terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" { region = var.aws_region }

locals {
  datasets = ["sales", "telemetry", "vehicle", "maintenance", "warranty", "dealer"]
  prefixes = concat(
    ["logs/", "athena/"],
    [for dataset in local.datasets : "raw/${dataset}/"],
    [for dataset in local.datasets : "processed/${dataset}/"],
    [for dataset in local.datasets : "curated/${dataset}/"],
    [for dataset in local.datasets : "rejected/${dataset}/"]
  )
}

resource "aws_s3_bucket" "analytics" {
  bucket = var.bucket_name
}

resource "aws_s3_bucket_versioning" "analytics" {
  bucket = aws_s3_bucket.analytics.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "analytics" {
  bucket = aws_s3_bucket.analytics.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "analytics" {
  bucket                  = aws_s3_bucket.analytics.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_object" "prefixes" {
  for_each = toset(local.prefixes)

  bucket  = aws_s3_bucket.analytics.id
  key     = each.value
  content = ""
}

output "bucket_name" { value = aws_s3_bucket.analytics.bucket }
