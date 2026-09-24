Introduction
============

Project Overview
----------------

The BMW Predictive Maintenance System is an end-to-end analytics solution that
converts vehicle, maintenance, fault, and telemetry data into maintenance-risk
classifications for proactive fleet planning.

Business Objective
------------------

* Identify vehicles requiring priority maintenance review.
* Combine operational datasets into a vehicle-level analytical model.
* Classify vehicles as ``High``, ``Medium``, or ``Low`` risk.
* Publish curated results for Athena and QuickSight analysis.
* Support regional comparison and maintenance workload planning.

Technology Stack
----------------

* **Python and PySpark:** Validation, transformation, joins, and risk scoring.
* **Amazon S3:** Curated output storage.
* **Amazon Athena:** SQL analysis of curated data.
* **Amazon QuickSight:** Dashboard reporting and business insights.
* **Terraform:** Repeatable AWS infrastructure provisioning.
* **Sphinx:** Project documentation.
