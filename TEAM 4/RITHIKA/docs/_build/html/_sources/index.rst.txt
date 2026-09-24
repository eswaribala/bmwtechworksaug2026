BMW Snowflake Incremental Data Warehouse
========================================

Production-style capstone documentation

.. toctree::
   :maxdepth: 2
   :caption: Project Documentation

   overview
   architecture
   data_pipeline
   aws_terraform
   snowflake_platform
   data_model
   incremental_processing
   python_ingestion
   pyspark_and_api
   testing_ci_cd
   security_operations
   deployment_runbook
   validation_evidence
   troubleshooting
   appendix

Project purpose
---------------

This documentation describes the complete BMW incremental data warehouse
implemented for the capstone project. It explains **what was built**, **why each
layer exists**, **how data moves through the platform**, and **how incremental
processing is demonstrated and verified**.

The core business flow is:

.. code-block:: text

   BMW source CSV files
          |
          v
   Python validation + canonicalization
          |
          v
   AWS S3 raw landing zone
          |
          v
   Snowflake external stage
          |
          v
   RAW tables
          |
          v
   RAW streams (CDC)
          |
          v
   RAW -> STAGING stored procedure
          |
          v
   STAGING tables
          |
          v
   STAGING streams (CDC)
          |
          v
   STAGING -> ANALYTICS stored procedure
          |
          +--------------------+
          |                    |
          v                    v
   Dimensions               Fact tables
          |                    |
          +---------+----------+
                    |
                    v
              Analytics views

Important terminology
---------------------

The project uses an **external Snowflake stage**. The stage is a managed
reference to the S3 location; it does not physically copy S3 objects into a
second storage bucket. Snowflake reads the files through the external stage
and ``COPY INTO`` loads their records into the RAW tables. This distinction is
important when describing the implementation to an evaluator.

Key implementation requirements covered
----------------------------------------

* AWS S3 landing and object organization.
* Snowflake database, warehouse, schemas and external stage.
* RAW, STAGING and ANALYTICS layers.
* Fact tables and dimension tables.
* Snowflake Streams for change data capture.
* Stored procedures for incremental transformations.
* Snowflake Task orchestration.
* Idempotent ``MERGE`` logic using business keys.
* Time Travel example.
* Zero-copy clone example.
* Python source validation and S3 ingestion.
* PySpark batch telemetry processing.
* Read-only FastAPI analytics endpoints.
* Terraform infrastructure definitions.
* Tests and CI/CD configuration.
* Health checks and operational evidence.
