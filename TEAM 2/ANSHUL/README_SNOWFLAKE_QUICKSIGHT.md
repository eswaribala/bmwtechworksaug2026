# Snowflake + QuickSight Integration Guide

This document explains how the BMW sales project integrates Snowflake and QuickSight for analytics and dashboarding.

## Overview

The project loads processed sales data into Snowflake and then exposes it to QuickSight for dashboard creation. The recommended pattern is:

- load data into Snowflake tables from S3
- create views for reporting
- connect QuickSight to Snowflake
- build dashboards using curated views instead of raw tables

This keeps the data layer clean and makes the dashboards easier to maintain.

## Data flow

```text
S3 bucket (anshul-ki-balti)
  ↓
Snowflake external stage (BMW_SALES_STAGE)
  ↓
COPY INTO BMW_SALES table
  ↓
Reporting views for actual + forecast data
  ↓
QuickSight dataset connection
  ↓
Executive dashboard visuals
```

## Required Snowflake objects

The working project configuration is:

- database: `BMW_SALES_DB`
- schema: `SALES`
- warehouse: `BMW_ANALYTICS_WH`
- role: `BMW_ANALYTICS_ROLE`
- storage integration: `BMW_S3_INTEGRATION`
- stage: `BMW_SALES_STAGE`
- raw/processed S3 prefix: `s3://anshul-ki-balti/processed/bmw/`
- base table: `BMW_SALES`
- forecast table: `BMW_SALES_FORECAST`
- reporting view: `BMW_SALES_WITH_FORECAST_VW`

## S3 integration pattern

The bucket used in this project is:

```text
anshul-ki-balti
```

Processed data is stored under:

```text
processed/bmw/
processed/bmw/forecast/
```

The Terraform storage integration and external stage are configured to point at the processed BMW prefix, which mirrors the cleaned Parquet dataset used by Snowflake.

## Step 1: create the database, schema, warehouse, and role

```sql
CREATE OR REPLACE DATABASE BMW_SALES_DB;
CREATE OR REPLACE SCHEMA BMW_SALES_DB.SALES;

CREATE OR REPLACE WAREHOUSE BMW_ANALYTICS_WH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;

CREATE OR REPLACE ROLE BMW_ANALYTICS_ROLE;
GRANT USAGE ON WAREHOUSE BMW_ANALYTICS_WH TO ROLE BMW_ANALYTICS_ROLE;
GRANT USAGE ON DATABASE BMW_SALES_DB TO ROLE BMW_ANALYTICS_ROLE;
GRANT USAGE ON SCHEMA BMW_SALES_DB.SALES TO ROLE BMW_ANALYTICS_ROLE;
GRANT CREATE TABLE, CREATE VIEW, CREATE STAGE ON SCHEMA BMW_SALES_DB.SALES TO ROLE BMW_ANALYTICS_ROLE;
GRANT ROLE BMW_ANALYTICS_ROLE TO USER <YOUR_SNOWFLAKE_USER>;
```

## Step 2: create the base sales table matching the Parquet schema

The cleaned Parquet file schema used by the project is aligned to the following structure:

```sql
CREATE OR REPLACE TABLE BMW_SALES_DB.SALES.BMW_SALES (
    sale_id VARCHAR,
    vehicle_id VARCHAR,
    dealer_id VARCHAR,
    customer_id VARCHAR,
    sale_date DATE,
    sale_year NUMBER,
    sale_month NUMBER,
    model VARCHAR,
    region VARCHAR,
    price NUMBER(18,2),
    quantity NUMBER,
    revenue NUMBER(18,2)
);
```

This matches the ETL output produced from the cleaned data files, including the revenue field generated in the Spark pipeline.

## Step 3: create the Snowflake stage and load the data from the S3 bucket

```sql
CREATE OR REPLACE STAGE BMW_SALES_DB.SALES.BMW_SALES_STAGE
    URL = 's3://anshul-ki-balti/processed/bmw/'
    STORAGE_INTEGRATION = BMW_S3_INTEGRATION
    FILE_FORMAT = (TYPE = PARQUET);
```

Load the cleaned parquet dataset into Snowflake:

```sql
COPY INTO BMW_SALES_DB.SALES.BMW_SALES
FROM @BMW_SALES_DB.SALES.BMW_SALES_STAGE
MATCH_BY_COLUMN_NAME = CASE_SENSITIVE
FILE_FORMAT = (TYPE = PARQUET);
```

If your bucket stores a file named with a specific prefix or filename, use a more explicit path such as:

```sql
COPY INTO BMW_SALES_DB.SALES.BMW_SALES
FROM @BMW_SALES_DB.SALES.BMW_SALES_STAGE/
MATCH_BY_COLUMN_NAME = CASE_SENSITIVE
FILE_FORMAT = (TYPE = PARQUET);
```

## Step 4: create the forecast table and load the forecast CSV

```sql
CREATE OR REPLACE TABLE BMW_SALES_DB.SALES.BMW_SALES_FORECAST (
    forecast_month DATE,
    model VARCHAR,
    region VARCHAR,
    predicted_revenue NUMBER(18,2),
    created_at TIMESTAMP_TZ
);
```

If the forecast output is uploaded into a dedicated forecast folder, use the stage location in that folder:

```sql
COPY INTO BMW_SALES_DB.SALES.BMW_SALES_FORECAST
FROM @BMW_SALES_DB.SALES.BMW_SALES_STAGE/forecast/
FILE_FORMAT = (
    TYPE = CSV,
    FIELD_OPTIONALLY_ENCLOSED_BY = '"',
    SKIP_HEADER = 1
);
```

