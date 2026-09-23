Usage
=====

This section describes how to run the BMW Warranty Claims Analytics
pipeline and verify its main components.

Prerequisites
-------------

The project requires:

* Python.
* PySpark.
* Java.
* Hadoop Windows utilities for local Spark execution.
* AWS CLI.
* Terraform.
* Access to the AWS environment.
* Snowflake access.

Activate the Python Environment
-------------------------------

From the project root:

::

    .\envwarranty\Scripts\Activate.ps1

Verify Python:

::

    python --version

Verify PySpark:

::

    python -c "import pyspark; print(pyspark.__version__)"

Spark Verification
------------------

Run the local Spark test:

::

    python src\processing\test_spark.py

The test confirms that the local PySpark environment can create a Spark
session successfully.

S3A Verification
----------------

Run:

::

    python src\processing\test_s3_spark.py

This verifies that PySpark can access the project's Amazon S3 data through
the S3A filesystem.

Run the Validation Pipeline
---------------------------

The main processing pipeline is:

::

    python src\processing\validate_warranty.py

The pipeline reads the raw warranty and vehicle master datasets, validates
the warranty claims, separates rejected records, enriches valid records,
and writes Parquet output to Amazon S3.

Run Automated Tests
-------------------

Execute:

::

    python -m pytest .\tests -v

A successful execution should report:

::

    6 passed

Terraform
---------

Navigate to the Terraform directory:

::

    cd terraform

Validate the configuration:

::

    terraform validate

Preview infrastructure changes:

::

    terraform plan

Apply infrastructure changes:

::

    terraform apply

Return to the project root:

::

    cd ..

AWS CLI
-------

Verify the AWS identity:

::

    aws sts get-caller-identity

Check the S3 bucket:

::

    aws s3 ls s3://bmw-warranty-claims-532404260630/

Athena
------

Athena queries can be executed using the AWS Console or AWS CLI.

Example:

::

    SELECT COUNT(*) AS total_claims
    FROM warranty_valid;

Snowflake
---------

The Snowflake environment contains the processed warranty claims and
analytical SQL views.

The main database and schema are:

::

    BMW_WARRANTY_ANALYTICS.WARRANTY

QuickSight
----------

The QuickSight dashboard provides the visualization layer for the
warranty analytics.

The dashboard can be opened from the Amazon QuickSight console after the
dataset and analysis have been configured.

Typical Workflow
----------------

The recommended project execution flow is:

::

    1. Activate Python environment
              |
              v
    2. Verify Spark
              |
              v
    3. Upload raw data to S3
              |
              v
    4. Run PySpark validation
              |
              v
    5. Verify processed S3 data
              |
              v
    6. Query data using Athena
              |
              v
    7. Load/analyze data in Snowflake
              |
              v
    8. Refresh QuickSight dataset
              |
              v
    9. View QuickSight dashboard
              |
              v
   10. Run automated tests

Notes
-----

AWS credentials should be configured using the AWS CLI credential
mechanism or another supported AWS credential provider.

Credentials must not be hard-coded into project source code.