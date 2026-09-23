resource "snowflake_table" "bmw_sales" {
  database = snowflake_database.bmw_sales.name
  schema   = snowflake_schema.sales.name
  name     = "BMW_SALES"

  column {
    name = "SALE_ID"
    type = "VARCHAR"
  }

  column {
    name = "VEHICLE_ID"
    type = "VARCHAR"
  }

  column {
    name = "DEALER_ID"
    type = "VARCHAR"
  }

  column {
    name = "CUSTOMER_ID"
    type = "VARCHAR"
  }

  column {
    name = "SALE_DATE"
    type = "DATE"
  }

  column {
    name = "SALE_YEAR"
    type = "NUMBER"
  }

  column {
    name = "SALE_MONTH"
    type = "NUMBER"
  }

  column {
    name = "MODEL"
    type = "VARCHAR"
  }

  column {
    name = "REGION"
    type = "VARCHAR"
  }

  column {
    name = "PRICE"
    type = "DOUBLE"
  }

  column {
    name = "QUANTITY"
    type = "NUMBER"
  }

  column {
    name = "REVENUE"
    type = "DOUBLE"
  }

  comment = "Processed BMW sales data matching the Parquet schema"
}