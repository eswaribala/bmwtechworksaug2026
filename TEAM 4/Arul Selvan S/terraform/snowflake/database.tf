resource "snowflake_database" "bmw_analytics" {
  name         = var.database_name
  is_transient = false
}