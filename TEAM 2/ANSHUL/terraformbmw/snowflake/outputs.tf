output "snowflake_database" {
  value       = snowflake_database.bmw_sales.name
  description = "BMW Snowflake database"
}

output "snowflake_schema" {
  value       = snowflake_schema.sales.name
  description = "BMW Snowflake schema"
}

output "snowflake_warehouse" {
  value       = snowflake_warehouse.bmw_analytics.name
  description = "BMW Snowflake warehouse"
}

output "snowflake_role" {
  value       = snowflake_account_role.bmw_analytics.name
  description = "BMW Snowflake analytics role"
}

output "snowflake_sales_table_reference" {
  value       = "${snowflake_database.bmw_sales.name}.${snowflake_schema.sales.name}.BMW_SALES"
  description = "Fully qualified BMW sales table reference"
}

output "snowflake_s3_role_arn" {
  value = aws_iam_role.snowflake_s3_role.arn
}

output "snowflake_iam_user_arn" {
  value = snowflake_storage_integration_aws.bmw_s3.describe_output[0].iam_user_arn
}

output "snowflake_storage_integration" {
  value = snowflake_storage_integration_aws.bmw_s3.name
}

output "snowflake_stage" {
  value = snowflake_stage_external_s3.bmw_sales_stage.fully_qualified_name
}

output "s3_bmw_path" {
  value = "s3://${var.s3_bucket_name}/${var.s3_bmw_prefix}"
}