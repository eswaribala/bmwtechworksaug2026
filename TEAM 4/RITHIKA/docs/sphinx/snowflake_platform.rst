Snowflake Platform
==================

Database and warehouse
----------------------

``01_database.sql`` creates the ``BMW_DW`` database and the schemas:

* ``RAW``
* ``STAGING``
* ``ANALYTICS``

It also creates ``BMW_WH`` as an XSMALL warehouse with auto-resume enabled and
short auto-suspend behavior.

File format
-----------

``02_file_formats.sql`` defines ``RAW.CSV_FORMAT`` with comma delimiters,
optional quoting, header skipping, whitespace trimming and standard null
handling.

RAW layer
---------

The RAW tables are source-aligned and retain ingestion metadata:

* ``RAW_TELEMETRY``
* ``RAW_SALES``
* ``RAW_VEHICLE``
* ``RAW_DEALER``

Each includes a source-file field and load timestamp so an evaluator can trace
a warehouse record back to its S3 source object.

STAGING layer
-------------

The STAGING tables add ``UPDATED_TS`` and are the target of the RAW-to-STAGING
incremental merges:

* ``STG_TELEMETRY``
* ``STG_SALES``
* ``STG_VEHICLE``
* ``STG_DEALER``

ANALYTICS layer
---------------

The analytical layer contains both dimensions and facts.

.. list-table:: Analytical objects
   :header-rows: 1
   :widths: 28 72

   * - Object
     - Purpose
   * - ``DIM_DATE``
     - Calendar/date attributes used for reporting.
   * - ``DIM_REGION``
     - Standardized region lookup with surrogate key.
   * - ``DIM_VEHICLE``
     - Vehicle master attributes with surrogate key.
   * - ``DIM_DEALER``
     - Dealer master attributes with surrogate key.
   * - ``FACT_TELEMETRY``
     - Vehicle telemetry measurements and derived alert flags.
   * - ``FACT_SALES``
     - Sales transactions linked to vehicle, dealer, region and date.

Security model
--------------

``16_security_grants.sql`` creates ``BMW_ANALYTICS_READONLY`` and grants read
access to all current and future tables/views in the ANALYTICS schema. This is
intended as the least-privilege role for the API/reporting layer.

Health checks
-------------

``17_health_checks.sql`` produces a single object-count result covering RAW,
STAGING, dimensions and facts, followed by recent task history. This is useful
for deployment evidence and operational checks.
