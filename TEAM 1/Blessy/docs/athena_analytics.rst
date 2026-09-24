Athena Analytics
================

Overview
--------

Amazon Athena provides serverless SQL analysis over curated files stored in
Amazon S3. It supports interactive analysis without operating a database
server.

Database and Table
------------------

The project uses database ``bmw_predictive_maintenance`` and table
``maintenance_risk_score``.

Example Table Definition
------------------------

.. code-block:: sql

	CREATE DATABASE IF NOT EXISTS bmw_predictive_maintenance;

	CREATE EXTERNAL TABLE IF NOT EXISTS
	bmw_predictive_maintenance.maintenance_risk_score (
		 vehicle_id string,
		 region string,
		 mileage double,
		 fault_count bigint,
		 maintenance_count bigint,
		 temperature_trend double,
		 risk_score double,
		 risk_category string
	)
	ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
	WITH SERDEPROPERTIES (
		 'separatorChar' = ',',
		 'quoteChar' = '"'
	)
	LOCATION 's3://bmw-maintenance-risk-score-blessy-2026/curated/'
	TBLPROPERTIES ('skip.header.line.count'='1');

Risk Category Distribution
--------------------------

.. code-block:: sql

	SELECT risk_category, COUNT(*) AS vehicle_count
	FROM bmw_predictive_maintenance.maintenance_risk_score
	GROUP BY risk_category
	ORDER BY vehicle_count DESC;

Top Ten High-Risk Vehicles
--------------------------

.. code-block:: sql

	SELECT vehicle_id, region, risk_score, risk_category
	FROM bmw_predictive_maintenance.maintenance_risk_score
	WHERE risk_category = 'High'
	ORDER BY risk_score DESC
	LIMIT 10;

Average Risk by Region
----------------------

.. code-block:: sql

	SELECT region, COUNT(*) AS vehicle_count,
			 AVG(risk_score) AS average_risk_score
	FROM bmw_predictive_maintenance.maintenance_risk_score
	GROUP BY region
	ORDER BY average_risk_score DESC;

Primary Risk Factors
--------------------

.. code-block:: sql

	SELECT AVG(mileage) AS average_mileage,
			 AVG(fault_count) AS average_fault_count,
			 AVG(maintenance_count) AS average_maintenance_count,
			 AVG(temperature_trend) AS average_temperature_trend
	FROM bmw_predictive_maintenance.maintenance_risk_score;

Analytics Benefits
------------------

Athena enables on-demand SQL analysis, direct S3 querying, low operational
overhead, and integration with QuickSight. Parquet, compression, partitioning,
and workgroup controls can improve production performance and cost.
