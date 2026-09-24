AWS Cloud Services
==================

Overview
--------

The project uses Amazon Web Services to provide cloud storage and
SQL-based analytical capabilities.

The main AWS services used are:

* Amazon S3
* Amazon Athena

AWS is used to store project data and perform analytical queries over
data stored in S3.


AWS Architecture
----------------

The AWS data flow is:

.. code-block:: text

   Local Project
        |
        | Upload CSV files
        v
   Amazon S3
        |
        | Query data
        v
   Amazon Athena
        |
        v
   Analytical Results


Amazon S3
---------

Amazon S3 is an object storage service used to store raw and processed
project data.

The project uses an S3 bucket named:

.. code-block:: text

   bmw-dealer-inventory-recommendation-2026

The bucket stores data using separate logical folders.


S3 Bucket Structure
~~~~~~~~~~~~~~~~~~~

The logical bucket structure is:

.. code-block:: text

   bmw-dealer-inventory-recommendation-2026/
   |
   +-- raw/
   |     dealer_inventory_features.csv
   |
   +-- processed/
   |     dealer_model_summary.csv
   |
   +-- athena-results/
         Athena query results


Raw Data
~~~~~~~~

The ``raw/`` path contains the historical dealer inventory dataset.

The raw dataset includes:

* Dealer information
* BMW model information
* Region
* Monthly sales
* Inventory levels
* Historical sales fields
* Next-month sales target


Processed Data
~~~~~~~~~~~~~~

The ``processed/`` path contains analytical data generated from the
source dataset.

The processed analytical data includes dealer-model summary information
such as:

* Total sales
* Average sales
* Average inventory
* Number of months


Athena Query Results
~~~~~~~~~~~~~~~~~~~~

The ``athena-results/`` path is used to store the results of Amazon Athena
queries.

This allows Athena to save query output files in Amazon S3.


Amazon Athena
-------------

Amazon Athena is a serverless query service that allows SQL queries to be
executed directly against data stored in Amazon S3.

The project uses Athena to perform dealer-level and model-level
analytics.


Athena Database
~~~~~~~~~~~~~~~

The project uses the following Athena database:

.. code-block:: text

   bmw_inventory


Athena Tables
~~~~~~~~~~~~~

The main tables are:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Table
     - Description
   * - ``dealer_inventory_raw``
     - External table representing the raw dealer inventory dataset.
   * - ``dealer_model_summary``
     - External table containing dealer-model aggregated information.


Raw Athena Table
~~~~~~~~~~~~~~~~

The raw table represents the CSV file stored in the S3 ``raw/`` path.

The main columns include:

* ``dealer_id``
* ``model``
* ``region``
* ``month``
* ``sales``
* ``current_inventory``
* ``previous_month_sales``
* ``inventory_30_days_ago``
* ``next_month_sales``


Analytical Athena Table
~~~~~~~~~~~~~~~~~~~~~~~

The analytical table contains aggregated dealer-model information.

The main columns include:

* ``dealer_id``
* ``model``
* ``region``
* ``total_sales``
* ``average_sales``
* ``average_inventory``
* ``number_of_months``


Example SQL Queries
-------------------

Total Number of Records
~~~~~~~~~~~~~~~~~~~~~~~

The following query checks the number of records in the raw table:

.. code-block:: sql

   SELECT COUNT(*)
   FROM bmw_inventory.dealer_inventory_raw;


Dealer and Model Summary
~~~~~~~~~~~~~~~~~~~~~~~~

The following query retrieves dealer-model summary information:

.. code-block:: sql

   SELECT *
   FROM bmw_inventory.dealer_model_summary
   LIMIT 10;


Total Sales by Model
~~~~~~~~~~~~~~~~~~~~

The following query calculates total sales for each BMW model:

.. code-block:: sql

   SELECT
       model,
       SUM(total_sales) AS model_total_sales
   FROM bmw_inventory.dealer_model_summary
   GROUP BY model
   ORDER BY model_total_sales DESC;


Average Inventory by Region
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following query calculates average inventory by region:

.. code-block:: sql

   SELECT
       region,
       AVG(average_inventory) AS regional_average_inventory
   FROM bmw_inventory.dealer_model_summary
   GROUP BY region
   ORDER BY regional_average_inventory DESC;


Data Quality Checks
-------------------

Athena queries were also used to perform basic data quality checks.

Examples include:

* Counting records
* Checking for null values
* Inspecting dealer-model combinations
* Checking aggregated sales
* Checking average inventory values

These checks help verify that the data was loaded correctly into the
analytical tables.


Security Considerations
-----------------------

The S3 bucket is configured with security-related controls through
Terraform.

The configuration includes:

* S3 bucket versioning
* Server-side encryption using AES256
* Public access blocking

The project does not store AWS access keys, passwords, or other sensitive
credentials in the source code.


AWS CLI Usage
-------------

The AWS CLI was used to interact with AWS resources during development.

Typical activities included:

* Checking AWS identity
* Creating and inspecting S3 resources
* Uploading data files
* Listing S3 objects
* Checking bucket availability
* Working with AWS infrastructure


Project Benefits
----------------

Using S3 and Athena provides the following benefits:

* Cloud-based data storage
* Separation of raw and processed data
* SQL-based analytics
* Serverless querying
* Easy integration with data engineering workflows
* Reproducible analytical queries


Limitations
-----------

The current project uses a synthetic dataset.

The AWS implementation demonstrates the cloud data workflow, but it is
not intended to represent a production BMW data platform.

Future improvements could include:

* AWS Glue Data Catalog
* AWS Glue ETL jobs
* IAM roles with least-privilege permissions
* CloudWatch monitoring
* Automated data uploads
* Scheduled Athena queries
* Data lifecycle policies
* Production data access controls