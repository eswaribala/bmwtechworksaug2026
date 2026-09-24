resource "snowflake_account_role" "bmw_analyst_readonly" {
  name = var.analyst_role_name
}


resource "snowflake_grant_privileges_to_account_role" "warehouse_usage" {
  account_role_name = snowflake_account_role.bmw_analyst_readonly.name

  privileges = [
    "USAGE"
  ]

  on_account_object {
    object_type = "WAREHOUSE"
    object_name = snowflake_warehouse.bmw_wh.name
  }

  with_grant_option = false
}


resource "snowflake_grant_privileges_to_account_role" "database_usage" {
  account_role_name = snowflake_account_role.bmw_analyst_readonly.name

  privileges = [
    "USAGE"
  ]

  on_account_object {
    object_type = "DATABASE"
    object_name = snowflake_database.bmw_analytics.name
  }

  with_grant_option = false
}


resource "snowflake_grant_privileges_to_account_role" "schema_usage" {
  account_role_name = snowflake_account_role.bmw_analyst_readonly.name

  privileges = [
    "USAGE"
  ]

  on_schema {
    schema_name = snowflake_schema.bmw_data.fully_qualified_name
  }

  with_grant_option = false
}


resource "snowflake_grant_privileges_to_account_role" "vehicle_sales_select" {
  account_role_name = snowflake_account_role.bmw_analyst_readonly.name

  privileges = [
    "SELECT"
  ]

  on_schema_object {
    object_type = "TABLE"
    object_name = snowflake_table.vehicle_sales.fully_qualified_name
  }

  with_grant_option = false
}


resource "snowflake_grant_privileges_to_account_role" "warranty_select" {
  account_role_name = snowflake_account_role.bmw_analyst_readonly.name

  privileges = [
    "SELECT"
  ]

  on_schema_object {
    object_type = "TABLE"
    object_name = snowflake_table.warranty.fully_qualified_name
  }

  with_grant_option = false
}


resource "snowflake_grant_privileges_to_account_role" "faults_select" {
  account_role_name = snowflake_account_role.bmw_analyst_readonly.name

  privileges = [
    "SELECT"
  ]

  on_schema_object {
    object_type = "TABLE"
    object_name = snowflake_table.faults.fully_qualified_name
  }

  with_grant_option = false
}


resource "snowflake_grant_privileges_to_account_role" "battery_select" {
  account_role_name = snowflake_account_role.bmw_analyst_readonly.name

  privileges = [
    "SELECT"
  ]

  on_schema_object {
    object_type = "TABLE"
    object_name = snowflake_table.battery.fully_qualified_name
  }

  with_grant_option = false
}


resource "snowflake_grant_account_role" "grant_to_arul" {
  role_name = snowflake_account_role.bmw_analyst_readonly.name
  user_name = var.analyst_user_name
}