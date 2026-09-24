resource "snowflake_table" "vehicle_sales" {
  database = snowflake_database.bmw_analytics.name
  schema   = snowflake_schema.bmw_data.name
  name     = "BMW_VEHICLE_SALES"

  data_retention_time_in_days = 1

  column {
    name     = "VEHICLE_ID"
    type     = "NUMBER(38,0)"
    nullable = true
  }

  column {
    name     = "MODEL"
    type     = "VARCHAR(100)"
    nullable = true
  }

  column {
    name     = "CITY"
    type     = "VARCHAR(100)"
    nullable = true
  }

  column {
    name     = "SALE_DATE"
    type     = "DATE"
    nullable = true
  }

  column {
    name     = "SALES_AMOUNT"
    type     = "FLOAT"
    nullable = true
  }

  column {
    name     = "QUANTITY"
    type     = "NUMBER(38,0)"
    nullable = true
  }
}


resource "snowflake_table" "warranty" {
  database = snowflake_database.bmw_analytics.name
  schema   = snowflake_schema.bmw_data.name
  name     = "BMW_WARRANTY"

  data_retention_time_in_days = 1

  column {
    name     = "VEHICLE_ID"
    type     = "NUMBER(38,0)"
    nullable = true
  }

  column {
    name     = "MODEL"
    type     = "VARCHAR(100)"
    nullable = true
  }

  column {
    name     = "CITY"
    type     = "VARCHAR(100)"
    nullable = true
  }

  column {
    name     = "WARRANTY_DATE"
    type     = "DATE"
    nullable = true
  }

  column {
    name     = "FAULT_TYPE"
    type     = "VARCHAR(100)"
    nullable = true
  }

  column {
    name     = "WARRANTY_COST"
    type     = "FLOAT"
    nullable = true
  }
}


resource "snowflake_table" "faults" {
  database = snowflake_database.bmw_analytics.name
  schema   = snowflake_schema.bmw_data.name
  name     = "BMW_FAULTS"

  data_retention_time_in_days = 1

  column {
    name     = "VEHICLE_ID"
    type     = "NUMBER(38,0)"
    nullable = true
  }

  column {
    name     = "MODEL"
    type     = "VARCHAR(100)"
    nullable = true
  }

  column {
    name     = "CITY"
    type     = "VARCHAR(100)"
    nullable = true
  }

  column {
    name     = "FAULT_DATE"
    type     = "DATE"
    nullable = true
  }

  column {
    name     = "FAULT_TYPE"
    type     = "VARCHAR(100)"
    nullable = true
  }

  column {
    name     = "SEVERITY"
    type     = "VARCHAR(50)"
    nullable = true
  }
}


resource "snowflake_table" "battery" {
  database = snowflake_database.bmw_analytics.name
  schema   = snowflake_schema.bmw_data.name
  name     = "BMW_BATTERY"

  data_retention_time_in_days = 1

  column {
    name     = "VEHICLE_ID"
    type     = "NUMBER(38,0)"
    nullable = true
  }

  column {
    name     = "MODEL"
    type     = "VARCHAR(100)"
    nullable = true
  }

  column {
    name     = "CITY"
    type     = "VARCHAR(100)"
    nullable = true
  }

  column {
    name     = "BATTERY_DATE"
    type     = "DATE"
    nullable = true
  }

  column {
    name     = "BATTERY_PERCENTAGE"
    type     = "FLOAT"
    nullable = true
  }

  column {
    name     = "BATTERY_STATUS"
    type     = "VARCHAR(50)"
    nullable = true
  }
}