Project Overview
================

Purpose
-------

The BMW Enterprise Batch ETL platform processes multiple BMW datasets through a
reusable batch data pipeline.

Datasets
--------

The platform processes:

* Vehicle Master
* Sales
* Maintenance
* Dealer

Processing Flow
---------------

The main processing flow is:

::

    CSV
      |
      v
    Validation
      |
      +---- Invalid records --> Rejected
      |
      v
    Transformation
      |
      v
    Parquet
      |
      v
    AWS S3
      |
      v
    AWS Glue Catalog
      |
      v
    Amazon Athena
      |
      v
    Business Analytics

Key Capabilities
----------------

* Schema validation
* Null handling
* Duplicate detection
* Invalid-record rejection
* Business-rule validation
* Parquet conversion
* Region-based sales partitioning
* AWS S3 integration
* AWS Glue Catalog integration
* Amazon Athena analytics
* FastAPI backend
* React dashboard
* Automated testing
* Application logging
* Docker deployment
* GitHub Actions CI/CD
* Terraform infrastructure configuration

Data Quality
------------

The latest local ETL execution produced:

+----------------+-------------+----------+-----------+
| Dataset        | Raw Records | Rejected | Processed |
+----------------+-------------+----------+-----------+
| Vehicle Master | 1,000       | 2        | 997       |
+----------------+-------------+----------+-----------+
| Sales          | 1,000       | 3        | 996       |
+----------------+-------------+----------+-----------+
| Maintenance    | 1,000       | 2        | 997       |
+----------------+-------------+----------+-----------+
| Dealer         | 100         | 2        | 97        |
+----------------+-------------+----------+-----------+

Business KPIs
-------------

Example analytical results include:

* Total revenue: ₹190,171,659.30
* Vehicles sold: 2,007
* Revenue by model
* Revenue by region
* Maintenance cost analysis
* Top dealers by revenue