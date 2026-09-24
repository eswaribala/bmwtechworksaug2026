AWS Infrastructure
==================

Infrastructure as Code
----------------------

Terraform defines and provisions the core AWS resources, making the
infrastructure repeatable, reviewable, and maintainable across environments.

Amazon S3 Bucket
----------------

The project uses the bucket:

.. code-block:: text

	bmw-maintenance-risk-score-blessy-2026

The bucket stores curated risk-score outputs. Terraform applies the project
and environment tags ``BMW Predictive Maintenance`` and ``Dev``.

Curated objects are stored at:

.. code-block:: text

	curated/maintenance_risk_score.csv
	curated/top10_risk_vehicles.csv

CloudWatch Log Group
--------------------

The log group ``/aws/bmw-maintenance`` is configured with seven days of log
retention to support operational monitoring while controlling storage costs.

IAM Role
--------

The project defines the role ``bmw-maintenance-role``. Its trust policy allows
the Amazon EC2 service to assume the role. Production deployments should add
only the minimum permissions required by the workload.

Example Terraform Workflow
--------------------------

.. code-block:: console

	terraform init
	terraform validate
	terraform plan
	terraform apply

Security Considerations
-----------------------

Recommended production practices include least-privilege IAM policies, S3
encryption, versioning, blocked public access, protected Terraform state,
separate environments, resource tagging, and avoiding credentials in source
code.
