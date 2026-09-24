AWS Infrastructure
==================

Terraform provisions the core AWS resources and keeps the deployment
repeatable and reviewable.

Amazon S3
---------

Bucket:

.. code-block:: text

	bmw-maintenance-risk-score-blessy-2026

Curated objects:

.. code-block:: text

	curated/maintenance_risk_score.csv
	curated/top10_risk_vehicles.csv

IAM
---

Role: ``bmw-maintenance-role``

CloudWatch
----------

Log group: ``/aws/bmw-maintenance``

Terraform Workflow
------------------

.. code-block:: console

	terraform init
	terraform validate
	terraform plan
	terraform apply

The infrastructure supports the S3 storage, monitoring, and access needs of
the predictive-maintenance workflow.
