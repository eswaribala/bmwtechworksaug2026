Architecture
============

The BMW sales architecture is designed to keep the core data flow simple and modular.

High-level flow
---------------

1. Raw sales CSV is loaded from the project data folder.
2. PySpark cleans and transforms the raw file.
3. The cleaned output is saved as a Parquet file.
4. The processed file is uploaded to S3 in a structured key layout.
5. Snowflake reads the data from S3 using a storage integration and external stage.
6. Analytics and reporting are built using Snowflake views and QuickSight dashboards.
7. A separate forecasting model reads the cleaned dataset and generates next-month estimates.

Core layers
-----------

ETL layer
~~~~~~~~~

The ETL layer handles:

- validating fields
- dropping duplicates
- cleaning invalid values
- standardizing types
- generating the cleaned Parquet file

Forecasting layer
~~~~~~~~~~~~~~~~~

The forecasting layer is intentionally separate from the source ETL flow. It:

- reads the cleaned Parquet output
- aggregates monthly sales data
- creates lag and rolling window features
- trains a model for revenue forecasting
- saves next-month predictions to a CSV output file

Analytics layer
~~~~~~~~~~~~~~~

Snowflake and AWS provide the reporting layer:

- S3 stores raw and processed datasets
- Snowflake loads the data into warehouse tables
- QuickSight connects to Snowflake views for dashboarding

Design principles
-----------------

- Keep the ETL pipeline unchanged when adding forecasting logic.
- Maintain a clear separation between raw, processed, and forecast outputs.
- Save forecast output as a separate artifact instead of overwriting original data.
- Use Snowflake views for reporting, not direct modification of raw historical tables.
