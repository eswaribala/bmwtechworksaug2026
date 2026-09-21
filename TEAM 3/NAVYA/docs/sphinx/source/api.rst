Python API Reference
====================

ETL Pipeline
------------

The main ETL pipeline is implemented in:

``src.processing.etl_pipeline``

The pipeline performs:

* Input dataset loading
* Schema enforcement
* Data-quality validation
* Invalid-record rejection
* Deduplication
* Business transformations
* Parquet generation
* Logging

Data Quality Validation
-----------------------

Validation utilities are implemented in:

``src.validation.data_quality``

The validation module provides checks for:

* Null values
* Duplicate keys
* Invalid numeric ranges
* Invalid dates
* Duplicate removal

FastAPI
-------

The backend API is implemented in:

``src.api.main``

Available API areas include:

* Health check
* Overall KPI summary
* Model analytics
* Regional analytics
* Maintenance analytics
* Dealer analytics

Automated Tests
---------------

Automated tests are located in:

``tests/test_etl_pipeline.py``

The project currently contains five automated tests covering:

* Processed vehicle data
* Vehicle ID uniqueness
* Sales revenue calculation
* Positive sales quantity
* Maintenance cost calculation