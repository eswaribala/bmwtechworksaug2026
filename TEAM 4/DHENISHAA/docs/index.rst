BMW Serverless Data Lake Documentation
=======================================

This documentation describes the BMW serverless data lake architecture,
data processing pipeline, AWS infrastructure, and Python implementation.

.. toctree::
   :maxdepth: 2
   :caption: Project Documentation

   01_business_requirements
   02_solution_architecture
   03_data_dictionary
   04_data_flow
   05_terraform_infrastructure
   06_data_processing
   07_athena_queries
   08_lake_formation_governance
   09_quicksight_dashboard
   10_testing_strategy
   11_cicd
   12_troubleshooting
   13_deployment_runbook
   14_demo_script

Python API
==========

Configuration
-------------

.. automodule:: bmw_data_lake.config
   :members:
   :undoc-members:

Data generation
---------------

.. automodule:: bmw_data_lake.data_generator
   :members:
   :undoc-members:

Validation
----------

.. automodule:: bmw_data_lake.validation
   :members:
   :undoc-members:

Transformations and ETL
-----------------------

.. automodule:: bmw_data_lake.transformations
   :members:
   :undoc-members:

.. automodule:: bmw_data_lake.etl
   :members:
   :undoc-members:

Partitioning
------------

.. automodule:: bmw_data_lake.partitioning
   :members:
   :undoc-members:
