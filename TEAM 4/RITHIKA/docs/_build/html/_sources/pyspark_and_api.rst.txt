PySpark and API Layers
======================

PySpark batch processing
------------------------

``pyspark/telemetry_processing.py`` demonstrates an independent Spark path for
batch processing of raw telemetry. Its purpose is to show that the platform can
also support compute-intensive processing outside the Snowflake CDC path.

The conceptual flow is:

.. code-block:: text

   S3 raw telemetry
         |
         v
      PySpark
         |
         +-- filtering / aggregation
         |
         v
   S3 processed telemetry (Parquet)

This batch path is intentionally independent from the Snowflake Streams/Tasks
pipeline. The Snowflake path is the capstone's transactional incremental
warehouse flow; the Spark path demonstrates scalable batch transformation.

FastAPI read-only interface
---------------------------

``api/main.py`` exposes warehouse KPIs without allowing callers to mutate the
warehouse.

Endpoints
~~~~~~~~~

``GET /health``
   Performs a simple Snowflake ``SELECT 1`` connectivity check.

``GET /kpis/sales``
   Reads ``ANALYTICS.VW_SALES_KPI``.

``GET /kpis/telemetry``
   Reads ``ANALYTICS.VW_TELEMETRY_HEALTH``.

``GET /vehicles/top-selling``
   Reads ``ANALYTICS.VW_VEHICLE_SALES`` and returns the top ten by revenue and
   units sold.

Run locally
~~~~~~~~~~~

.. code-block:: powershell

   uvicorn api.main:app --reload --port 8000

Then use the FastAPI interactive documentation at ``/docs``.

Authentication and secrets
~~~~~~~~~~~~~~~~~~~~~~~~~~

The API reads Snowflake connection information from environment variables. The
preferred production approach is key-pair authentication or another managed
secret mechanism rather than hard-coded passwords.
