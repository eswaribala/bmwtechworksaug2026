BMW Warranty Claims Analytics
=============================

Welcome to the BMW Warranty Claims Analytics project documentation.

This project provides an end-to-end data analytics pipeline for BMW warranty
claims using AWS, PySpark, SQL, Snowflake, and Amazon QuickSight.

Project Overview
----------------

The pipeline performs the following major tasks:

* Ingests warranty and vehicle data into Amazon S3.
* Validates warranty claim records using PySpark.
* Separates valid and rejected records.
* Enriches warranty claims with vehicle master information.
* Stores processed data in Parquet format.
* Queries processed data using Amazon Athena.
* Loads analytical data into Snowflake.
* Creates analytical views and KPIs using SQL.
* Visualizes warranty claim metrics using Amazon QuickSight.
* Runs automated Python unit tests using pytest.

Documentation
-------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   architecture
   aws_infrastructure
   pyspark
   athena
   snowflake
   quicksight
   testing
   usage

Python API
----------

.. automodule:: src.processing.validate_warranty
   :members:
   :undoc-members:
   :show-inheritance:

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`