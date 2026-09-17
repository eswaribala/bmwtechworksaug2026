Architecture
============

High-level data flow
---------------------

.. code-block:: text

                            BMW DATA SOURCES
                                 |
                                 v
                       +---------------------+
                       |   Incoming Dataset  |
                       | CSV / JSON / etc.   |
                       +----------+----------+
                                  |
                                  v
                       +---------------------+
                       |     Amazon S3       |
                       |      RAW Zone       |
                       +----------+----------+
                                  |
                                  v
                       +---------------------+
                       |   PySpark Engine    |
                       | Validation, Scoring |
                       | Quarantine Routing  |
                       +----------+----------+
                                  |
                    +-------------+-------------+
                    v                           v
          +------------------+        +--------------------+
          |  Curated (valid) |        |  Quarantine (bad)  |
          |     S3 Zone      |        |      S3 Zone        |
          +--------+---------+        +----------------------+
                    |
                    v
          +------------------+
          | AWS Glue Catalog |
          +--------+---------+
                    |
                    v
          +------------------+
          |  Amazon Athena   |
          +------------------+

Components
----------

``src/ingestion``
   Loads raw datasets from S3 or the local filesystem into PySpark
   DataFrames (:mod:`src.ingestion.s3_loader`).

``src/processing``
   Validation rules (:mod:`src.processing.validator`), orchestration
   (:mod:`src.processing.quality_engine`), and quarantine routing
   (:mod:`src.processing.quarantine`).

``src/scoring``
   Computes the 0-100 Data Quality Score
   (:mod:`src.scoring.quality_score`).

``src/reporting``
   Generates the JSON/HTML quality report
   (:mod:`src.reporting.quality_report`).

``src/monitoring``
   Publishes metrics to Amazon CloudWatch
   (:mod:`src.monitoring.cloudwatch_logger`).

``src/utils``
   Shared configuration, logging, and the PySpark session factory.

``backend``
   FastAPI service that bridges the frontend upload UI to the pipeline.

``frontend``
   React/TypeScript single-page app for uploading datasets, viewing
   quality checks, quarantine records, and reports.

``terraform``
   Infrastructure as code for S3, Glue, Athena, CloudWatch, and IAM.

Data Quality checks
--------------------

The engine runs the following checks on every dataset:

- **Schema check** — required columns present.
- **Null check** — missing values in required columns.
- **Duplicate check** — duplicate records by unique key, first occurrence kept.
- **VIN check** — VIN format validation via regex.
- **Date check** — parseable/valid date columns.
- **Range check** — numeric values within configured bounds.
- **Referential integrity check** — foreign keys exist in the reference dataset
  (e.g. ``vehicle_id`` must exist in ``vehicle_master``).

Records that fail any check are routed to quarantine; the remainder are
scored and published as curated data.
