Amazon Athena
=============

Amazon Athena is used to query the processed warranty data stored in
Amazon S3 using SQL.

Athena Configuration
--------------------

The project uses the AWS Glue Data Catalog to define the metadata for
the processed Parquet datasets.

Database
~~~~~~~~

The Athena database is:

::

    bmw_warranty_analytics

Region
~~~~~~

Athena is configured in:

::

    eu-north-1

Query Results
~~~~~~~~~~~~~

Athena query results are stored in:

::

    s3://bmw-warranty-claims-532404260630/athena-results/

Main Table
----------

The primary table used for analysis is:

::

    warranty_valid

The table points to the processed Parquet data:

::

    processed/warranty_valid/

Data Analysis
-------------

Athena can be used to calculate basic warranty claim metrics.

Total Claims
~~~~~~~~~~~~

Example query:

::

    SELECT COUNT(*) AS total_claims
    FROM warranty_valid;

The validated dataset currently contains 1,496 warranty claims.

Total Claim Amount
~~~~~~~~~~~~~~~~~~

Example query:

::

    SELECT SUM(claim_amount) AS total_claim_amount
    FROM warranty_valid;

Claims by Component
~~~~~~~~~~~~~~~~~~~

Example query:

::

    SELECT
        component,
        COUNT(*) AS claim_count,
        SUM(claim_amount) AS total_claim_amount
    FROM warranty_valid
    GROUP BY component
    ORDER BY total_claim_amount DESC;

Claims by Status
~~~~~~~~~~~~~~~~

Example query:

::

    SELECT
        claim_status,
        COUNT(*) AS claim_count
    FROM warranty_valid
    GROUP BY claim_status
    ORDER BY claim_count DESC;

Athena CLI
----------

Athena queries can also be executed using the AWS CLI.

Example:

::

    aws athena start-query-execution `
      --query-string "SELECT COUNT(*) AS total_claims FROM warranty_valid;" `
      --query-execution-context Database=bmw_warranty_analytics `
      --result-configuration OutputLocation=s3://bmw-warranty-claims-532404260630/athena-results/ `
      --region eu-north-1

Query Verification
------------------

Query execution can be monitored using:

::

    aws athena get-query-results

Athena provides the SQL query layer between the processed S3 data and
the downstream analytics platforms.