# ---------------------------------------------------------
# 1. Snowflake Warehouse
# ---------------------------------------------------------

resource "snowflake_warehouse" "bmw_analytics" {
  name = var.warehouse_name

  warehouse_size = "XSMALL"

  auto_suspend = 60
  auto_resume  = "true"

  initially_suspended = true

  comment = "Warehouse for BMW sales analytics"
}


# ---------------------------------------------------------
# 2. Snowflake Database
# ---------------------------------------------------------

resource "snowflake_database" "bmw_sales" {
  name = var.database_name

  comment = "BMW Sales Analytics Database"
}


# ---------------------------------------------------------
# 3. Snowflake Schema
# ---------------------------------------------------------

resource "snowflake_schema" "sales" {
  database = snowflake_database.bmw_sales.name

  name = var.schema_name

  comment = "BMW sales data schema"
}


# ---------------------------------------------------------
# 4. Snowflake Role
# ---------------------------------------------------------

resource "snowflake_account_role" "bmw_analytics" {
  name = var.role_name

  comment = "Role for BMW sales analytics"
}


# ---------------------------------------------------------
# 5. Grant USAGE on Warehouse
# ---------------------------------------------------------

resource "snowflake_grant_privileges_to_account_role" "warehouse_usage" {
  account_role_name = snowflake_account_role.bmw_analytics.name

  privileges = [
    "USAGE"
  ]

  on_account_object {
    object_type = "WAREHOUSE"
    object_name = snowflake_warehouse.bmw_analytics.name
  }
}


# ---------------------------------------------------------
# 6. Grant USAGE on Database
# ---------------------------------------------------------

resource "snowflake_grant_privileges_to_account_role" "database_usage" {
  account_role_name = snowflake_account_role.bmw_analytics.name

  privileges = [
    "USAGE"
  ]

  on_account_object {
    object_type = "DATABASE"
    object_name = snowflake_database.bmw_sales.name
  }
}


# ---------------------------------------------------------
# 7. Grant USAGE + CREATE TABLE on Schema
# ---------------------------------------------------------

resource "snowflake_grant_privileges_to_account_role" "schema_privileges" {
  account_role_name = snowflake_account_role.bmw_analytics.name

  privileges = [
    "USAGE",
    "CREATE TABLE"
  ]

  on_schema {
    schema_name = snowflake_schema.sales.fully_qualified_name
  }
}


# ---------------------------------------------------------
# 8. Grant privileges on future tables
# ---------------------------------------------------------

resource "snowflake_grant_privileges_to_account_role" "future_tables" {
  account_role_name = snowflake_account_role.bmw_analytics.name

  privileges = [
    "SELECT",
    "INSERT",
    "UPDATE",
    "DELETE"
  ]

  on_schema_object {
    future {
      object_type_plural = "TABLES"
      in_schema          = snowflake_schema.sales.fully_qualified_name
    }
  }
}


# ---------------------------------------------------------
# 9. Grant role to current user
# ---------------------------------------------------------

resource "snowflake_grant_account_role" "grant_role_to_user" {
  role_name = snowflake_account_role.bmw_analytics.name
  user_name = var.snowflake_user
}