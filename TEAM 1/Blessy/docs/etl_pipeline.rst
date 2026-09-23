ETL Pipeline
============

Pipeline Purpose
----------------

The ETL pipeline converts raw vehicle data into a curated maintenance-risk
dataset suitable for reporting and decision-making.

1. Data Validation
------------------

Python validates file availability, required columns, data types, null values,
duplicates, vehicle identifiers, and numeric ranges before Spark processing.

2. Data Loading
---------------

Validated CSV files are loaded into PySpark DataFrames. Explicit schemas are
recommended so identifiers, dates, telemetry, and numeric values are handled
consistently.

3. Data Integration
-------------------

The datasets are joined using a common vehicle identifier. The integrated data
combines vehicle attributes, maintenance history, fault information, and
telemetry measurements.

4. Feature Engineering
----------------------

Vehicle-level features include total mileage, fault count, maintenance count,
temperature trends, and regional attributes.

5. Risk Score Calculation
-------------------------

A conceptual scoring model is:

.. code-block:: text

	risk_score = mileage_component + fault_component
					 + maintenance_component + temperature_component

Components may be normalized or weighted so that the score reflects business
priorities and comparable measurement scales.

6. Risk Categorization
----------------------

Scores are mapped to ``High``, ``Medium``, or ``Low`` risk categories for
operational use.

7. Output Generation
--------------------

The pipeline produces ``maintenance_risk_score.csv`` for vehicle-level
analysis and ``top10_risk_vehicles.csv`` for maintenance prioritization.

8. S3 Publication
-----------------

The outputs are published to the curated S3 layer:

.. code-block:: text

	s3://bmw-maintenance-risk-score-blessy-2026/curated/maintenance_risk_score.csv
	s3://bmw-maintenance-risk-score-blessy-2026/curated/top10_risk_vehicles.csv

Data Quality and Reproducibility
--------------------------------

The pipeline should use deterministic transformations, preserve source data,
validate row counts after joins, check for duplicate vehicle records, compare
output counts with expected totals, and log processing metrics.

Processing Result
-----------------

The completed pipeline processed 210 vehicles and generated the curated
outputs used by Athena and QuickSight.
