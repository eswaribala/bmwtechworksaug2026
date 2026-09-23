resource "aws_s3_bucket" "bmw_warranty" {
  bucket = "${var.project_name}-${data.aws_caller_identity.current.account_id}"

  tags = {
    Project     = "BMW Warranty Claims Analytics"
    Participant = "P5"
    Environment = "Development"
    ManagedBy   = "Terraform"
  }
}

data "aws_caller_identity" "current" {}

resource "aws_s3_bucket_versioning" "bmw_warranty" {
  bucket = aws_s3_bucket.bmw_warranty.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "bmw_warranty" {
  bucket = aws_s3_bucket.bmw_warranty.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "bmw_warranty" {
  bucket = aws_s3_bucket.bmw_warranty.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ------------------------------------------------------------
# AWS Glue Data Catalog Database for Athena
# ------------------------------------------------------------

resource "aws_glue_catalog_database" "bmw_warranty" {
  name        = "bmw_warranty_analytics"
  description = "AWS Glue Data Catalog database for BMW Warranty Claims Analytics - Participant 5"
}

resource "aws_glue_catalog_table" "warranty_valid" {
  name          = "warranty_valid"
  database_name = aws_glue_catalog_database.bmw_warranty.name
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://${var.project_name}-${data.aws_caller_identity.current.account_id}/processed/warranty_valid/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "vehicle_id"
      type = "string"
    }

    columns {
      name = "claim_id"
      type = "string"
    }

    columns {
      name = "claim_date"
      type = "string"
    }

    columns {
      name = "component"
      type = "string"
    }

    columns {
      name = "claim_amount"
      type = "double"
    }

    columns {
      name = "claim_status"
      type = "string"
    }

    columns {
      name = "claim_date_parsed"
      type = "date"
    }

    columns {
      name = "rejection_reason"
      type = "string"
    }

    columns {
      name = "validation_status"
      type = "string"
    }
  }
}

resource "aws_glue_catalog_table" "warranty_enriched" {
  name          = "warranty_enriched"
  database_name = aws_glue_catalog_database.bmw_warranty.name
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://${var.project_name}-${data.aws_caller_identity.current.account_id}/processed/warranty_enriched/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "vehicle_id"
      type = "string"
    }

    columns {
      name = "claim_id"
      type = "string"
    }

    columns {
      name = "claim_date"
      type = "string"
    }

    columns {
      name = "component"
      type = "string"
    }

    columns {
      name = "claim_amount"
      type = "double"
    }

    columns {
      name = "claim_status"
      type = "string"
    }

    columns {
      name = "claim_date_parsed"
      type = "date"
    }

    columns {
      name = "rejection_reason"
      type = "string"
    }

    columns {
      name = "validation_status"
      type = "string"
    }
  }
}

resource "aws_glue_catalog_table" "warranty_rejected" {
  name          = "warranty_rejected"
  database_name = aws_glue_catalog_database.bmw_warranty.name
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://${var.project_name}-${data.aws_caller_identity.current.account_id}/processed/warranty_rejected/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "vehicle_id"
      type = "string"
    }

    columns {
      name = "claim_id"
      type = "string"
    }

    columns {
      name = "claim_date"
      type = "string"
    }

    columns {
      name = "component"
      type = "string"
    }

    columns {
      name = "claim_amount"
      type = "double"
    }

    columns {
      name = "claim_status"
      type = "string"
    }

    columns {
      name = "claim_date_parsed"
      type = "date"
    }

    columns {
      name = "rejection_reason"
      type = "string"
    }

    columns {
      name = "validation_status"
      type = "string"
    }
  }
}

# ------------------------------------------------------------
# QuickSight Glue Data Catalog Database - us-west-2
# ------------------------------------------------------------

resource "aws_glue_catalog_database" "bmw_warranty_quicksight" {
  provider    = aws.quicksight
  name        = "bmw_warranty_analytics"
  description = "AWS Glue Data Catalog database for BMW Warranty Claims Analytics - QuickSight"
}

# ------------------------------------------------------------
# QuickSight Glue Table - warranty_valid - us-west-2
# ------------------------------------------------------------

resource "aws_glue_catalog_table" "warranty_valid_quicksight" {
  provider      = aws.quicksight
  name          = "warranty_valid"
  database_name = aws_glue_catalog_database.bmw_warranty_quicksight.name
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://${var.project_name}-${data.aws_caller_identity.current.account_id}/processed/warranty_valid/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "vehicle_id"
      type = "string"
    }

    columns {
      name = "claim_id"
      type = "string"
    }

    columns {
      name = "claim_date"
      type = "string"
    }

    columns {
      name = "component"
      type = "string"
    }

    columns {
      name = "claim_amount"
      type = "double"
    }

    columns {
      name = "claim_status"
      type = "string"
    }

    columns {
      name = "claim_date_parsed"
      type = "date"
    }

    columns {
      name = "rejection_reason"
      type = "string"
    }

    columns {
      name = "validation_status"
      type = "string"
    }
  }
}