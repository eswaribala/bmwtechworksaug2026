BMW Predictive Maintenance System
==================================

.. toctree::
	:maxdepth: 2
	:caption: Contents:

	introduction
	architecture
	aws_infrastructure
	etl_pipeline
	athena_analytics
	quicksight_dashboard
	results
	conclusion

Overview
--------

The BMW Predictive Maintenance System is an end-to-end data engineering and
analytics solution for identifying vehicles that may require maintenance.

The platform combines historical maintenance records, telemetry data, fault
information, and vehicle attributes to calculate maintenance risk scores. The
results are stored in Amazon S3, queried through Amazon Athena, and visualized
in Amazon QuickSight.

Key technologies include:

* Python
* PySpark
* Terraform
* Amazon S3
* Amazon Athena
* Amazon QuickSight
* Sphinx

Project Outcomes
----------------

The project processed 210 vehicles and generated two curated outputs:

* ``maintenance_risk_score.csv``
* ``top10_risk_vehicles.csv``

The solution classifies vehicles into three risk categories: High, Medium, and
Low. It identifies risk factors including mileage, fault frequency, maintenance
frequency, and temperature trends.
