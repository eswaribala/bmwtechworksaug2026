Architecture
============

System Architecture
--------------------

The platform follows a batch data engineering architecture.

::

    BMW CSV Datasets
           |
           v
        S3 Raw
           |
           v
      PySpark ETL
           |
      +----+----+
      |         |
      v         v
   Processed  Rejected
   Parquet    Records
      |
      v
     S3
      |
      v
  Glue Catalog
      |
      v
    Athena
      |
      v
 Business KPIs
      |
      +----------+
      |          |
      v          v
   FastAPI    React
   Backend   Dashboard

Main Components
---------------

PySpark ETL
~~~~~~~~~~~

Responsible for reading datasets, applying schemas, validating records,
removing duplicates, applying business rules, and producing Parquet output.

Amazon S3
~~~~~~~~~

Stores raw, processed, and rejected datasets.

AWS Glue
~~~~~~~~

Provides the Data Catalog used by Athena to discover the processed datasets.

Amazon Athena
~~~~~~~~~~~~~

Provides SQL-based analytics over the curated Parquet datasets.

FastAPI
~~~~~~~

Provides API endpoints for dashboard KPIs and analytical results.

React
~~~~~

Provides the interactive business dashboard.

Docker
~~~~~~

Packages and serves the React frontend through Nginx.

Terraform
~~~~~~~~~

Contains infrastructure configuration for the AWS resources used by the platform.

AWS Account Limitation
----------------------

The BMW training AWS account contains explicit IAM restrictions that prevent
Terraform from managing certain existing AWS resources.

The Terraform configurations were validated using ``terraform validate`` and
``terraform plan``. Affected resources were not force-applied and no AWS
permissions were bypassed.