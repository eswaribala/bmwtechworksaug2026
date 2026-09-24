ETL Pipeline
============

The ETL process is implemented in Python using PySpark to transform raw service data into a usable
analytics dataset.

Data Ingestion
--------------

The pipeline reads source files such as:

- dealer_large.csv
- maintenance_large_100k.csv

Data Cleaning
-------------

The cleaning stage removes or handles:

- missing values
- duplicate records
- invalid dealer IDs
- invalid service IDs
- incorrect or inconsistent cost values

Data Transformation
-------------------

Key transformation rules include:

- computing `repair_cost = parts_cost + labour_cost`
- validating essential attributes
- aligning maintenance records with dealer metadata

Data Integration
----------------

The service records are joined with dealer information using the `dealer_id` key to create the final
analytics-ready dataset:

- maintenance_dealer_joined.csv

This integrated dataset is then stored in S3 and used as the source for Athena queries and KPI views.
