System Architecture
====================

Architecture Overview
---------------------

The system follows a layered data-processing architecture:

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

Source Layer
------------

CSV files provide vehicle information, historical maintenance records,
telemetry measurements, and fault records.

Validation Layer
----------------

Python validation confirms that files exist, required columns are available,
data types are valid, identifiers are consistent, and missing or duplicate
records are identified before transformation.

Transformation Layer
--------------------

PySpark joins the validated datasets using a common vehicle identifier. It
creates vehicle-level metrics, derives risk indicators, calculates risk
scores, and assigns risk categories.

Curated Storage Layer
---------------------

Amazon S3 stores the analytical outputs:

* ``curated/maintenance_risk_score.csv``
* ``curated/top10_risk_vehicles.csv``

Analytics and Visualization Layers
-----------------------------------

Amazon Athena provides serverless SQL access to the curated S3 data. Amazon
QuickSight connects to the analytical data and presents metrics, charts, and
tables in the BMW Predictive Maintenance Dashboard.

Design Benefits
---------------

This architecture separates ingestion, processing, storage, and reporting. It
also provides repeatable infrastructure, scalable processing, serverless
querying, and self-service business intelligence.
