ETL Pipeline
============

The pipeline converts raw vehicle data into curated maintenance-risk outputs.

Input Datasets
--------------

* Vehicle master data
* Historical maintenance records
* Telemetry measurements
* Fault records

Processing Steps
----------------

* **Validation:** Check file availability, required columns, data types, nulls,
  duplicates, identifiers, and numeric ranges.
* **Loading:** Read validated CSV files into PySpark DataFrames.
* **Integration:** Join datasets using the common vehicle identifier.
* **Feature engineering:** Derive mileage, fault count, maintenance count,
  temperature trend, and regional attributes.
* **Risk scoring:** Combine the indicators into a vehicle-level risk score.
* **Categorization:** Map scores to ``High``, ``Medium``, or ``Low`` risk.

Output Files
------------

* ``maintenance_risk_score.csv`` for vehicle-level analysis.
* ``top10_risk_vehicles.csv`` for maintenance prioritization.

S3 Publication
--------------

The outputs are published to the curated S3 layer:

.. code-block:: text

	s3://bmw-maintenance-risk-score-blessy-2026/curated/maintenance_risk_score.csv
	s3://bmw-maintenance-risk-score-blessy-2026/curated/top10_risk_vehicles.csv

Processing Result
-----------------

The completed pipeline processed 210 vehicles and generated the curated
outputs used by Athena and QuickSight.
