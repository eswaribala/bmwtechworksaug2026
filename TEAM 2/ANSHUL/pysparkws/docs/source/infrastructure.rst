Infrastructure and Data Platform
================================

This project uses a combination of AWS, Terraform, and Snowflake to store, stage, and visualize BMW sales data.

AWS S3
------

The raw and processed data are organized under object prefixes such as:

.. code-block:: text

   raw/bmw/
   processed/bmw/

This structure keeps historical and transformed data separated and improves operational clarity.

Terraform
---------

Terraform configuration is used to define and manage:

- the S3 bucket
- storage-related resources
- Snowflake integration-related infrastructure
- IAM and trust configuration for access between AWS and Snowflake

Snowflake
---------

Snowflake is the warehouse layer for:

- loading processed data
- maintaining sales tables
- creating analytic views
- powering QuickSight dashboards

The common pattern is:

1. S3 receives the processed file.
2. Snowflake external stage points to the S3 object key.
3. COPY INTO loads data into Snowflake tables.
4. Views are created for reporting and dashboard consumption.

QuickSight
----------

QuickSight connects to Snowflake using the warehouse and database metadata to build executive and operational dashboards.

The recommended pattern is to expose curated Snowflake views rather than raw tables directly to the BI layer.
