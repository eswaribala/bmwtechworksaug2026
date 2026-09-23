BMW Sales Data Pipeline
=======================

This project performs end-to-end ETL on BMW sales data, stores the cleaned data in Parquet,
loads it into Snowflake via S3, and keeps a separate forecasting workflow for next-month sales prediction.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   installation
   architecture
   etl_pipeline
   forecasting
   infrastructure
   api_reference

Overview
--------

The platform is designed in a modular way:

- Raw sales data is loaded and cleaned in the PySpark ETL layer.
- Cleaned data is written to Parquet for downstream storage and analytics.
- The curated data is then loaded to Snowflake through S3 and external stages.
- A separate forecasting workflow produces monthly predictions without changing the original ETL pipeline.
- QuickSight can access the Snowflake views to build dashboards.

Project flow
------------

.. code-block:: text

   Raw CSV
      ↓
   PySpark ETL cleaning
      ↓
   Cleaned Parquet (bmw_sales_cleaned.parquet)
      ↓
   S3 raw / processed folder structure
      ↓
   Snowflake stage and tables
      ↓
   QuickSight dashboards
      ↓
   Separate forecasting model output

This documentation is organized so the infrastructure, ETL logic, and forecasting pipeline remain easy to understand and maintain.
