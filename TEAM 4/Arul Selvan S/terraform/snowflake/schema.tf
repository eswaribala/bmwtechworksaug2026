resource "snowflake_schema" "bmw_data" {
  name                = var.schema_name
  database            = snowflake_database.bmw_analytics.name
  is_transient        = false
  with_managed_access = false
}