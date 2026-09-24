System Architecture
====================

Architecture Overview
---------------------

The workflow moves validated CSV data through PySpark processing into AWS
analytics and reporting:

.. code-block:: text

   Vehicle CSV Files
	   |
	   v
   Python Data Validation
	   |
	   v
   PySpark ETL Processing
	   |
	   v
   Risk Score Calculation
	   |
	   v
   Amazon S3 Curated Layer
	   |
	   v
   Amazon Athena
	   |
	   v
   Amazon QuickSight Dashboard

Implementation Flow
-------------------

* **Input:** Vehicle master, maintenance, telemetry, and fault CSV files.
* **Validation:** Python checks file structure, required fields, identifiers,
	nulls, duplicates, and data types.
* **Transformation:** PySpark joins datasets by vehicle identifier and derives
	mileage, fault, maintenance, temperature, and regional metrics.
* **Scoring:** The pipeline calculates a risk score and assigns a risk category.
* **Storage and reporting:** Curated CSV files are published to S3 for Athena
	queries and QuickSight dashboards.

Curated Outputs
---------------

Amazon S3 stores:

* ``curated/maintenance_risk_score.csv``
* ``curated/top10_risk_vehicles.csv``

.. figure:: ../submission_screenshots/03_s3_curated_files.png
	:alt: Curated files stored in Amazon S3
	:width: 800px
	:align: center

	Curated maintenance risk files stored in the Amazon S3 output location.

Infrastructure Evidence
-----------------------

Terraform provisions the S3 bucket, IAM role, and CloudWatch log group used by
the solution.

.. figure:: ../submission_screenshots/05_terraform_resources.png
	:alt: AWS resources provisioned with Terraform
	:width: 800px
	:align: center

	AWS resources provisioned through the project's Terraform configuration.

Review Summary
--------------

The architecture separates validation, transformation, storage, analysis, and
visualization so each stage can be tested and reviewed independently.
