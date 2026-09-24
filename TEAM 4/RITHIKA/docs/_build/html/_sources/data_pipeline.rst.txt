Data Pipeline
=============

Stage 1: Source files and contracts
------------------------------------

Four source domains are represented by CSV files under ``data/``. The Python
layer defines a contract for each dataset in ``python/schemas.py``. A contract
contains required columns, business keys and accepted aliases.

Example telemetry contract concepts include:

* event identifier
* vehicle identifier
* event timestamp
* latitude and longitude
* speed
* battery percentage
* temperature
* region

The sales contract similarly defines ``SALE_ID`` as the business key and
requires vehicle, dealer, date, amount, currency, customer and region fields.

Stage 2: Validation and canonicalization
-----------------------------------------

Before upload, ``python/main.py`` reads the CSV and applies two categories of
checks:

* contract validation: required columns, non-empty files, non-null keys and
  duplicate key detection;
* domain validation: telemetry coordinates and battery range, and non-negative
  sales amounts.

``python/canonicalize.py`` standardizes column names, resolves aliases,
selects the canonical field order, drops duplicate business keys keeping the
last row, and converts timestamps/numeric fields to consistent Python types.
The normalized file is written under ``build/normalized`` and that normalized
file is uploaded to S3.

Stage 3: S3 landing
-------------------

Files are organized under the raw prefix:

.. code-block:: text

   s3://<bucket>/raw/
       telemetry/
           telemetry_initial.csv
           telemetry_incremental.csv
       sales/
           sales_initial.csv
           sales_incremental.csv
       vehicle/
           vehicle_master.csv
       dealer/
           dealer_master.csv

The Python uploader maps dataset types to these prefixes and uses boto3 for
object upload.

Stage 4: External stage
-----------------------

The Snowflake object ``BMW_DW.RAW.BMW_S3_STAGE`` is an external stage backed by
S3. It points to the raw prefix and uses ``BMW_S3_INTEGRATION`` for AWS
credentials/role assumption plus ``CSV_FORMAT`` for file parsing.

The stage is queried with:

.. code-block:: sql

   USE DATABASE BMW_DW;
   USE SCHEMA RAW;

   LIST @BMW_S3_STAGE;

The correct production description is: **the external stage references the S3
files; ``COPY INTO`` reads them through that stage into Snowflake tables**.
The files are not physically copied into an internal Snowflake stage.

Stage 5: RAW ingestion
----------------------

``snowflake/09_initial_load.sql`` uses ``COPY INTO`` statements to load each
source domain from stage subpaths into corresponding RAW tables. The load also
records ``METADATA$FILENAME`` in ``SOURCE_FILE`` and uses ``LOAD_TS`` for
lineage.

Example pattern:

.. code-block:: sql

   COPY INTO BMW_DW.RAW.RAW_TELEMETRY
   FROM (
     SELECT ... , METADATA$FILENAME
     FROM @BMW_DW.RAW.BMW_S3_STAGE/telemetry
   )
   FILE_FORMAT = (FORMAT_NAME = 'BMW_DW.RAW.CSV_FORMAT')
   PATTERN = '.*telemetry.*[.]csv'
   ON_ERROR = 'ABORT_STATEMENT'
   FORCE = FALSE;

The incremental runbook uses the same approach but restricts the pattern to
``incremental`` files. This gives a deterministic way to demonstrate the CDC
pipeline without reprocessing the initial files.

Stage 6: Initial RAW -> STAGING -> ANALYTICS
--------------------------------------------

The initial load script then inserts RAW rows into STAGING and uses ``MERGE``
statements to build:

* ``DIM_REGION``
* ``DIM_VEHICLE``
* ``DIM_DEALER``
* ``FACT_TELEMETRY``
* ``FACT_SALES``

``DIM_DATE`` is pre-populated using Snowflake's ``GENERATOR`` function.

Stage 7: Change data capture
-----------------------------

``snowflake/10_streams.sql`` creates streams on both RAW and STAGING tables.
For example:

.. code-block:: sql

   CREATE OR REPLACE STREAM RAW.RAW_TELEMETRY_STREAM
   ON TABLE RAW.RAW_TELEMETRY;

   CREATE OR REPLACE STREAM STAGING.TELEMETRY_STREAM
   ON TABLE STAGING.STG_TELEMETRY;

A stream exposes metadata such as ``METADATA$ACTION`` so the procedures can
process new inserted/changed records.

Stage 8: Orchestration
----------------------

``snowflake/11_procedures.sql`` contains three procedures:

``STAGING.PROC_RAW_TO_STAGING``
   Consumes RAW streams and merges newly inserted records into STAGING.

``ANALYTICS.PROC_STAGING_TO_ANALYTICS``
   Consumes STAGING streams, maintains dimensions, resolves surrogate keys,
   calculates dates/alerts and merges records into the fact tables.

``ANALYTICS.PROC_RUN_INCREMENTAL_PIPELINE``
   Checks whether RAW or STAGING streams contain changes. It calls the first
   procedure when RAW changes exist and the second procedure when STAGING
   changes exist.

Stage 9: Task execution
-----------------------

``snowflake/12_tasks.sql`` creates ``ANALYTICS.TASK_INCREMENTAL_PIPELINE``
with a five-minute schedule and a ``SYSTEM$STREAM_HAS_DATA`` condition. A
new task is created suspended, so deployment validation should happen before
it is resumed.

For an immediate demonstration, the project runbook supports:

.. code-block:: sql

   EXECUTE TASK BMW_DW.ANALYTICS.TASK_INCREMENTAL_PIPELINE;

Stage 10: Analytics
-------------------

``snowflake/15_analytics.sql`` creates three views:

``VW_SALES_KPI``
   Revenue, count and average sale by month and region.

``VW_TELEMETRY_HEALTH``
   Event volume, average speed, battery, temperature and alert counts by
   region.

``VW_VEHICLE_SALES``
   Units sold and total revenue by vehicle with dealer and region context.