If the forecast file is named `bmw_next_month_forecast.csv`, the direct path is usually:

```sql
COPY INTO BMW_SALES_DB.SALES.BMW_SALES_FORECAST
FROM (
    SELECT
        $1::DATE AS forecast_month,
        $2::VARCHAR AS model,
        $3::VARCHAR AS region,
        $4::NUMBER(18,2) AS predicted_revenue,
        $5::TIMESTAMP_TZ AS created_at
    FROM @BMW_SALES_DB.SALES.BMW_SALES_STAGE/forecast/bmw_next_month_forecast.csv
)
FILE_FORMAT = (
    TYPE = CSV,
    FIELD_OPTIONALLY_ENCLOSED_BY = '"',
    SKIP_HEADER = 1
);
```

## Step 5: create the reporting views for QuickSight

### Actual sales reporting view

```sql
CREATE OR REPLACE VIEW BMW_SALES_DB.SALES.BMW_SALES_VW AS
SELECT
    sale_date,
    sale_year,
    sale_month,
    model,
    region,
    price,
    quantity,
    revenue
FROM BMW_SALES_DB.SALES.BMW_SALES;
```

### Forecast reporting view

```sql
CREATE OR REPLACE VIEW BMW_SALES_DB.SALES.BMW_SALES_FORECAST_VW AS
SELECT
    forecast_month,
    model,
    region,
    predicted_revenue,
    created_at
FROM BMW_SALES_DB.SALES.BMW_SALES_FORECAST;
```

### Combined actual + forecast view

```sql
CREATE OR REPLACE VIEW BMW_SALES_DB.SALES.BMW_SALES_WITH_FORECAST_VW AS
SELECT
    sale_date AS period_date,
    model,
    region,
    revenue AS revenue_value,
    'actual' AS record_type
FROM BMW_SALES_DB.SALES.BMW_SALES

UNION ALL

SELECT
    forecast_month AS period_date,
    model,
    region,
    predicted_revenue AS revenue_value,
    'forecast' AS record_type
FROM BMW_SALES_DB.SALES.BMW_SALES_FORECAST;
```

This is the ideal dataset for dashboarding because it gives a single combined view of historical and forecast revenue.

## QuickSight configuration

In QuickSight:

1. Go to `Datasets`
2. Click `Create dataset`
3. Select `Snowflake`
4. Enter the Snowflake connection details:
   - host: `XJ05853.eu-north-1.aws.snowflakecomputing.com`
   - database: `BMW_SALES_DB`
   - schema: `SALES`
   - warehouse: `BMW_ANALYTICS_WH`
   - user: your reporting user
5. Choose the view you want to analyze, such as:
   - `BMW_SALES_VW`
   - `BMW_SALES_FORECAST_VW`
   - `BMW_SALES_WITH_FORECAST_VW`

## Role and permissions

Grant read access to the reporting role:

```sql
CREATE OR REPLACE ROLE BMW_QUICKSIGHT_READONLY;
GRANT USAGE ON DATABASE BMW_SALES_DB TO ROLE BMW_QUICKSIGHT_READONLY;
GRANT USAGE ON SCHEMA BMW_SALES_DB.SALES TO ROLE BMW_QUICKSIGHT_READONLY;
GRANT SELECT ON VIEW BMW_SALES_DB.SALES.BMW_SALES_VW TO ROLE BMW_QUICKSIGHT_READONLY;
GRANT SELECT ON VIEW BMW_SALES_DB.SALES.BMW_SALES_FORECAST_VW TO ROLE BMW_QUICKSIGHT_READONLY;
GRANT SELECT ON VIEW BMW_SALES_DB.SALES.BMW_SALES_WITH_FORECAST_VW TO ROLE BMW_QUICKSIGHT_READONLY;
GRANT ROLE BMW_QUICKSIGHT_READONLY TO USER <YOUR_QUICKSIGHT_USER>;
```

## Recommended dashboard design

### 1. Historical sales dashboard
Use `BMW_SALES_VW` for:

- revenue by month
- revenue by region
- revenue by model
- quantity sold and average price

### 2. Forecast dashboard
Use `BMW_SALES_FORECAST_VW` for:

- next-month forecast revenue
- forecast by model
- forecast by region
- forecast KPI cards

### 3. Executive summary dashboard
Use `BMW_SALES_WITH_FORECAST_VW` for:

- actual vs forecast revenue line chart
- model-wise comparison
- region-wise comparison
- KPI cards for total actual revenue and total forecast revenue

## Best practices

- Keep raw tables separate from reporting views.
- Use views for business dashboards instead of direct table access.
- Keep forecast data in its own table and join it only when needed.
- Maintain a consistent date field across actual and forecast tables.
- Use role-based access control for QuickSight users.
- Prefer `BMW_SALES_WITH_FORECAST_VW` as the canonical dashboard dataset for management reporting.

## Troubleshooting

### QuickSight connection issues

Check:

- Snowflake hostname is correct
- warehouse is active
- user has access to the database and view
- network and AWS permissions allow the connection

### Missing records in dashboard

Verify:

- the table was loaded successfully
- the stage path is correct
- the file format matches the dataset
- the data types match the Snowflake schema exactly

### Stage path mismatch

If the stage is configured as `processed/bmw/`, make sure the uploaded file is in that prefix and the `COPY INTO` path references it correctly.

## Summary

This architecture enables a clean analytics workflow:

- raw and processed data land in S3
- Snowflake acts as the analytics engine
- QuickSight provides business dashboards
- forecasts remain isolated from the original ETL flow

This separation keeps the project clean, auditable, and easy to extend.
