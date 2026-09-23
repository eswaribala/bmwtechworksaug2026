Architecture
============

The BMW Warranty Claims Analytics project follows an end-to-end data
engineering and analytics architecture.

Architecture Flow
-----------------

The overall data flow is:

::

    Source CSV Files
          |
          v
    Amazon S3 - Raw Data
          |
          v
    PySpark Validation
          |
          +------------------+
          |                  |
          v                  v
    Valid Records      Rejected Records
          |
          v
    PySpark Enrichment
          |
          v
    Amazon S3 - Processed Parquet
          |
          +------------------+
          |                  |
          v                  v
       Athena            Snowflake
                              |
                              v
                         SQL Analytics
                              |
                              v
                         QuickSight
                              |
                              v
                         Dashboard


Main Components
---------------

Amazon S3
~~~~~~~~~

Amazon S3 is used as the project's cloud storage layer.

The data is organized into:

* ``raw/warranty/`` — warranty claim source data.
* ``raw/vehicle_master/`` — vehicle master source data.
* ``processed/warranty_valid/`` — validated warranty claims.
* ``processed/warranty_rejected/`` — rejected records.
* ``processed/warranty_enriched/`` — validated and enriched claims.
* ``athena-results/`` — Amazon Athena query results.

PySpark
~~~~~~~

PySpark is responsible for data processing.

The validation pipeline:

* Reads warranty claims.
* Reads vehicle master data.
* Validates required fields.
* Validates claim dates.
* Validates claim amounts.
* Checks vehicle references.
* Separates valid and rejected records.
* Enriches valid claims with vehicle information.
* Writes processed data as Parquet.

Amazon Athena
~~~~~~~~~~~~~

Amazon Athena provides SQL-based querying over the processed data stored
in Amazon S3.

Snowflake
~~~~~~~~~

Snowflake is used as the analytical data warehouse.

Processed warranty claim data is loaded into Snowflake, where SQL views
are used to calculate warranty analytics and key performance indicators.

Amazon QuickSight
~~~~~~~~~~~~~~~~~

Amazon QuickSight provides the visualization layer.

The dashboard contains metrics such as:

* Total warranty claims.
* Total claim amount.
* Claims by status.
* Claim amount by component.
* Monthly claim amount trends.
* Claims by component.
* Average claim amount by status.
* Monthly claim count trends.

Terraform
~~~~~~~~~

Terraform is used to provision and manage AWS infrastructure as code.

The infrastructure includes resources such as:

* Amazon S3.
* AWS Glue Data Catalog.
* Glue databases.
* Glue tables.
* Supporting AWS configuration required by the analytics pipeline.

Testing
~~~~~~~

Automated testing is performed using pytest.

The test suite covers:

* Warranty claim validation.
* Missing claim IDs.
* Unknown vehicles.
* Negative claim amounts.
* Invalid claim dates.
* Warranty claim enrichment.