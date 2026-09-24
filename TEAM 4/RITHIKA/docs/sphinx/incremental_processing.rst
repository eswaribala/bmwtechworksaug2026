Incremental Processing
======================

This is the central capability of the project.

What changes between initial and incremental loads
---------------------------------------------------

Initial batch
~~~~~~~~~~~~~

The initial files are uploaded to S3, exposed through the external stage and
loaded with ``COPY INTO``. Those rows are then moved through STAGING into the
analytical model before Streams are created.

Incremental batch
~~~~~~~~~~~~~~~~~

A second set of files is uploaded with names such as ``telemetry_incremental``
and ``sales_incremental``. The incremental runbook uses ``COPY INTO`` with a
pattern matching only those incremental objects.

The sequence is:

.. code-block:: text

   new CSV
      |
      v
   S3 raw prefix
      |
      v
   external stage
      |
      v
   COPY INTO RAW
      |
      v
   RAW stream records INSERT
      |
      v
   PROC_RAW_TO_STAGING
      |
      v
   STAGING stream records INSERT
      |
      v
   PROC_STAGING_TO_ANALYTICS
      |
      v
   MERGE into dimensions + facts

Idempotency
-----------

The pipeline uses business-key merges rather than blind inserts into the
analytical model. Examples include:

* ``EVENT_ID`` for telemetry.
* ``SALE_ID`` for sales.
* ``VEHICLE_ID`` for vehicle master.
* ``DEALER_ID`` for dealer master.

The combination of ``COPY INTO ... FORCE = FALSE``, deterministic file naming,
stream-based CDC and business-key ``MERGE`` logic keeps re-runs predictable.

Incremental runbook
-------------------

1. Verify the initial fact counts.
2. Upload only the incremental telemetry and sales files.
3. Run the incremental ``COPY INTO`` statements from
   ``scripts/run_incremental_load.sql`` or the equivalent statements in the
   demo runbook.
4. Confirm that the RAW streams have data.
5. Trigger the task immediately for a demo or wait for its schedule.
6. Confirm that STAGING streams have been consumed.
7. Compare analytical fact counts before and after the run.

Immediate execution example
---------------------------

.. code-block:: sql

   EXECUTE TASK BMW_DW.ANALYTICS.TASK_INCREMENTAL_PIPELINE;

Then check task history:

.. code-block:: sql

   SELECT *
   FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
     SCHEDULED_TIME_RANGE_START => DATEADD('hour', -1, CURRENT_TIMESTAMP())
   ))
   WHERE NAME = 'TASK_INCREMENTAL_PIPELINE'
   ORDER BY SCHEDULED_TIME DESC;

Expected capstone proof
-----------------------

The most persuasive evaluator evidence is the before/after result:

.. list-table:: Incremental proof
   :header-rows: 1
   :widths: 25 25 25

   * - Measure
     - Initial
     - After incremental load
   * - ``FACT_TELEMETRY``
     - 8
     - 12
   * - ``FACT_SALES``
     - 5
     - 8

Use the actual executed results in the final submission document if the sample
data is changed.
