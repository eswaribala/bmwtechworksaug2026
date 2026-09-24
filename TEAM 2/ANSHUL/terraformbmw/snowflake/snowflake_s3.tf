# ---------------------------------------------------------
# Snowflake Storage Integration
# ---------------------------------------------------------

resource "snowflake_storage_integration_aws" "bmw_s3" {

  name = "BMW_S3_INTEGRATION"

  enabled = true

  storage_provider = "S3"

  storage_allowed_locations = [
    "s3://${var.s3_bucket_name}/${var.s3_bmw_prefix}"
  ]

  storage_aws_role_arn = aws_iam_role.snowflake_s3_role.arn

  storage_aws_external_id = var.snowflake_external_id

  comment = "Snowflake access to BMW processed sales data in S3"
}


# ---------------------------------------------------------
# External S3 Stage
# ---------------------------------------------------------

resource "snowflake_stage_external_s3" "bmw_sales_stage" {

  name = "BMW_SALES_STAGE"

  database = snowflake_database.bmw_sales.name

  schema = snowflake_schema.sales.name

  url = "s3://${var.s3_bucket_name}/${var.s3_bmw_prefix}"

  storage_integration = snowflake_storage_integration_aws.bmw_s3.name

  file_format {
    parquet {
      compression = "AUTO"
      use_logical_type = "true"
    }
  }

  comment = "External stage for BMW sales Parquet data"
}