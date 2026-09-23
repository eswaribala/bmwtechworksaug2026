ETL Pipeline
============

The ETL pipeline in this project is responsible for cleaning and validating the raw BMW sales dataset before it is stored for analysis.

Purpose
-------

The ETL workflow ensures that sales data is:

- structurally valid
- free of duplicates
- free of missing critical identifiers
- numeric where required
- ready for warehouse ingestion and reporting

Input and output
-----------------

The ETL job reads the raw CSV file from:

.. code-block:: text

   src/pysparkmodule/data/bmw_sales_records.csv

After cleaning, it writes the processed Parquet file to:

.. code-block:: text

   src/pysparkmodule/data/bmw_sales_cleaned.parquet

Transformation steps
--------------------

The cleaning flow performs the following tasks:

- cast columns to the correct data types
- validate required identifiers and timestamps
- trim blank values
- drop incomplete rows
- remove duplicate sale records
- keep only valid price and quantity values
- calculate derived values for downstream analytics

Key logic areas
---------------

Type definition
~~~~~~~~~~~~~~~

Important fields are cast to the correct types before analysis, including:

- sale_id
- vehicle_id
- dealer_id
- customer_id
- sale_date
- model
- region
- price
- quantity

Validation
~~~~~~~~~~

The pipeline rejects rows that contain:

- missing sale identifiers
- invalid quantity values
- invalid or zero prices
- empty critical business fields

Output contract
---------------

The cleaned Parquet dataset is expected to contain these fields:

- sale_id
- vehicle_id
- dealer_id
- customer_id
- sale_date
- sale_year
- sale_month
- model
- region
- price
- quantity
- revenue

This contract is important because downstream systems such as Snowflake and the forecasting model rely on this consistent schema.
