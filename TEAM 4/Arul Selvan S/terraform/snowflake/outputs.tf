output "database_name" {
  value = snowflake_database.bmw_analytics.name
}

output "warehouse_name" {
  value = snowflake_warehouse.bmw_wh.name
}

output "schema_name" {
  value = snowflake_schema.bmw_data.name
}

output "vehicle_sales_table" {
  value = snowflake_table.vehicle_sales.fully_qualified_name
}

output "warranty_table" {
  value = snowflake_table.warranty.fully_qualified_name
}

output "faults_table" {
  value = snowflake_table.faults.fully_qualified_name
}

output "battery_table" {
  value = snowflake_table.battery.fully_qualified_name
}

output "analyst_role" {
  value = snowflake_account_role.bmw_analyst_readonly.name
}
