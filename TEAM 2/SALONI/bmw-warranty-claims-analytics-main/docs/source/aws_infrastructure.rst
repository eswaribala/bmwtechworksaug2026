AWS Infrastructure
===================

The AWS infrastructure for the BMW Warranty Claims Analytics project is
managed using Terraform.

Amazon S3
---------

The project uses Amazon S3 as the primary cloud storage layer.

Bucket
~~~~~~

The project S3 bucket is:

::

    bmw-warranty-claims-532404260630

Raw Data
~~~~~~~~

Raw source files are stored under:

::

    raw/
    ├── warranty/
    │   └── warranty_claims.csv
    │
    └── vehicle_master/
        └── vehicle_master.csv

Processed Data
~~~~~~~~~~~~~~

After PySpark processing, the output is stored as Parquet files:

::

    processed/
    ├── warranty_valid/
    ├── warranty_rejected/
    └── warranty_enriched/

AWS Glue
--------

AWS Glue Data Catalog is used to provide table metadata for the processed
Parquet datasets.

Glue Database
~~~~~~~~~~~~~

The project uses the database:

::

    bmw_warranty_analytics

Glue Tables
~~~~~~~~~~~

The main catalog tables are:

* ``warranty_valid``
* ``warranty_enriched``
* ``warranty_rejected``

Terraform
---------

Terraform is used to create and manage the AWS infrastructure.

The Terraform configuration manages resources including:

* S3 bucket.
* S3 bucket versioning.
* Server-side encryption.
* Public access blocking.
* AWS Glue database.
* AWS Glue tables.
* QuickSight-compatible Glue resources.

Infrastructure Validation
--------------------------

Terraform configuration is validated before deployment using:

::

    terraform validate

The infrastructure state can be checked using:

::

    terraform plan

A successful plan with no pending changes indicates that the deployed
infrastructure matches the Terraform configuration.

Security
--------

The S3 bucket uses server-side encryption and public access blocking.

AWS credentials are provided through the AWS CLI credential configuration
rather than being hard-coded into Python source code.

The PySpark S3A connector uses the AWS SDK's default credential provider
chain to authenticate with Amazon S3.