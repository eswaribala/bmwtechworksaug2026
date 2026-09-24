Project Overview
================

Objective
---------

The platform is designed to ingest and incrementally process four BMW data
products:

.. list-table:: Source domains
   :header-rows: 1
   :widths: 20 45 35

   * - Dataset
     - Purpose
     - Natural/business key
   * - Telemetry
     - Vehicle sensor and movement events
     - ``EVENT_ID``
   * - Sales
     - Vehicle sales transactions
     - ``SALE_ID``
   * - Vehicle master
     - Vehicle attributes and dealer assignment
     - ``VEHICLE_ID``
   * - Dealer master
     - Dealer attributes and regional information
     - ``DEALER_ID``

The initial files are uploaded to S3 under a raw prefix. Snowflake reads them
through an external stage and loads them into RAW tables. The initial batch is
then promoted to STAGING and ANALYTICS. After that, incremental files are
loaded into RAW, captured by streams, propagated by stored procedures, and
finally merged into the analytical facts and dimensions.

Expected demonstration
----------------------

The capstone dataset is designed around an easily verifiable incremental
scenario:

* Telemetry grows from 8 initial records to 12 after the incremental batch.
* Sales grows from 5 initial records to 8 after the incremental batch.
* Vehicle and dealer master data are loaded initially and maintained through
  the same CDC framework when changes are introduced.

Why the layered design matters
------------------------------

The project deliberately separates concerns:

``RAW``
   Immutable-ish ingestion boundary containing source records plus source-file
   and load-time metadata.

``STAGING``
   Conformed records where incremental updates are merged by business key.

``ANALYTICS``
   Dimensional model intended for reporting, KPI queries and read-only API
   consumption.

This makes the pipeline easier to audit, replay and troubleshoot than loading
raw CSVs directly into fact tables.

Repository structure
--------------------

.. code-block:: text

   bmw-snowflake-incremental-dw/
   |
   +-- data/
   |   +-- telemetry/
   |   +-- sales/
   |   +-- vehicle/
   |   +-- dealer/
   |
   +-- python/
   |   +-- config.py
   |   +-- schemas.py
   |   +-- canonicalize.py
   |   +-- data_validation.py
   |   +-- s3_ingestion.py
   |   +-- main.py
   |   +-- logger.py
   |
   +-- pyspark/
   |   +-- telemetry_processing.py
   |
   +-- snowflake/
   |   +-- 01_database.sql
   |   +-- 02_file_formats.sql
   |   +-- 03_storage_integration.sql
   |   +-- 04_stages.sql
   |   +-- 05_raw_tables.sql
   |   +-- 06_staging_tables.sql
   |   +-- 07_dimensions.sql
   |   +-- 08_facts.sql
   |   +-- 09_initial_load.sql
   |   +-- 10_streams.sql
   |   +-- 11_procedures.sql
   |   +-- 12_tasks.sql
   |   +-- 13_time_travel.sql
   |   +-- 14_zero_copy_clone.sql
   |   +-- 15_analytics.sql
   |   +-- 16_security_grants.sql
   |   +-- 17_health_checks.sql
   |
   +-- terraform/
   +-- api/
   +-- tests/
   +-- scripts/
   +-- .github/workflows/
   +-- pyproject.toml
   +-- README.md
