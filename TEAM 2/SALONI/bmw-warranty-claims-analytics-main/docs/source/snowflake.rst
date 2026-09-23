Snowflake
=========

Snowflake is used as the analytical data warehouse for the BMW Warranty
Claims Analytics project.

Database and Schema
-------------------

The Snowflake database is:

::

    BMW_WARRANTY_ANALYTICS

The project schema is:

::

    WARRANTY

Warehouse
---------

The project uses the warehouse:

::

    BMW_WARRANTY_WH

The warehouse is configured as an X-Small warehouse with automatic resume
and automatic suspension.

Warranty Claims Table
---------------------

The main Snowflake table is:

::

    WARRANTY_CLAIMS

The table contains the processed warranty claim information used for
analytics.

The primary columns include:

* ``VEHICLE_ID``
* ``CLAIM_ID``
* ``CLAIM_DATE``
* ``COMPONENT``
* ``CLAIM_AMOUNT``
* ``CLAIM_STATUS``
* ``CLAIM_DATE_PARSED``
* ``REJECTION_REASON``
* ``VALIDATION_STATUS``

S3 Storage Integration
----------------------

Snowflake accesses the processed S3 data through a storage integration.

The storage integration is:

::

    BMW_WARRANTY_S3_INTEGRATION

The integration provides controlled access to the processed warranty
dataset stored in Amazon S3.

Snowflake Stage
---------------

The external stage is:

::

    BMW_WARRANTY_ANALYTICS.WARRANTY.BMW_WARRANTY_S3_STAGE

The stage points to the processed warranty data in Amazon S3.

Data Validation
---------------

The loaded warranty claims can be verified using:

::

    SELECT COUNT(*)
    FROM WARRANTY_CLAIMS;

The validated dataset contains 1,496 warranty claims.

Analytics Views
---------------

The project uses SQL views to organize analytical results.

Component Status Summary
~~~~~~~~~~~~~~~~~~~~~~~~

The view:

::

    COMPONENT_STATUS_SUMMARY

provides warranty claim information grouped by component and claim
status.

Warranty KPI Summary
~~~~~~~~~~~~~~~~~~~~

The view:

::

    WARRANTY_KPI_SUMMARY

provides key warranty metrics used for reporting and dashboard analysis.

Rejection Analysis
~~~~~~~~~~~~~~~~~~

The view:

::

    REJECTION_ANALYSIS

provides information about rejected warranty records and their rejection
reasons.

Component Cost Analysis
-----------------------

Warranty costs can be analyzed using SQL.

Example:

::

    SELECT
        COMPONENT,
        COUNT(*) AS CLAIM_COUNT,
        SUM(CLAIM_AMOUNT) AS TOTAL_CLAIM_AMOUNT
    FROM WARRANTY_CLAIMS
    GROUP BY COMPONENT
    ORDER BY TOTAL_CLAIM_AMOUNT DESC;

This analysis identifies the components generating the highest total
warranty claim costs.

Snowflake's SQL analytics layer provides the data used for downstream
business intelligence and visualization.