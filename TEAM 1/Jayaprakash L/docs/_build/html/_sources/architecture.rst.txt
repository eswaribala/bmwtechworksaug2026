Architecture
============

Overview
--------

The application has two execution paths.

Local development
~~~~~~~~~~~~~~~~~

The local path is intentionally simple:

.. code-block:: text

   data/dataset.csv
        |
        v
   src.ingestion
        |
        v
   src.validation
        |
        +----------------------+
        |                      |
        v                      v
   pandas pipeline        PySpark pipeline
        |                      |
        v                      v
   data/curated_local      Parquet
        |                      |
        +----------+-----------+
                   |
                   v
              FastAPI
                   |
                   v
              Streamlit

AWS production path
~~~~~~~~~~~~~~~~~~~

The AWS path follows the project's data-lake architecture:

.. code-block:: text

   Raw CSV
     |
     v
   Amazon S3 /raw/
     |
     v
   AWS Glue Spark job
     |
     v
   Amazon S3 /curated/
     |
     v
   AWS Glue Data Catalog
     |
     v
   Amazon Athena
     |
     v
   FastAPI / query layer
     |
     v
   Streamlit dashboard

Main components
---------------

* **Python/pandas** - lightweight local ingestion and API data preparation.
* **PySpark** - distributed-style transformation and aggregation logic.
* **Amazon S3** - raw and curated object storage.
* **AWS Glue** - managed Spark execution and table cataloging.
* **Amazon Athena** - SQL query layer over curated Parquet.
* **FastAPI** - REST interface for analytics.
* **Streamlit** - interactive analytics dashboard.
* **Terraform** - infrastructure-as-code for AWS resources.

Source locations
----------------

* ``src/ingestion/`` - CSV and S3 ingestion.
* ``src/validation/`` - schema and basic data validation.
* ``src/pyspark/`` - reusable Spark transformations and analytics.
* ``src/api/`` - FastAPI routes and local query functions.
* ``src/dashboard/`` - Streamlit application.
* ``scripts/glue_job.py`` - AWS Glue implementation.
* ``terraform/`` - infrastructure definitions.
* ``sql/`` - Athena-oriented analytical SQL.
