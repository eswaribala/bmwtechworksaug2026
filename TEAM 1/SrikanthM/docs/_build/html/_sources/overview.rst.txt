Overview
========

Purpose
-------

The pipeline identifies vehicles whose battery state of health (SoH) may need
attention. It assigns each vehicle one of three categories:

* **Healthy**: average SoH is at least 90 percent.
* **Watch**: average SoH is at least 80 percent and below 90 percent.
* **Critical**: average SoH is below 80 percent.

The current implementation runs Apache Spark locally. Amazon S3 stores raw CSV
inputs and curated Parquet output, Athena provides the query layer, and
QuickSight consumes the Athena dashboard view.

Repository map
--------------

.. list-table::
   :header-rows: 1
   :widths: 28 72

   * - Path
     - Responsibility
   * - ``src/battery_health_pipeline.py``
     - Executable end-to-end Spark pipeline and S3 Parquet writer.
   * - ``src/ingestion.py``
     - Reusable local CSV reader.
   * - ``src/transforms.py``
     - Reusable cleaning, enrichment, and summary helpers.
   * - ``src/health_scoring.py``
     - Reusable SoH classification and summary trend helper.
   * - ``src/dashboard_data.py``
     - Reusable charging metrics join for dashboard data.
   * - ``src/athena_queries.py``
     - boto3 Athena query runner.
   * - ``src/generate_battery_data.py``
     - Synthetic telemetry and charging-session generator.
   * - ``sql/athena_setup.sql``
     - Athena database, table, partition repair, and dashboard view.
   * - ``terraform/``
     - S3 bucket security, versioning, and raw CSV uploads.

Important implementation boundaries
-----------------------------------

The main executable contains its own read, cleaning, aggregation, and scoring
logic; it does not currently call every reusable helper module. The checked-in
sample has one telemetry and one charging record per vehicle, so it is useful
for demonstrating the pipeline but does not provide a rich time series.

The curated writer converts the final Spark DataFrame to pandas and replaces
the complete curated S3 prefix on each run. This is appropriate for the sample
size, but it is not a distributed large-volume publishing strategy.
