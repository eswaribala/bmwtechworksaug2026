Data Pipeline
=============

Overview
--------

The data pipeline transforms historical dealer inventory data into a
machine-learning-ready dataset and analytical data that can be used for
inventory recommendations.

The pipeline follows:

.. code-block:: text

   Raw CSV
      |
      v
   Data Validation
      |
      v
   Data Cleaning
      |
      v
   Feature Engineering
      |
      v
   Processed Dataset
      |
      +------------------+
      |                  |
      v                  v
   ML Training       AWS S3
                         |
                         v
                     AWS Athena


Source Dataset
--------------

The project uses a synthetic historical dataset generated for development
and testing.

The dataset contains monthly observations for BMW dealers and vehicle
models.

The main fields are:

* ``dealer_id`` - Dealer identifier
* ``model`` - BMW vehicle model
* ``region`` - Dealer region
* ``month`` - Monthly observation date
* ``sales`` - Sales during the month
* ``current_inventory`` - Current inventory level
* ``previous_month_sales`` - Sales from the previous month
* ``inventory_30_days_ago`` - Inventory level approximately 30 days earlier
* ``next_month_sales`` - Target value representing the following month's
  sales

The generated source dataset contains 221,250 usable rows after creating
the next-month sales target.

The data is synthetic and does not represent actual BMW sales data.


Data Generation
---------------

The project includes a Python data-generation script that creates
realistic dealer and vehicle sales patterns.

The generated data includes variation based on:

* Vehicle model
* Dealer
* Region
* Monthly seasonality
* Historical sales
* Inventory levels
* Demand trends

The target variable ``next_month_sales`` is generated from the next
historical sales observation for the same dealer and model.


Data Validation
---------------

Before machine learning, the dataset is checked for data quality.

Validation includes:

* Checking required columns
* Checking missing values
* Converting the ``month`` column to a date format
* Sorting historical records
* Checking dealer-model historical sequences
* Removing records that do not have enough historical information for
  feature generation

Historical Features
-------------------

The feature engineering process uses previous observations to create
historical demand features.

Sales Last Month
~~~~~~~~~~~~~~~~

The previous month's sales are calculated for each dealer and model.

This provides the model with the most recent sales information.

Three-Month Average
~~~~~~~~~~~~~~~~~~~

A rolling three-month sales average is calculated using previous months.

This helps represent short-term demand patterns.

Six-Month Average
~~~~~~~~~~~~~~~~~~

A rolling six-month sales average is calculated using historical sales.

This provides a longer-term view of demand.

Sales Growth
~~~~~~~~~~~~

The one-month sales growth feature measures the change between recent
historical sales values.

It helps identify whether demand is increasing or decreasing.

Regional Model Demand
~~~~~~~~~~~~~~~~~~~~~

Sales are aggregated by region, model, and month.

This provides information about regional demand for individual BMW models.

Inventory Features
-------------------

The pipeline also creates features related to inventory.

Days of Inventory
~~~~~~~~~~~~~~~~~

Days of inventory estimates how many days the current inventory can cover
based on recent sales.

Inventory Turnover
~~~~~~~~~~~~~~~~~~

Inventory turnover measures the relationship between recent sales and
current inventory.

These features help the recommendation system understand whether a dealer
has relatively high or low inventory compared with demand.

Time Features
-------------

Calendar-based features are also created.

These include:

* Month number
* Quarter

These features allow the machine learning model to capture recurring
monthly and quarterly demand patterns.

Categorical Encoding
--------------------

Categorical columns such as dealer, model, and region cannot be directly
used by the regression models.

They are converted into numerical columns using one-hot encoding.

The resulting processed dataset contains the encoded dealer, model, and
region information together with the engineered numerical features.


Processed Dataset
-----------------

After feature engineering and removal of records without sufficient
historical information, the processed dataset contains:

* 198,750 records
* 285 columns in the saved processed dataset
* 283 model input columns

The target variable is:

``next_month_sales``

The ``month`` column is retained separately for chronological train/test
splitting and is not used directly as a model feature.


Chronological Train/Test Split
------------------------------

The machine learning pipeline uses a chronological split instead of a
random split.

Training data covers:

* July 2021 to December 2024

Testing data covers:

* January 2025 to November 2025

This approach prevents future observations from being used to train the
model when evaluating historical demand prediction.


AWS Data Pipeline
-----------------

Processed analytical data is also stored in Amazon S3.

The logical storage structure is:

.. code-block:: text

   S3 Bucket
   |
   +-- raw/
   |     dealer_inventory_features.csv
   |
   +-- processed/
   |     dealer_model_summary.csv
   |
   +-- athena-results/
         Athena query results


AWS S3
~~~~~~

Amazon S3 is used as the cloud storage layer.

The raw dataset is stored under the ``raw/`` path and processed analytical
data is stored under the ``processed/`` path.


AWS Athena
~~~~~~~~~~

Amazon Athena provides SQL-based analysis over the S3 data.

The project uses an Athena database named:

``bmw_inventory``

The main analytical tables are:

* ``dealer_inventory_raw``
* ``dealer_model_summary``


Analytical Aggregation
~~~~~~~~~~~~~~~~~~~~~~

The processed analytical dataset contains dealer and model level
aggregations such as:

* Total sales
* Average sales
* Average inventory
* Number of months

This allows business-level questions to be answered using SQL.


Pipeline Output
---------------

The pipeline produces two important outputs.

Machine Learning Dataset
~~~~~~~~~~~~~~~~~~~~~~~~~

The feature engineering pipeline produces the processed dataset used for
model training.

This dataset contains the engineered historical, demand, inventory, time,
and encoded categorical features.

Analytical Dataset
~~~~~~~~~~~~~~~~~~

The cloud analytics pipeline produces dealer-model summary information
that can be queried through AWS Athena.

The analytical output supports understanding of dealer-level and
model-level demand and inventory patterns.