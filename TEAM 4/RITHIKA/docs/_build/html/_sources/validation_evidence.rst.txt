Validation and Evaluator Evidence
=================================

The final project document should prove the implementation with outputs rather
than asking an evaluator to run every SQL file manually.

Environment
-----------

.. code-block:: sql

   SELECT
     CURRENT_ACCOUNT() AS ACCOUNT,
     CURRENT_USER() AS USER_NAME,
     CURRENT_ROLE() AS ROLE_NAME,
     CURRENT_DATABASE() AS DATABASE_NAME,
     CURRENT_SCHEMA() AS SCHEMA_NAME,
     CURRENT_WAREHOUSE() AS WAREHOUSE_NAME;

AWS/S3 evidence
---------------

Capture:

* S3 bucket and raw object list.
* Snowflake ``LIST @BMW_S3_STAGE`` output.
* Storage integration properties from ``DESC STORAGE INTEGRATION``.

Warehouse object evidence
-------------------------

Run:

.. code-block:: sql

   SHOW SCHEMAS IN DATABASE BMW_DW;
   SHOW TABLES IN SCHEMA BMW_DW.RAW;
   SHOW TABLES IN SCHEMA BMW_DW.STAGING;
   SHOW TABLES IN SCHEMA BMW_DW.ANALYTICS;
   SHOW STREAMS IN SCHEMA BMW_DW.RAW;
   SHOW STREAMS IN SCHEMA BMW_DW.STAGING;
   SHOW TASKS IN SCHEMA BMW_DW.ANALYTICS;
   SHOW PROCEDURES IN SCHEMA BMW_DW.ANALYTICS;

Row-count evidence
------------------

The best compact proof is the result of ``17_health_checks.sql``. Capture the
single combined row-count table and explain the expected initial/after-change
counts.

Incremental evidence
--------------------

Capture both before and after results:

.. code-block:: sql

   SELECT
     (SELECT COUNT(*) FROM BMW_DW.ANALYTICS.FACT_TELEMETRY) AS TELEMETRY_COUNT,
     (SELECT COUNT(*) FROM BMW_DW.ANALYTICS.FACT_SALES) AS SALES_COUNT;

The demonstration target is 8 -> 12 telemetry and 5 -> 8 sales.

CDC evidence
------------

Before the Task consumes them, capture:

.. code-block:: sql

   SELECT * FROM BMW_DW.RAW.RAW_TELEMETRY_STREAM;
   SELECT * FROM BMW_DW.STAGING.TELEMETRY_STREAM;

Task evidence
-------------

Capture recent Task History showing successful execution.

Data quality evidence
---------------------

Useful checks include:

.. code-block:: sql

   SELECT EVENT_ID, COUNT(*)
   FROM BMW_DW.ANALYTICS.FACT_TELEMETRY
   GROUP BY EVENT_ID
   HAVING COUNT(*) > 1;

and:

.. code-block:: sql

   SELECT SALE_ID, COUNT(*)
   FROM BMW_DW.ANALYTICS.FACT_SALES
   GROUP BY SALE_ID
   HAVING COUNT(*) > 1;

A ``Query produced no results`` response is a successful outcome for a duplicate
check, because it means no duplicates were found.

Time Travel and clone evidence
------------------------------

Capture one historical query from ``13_time_travel.sql`` and the source/clone
row counts from ``14_zero_copy_clone.sql``.

Analytics evidence
------------------

Capture the output from ``VW_SALES_KPI`` and ``VW_TELEMETRY_HEALTH``. These
show that the warehouse is not merely storing data; it supports business
analysis.
