Data Dictionary
===============

Overview
--------

This document describes the main fields used in the BMW Dealer Inventory
Recommendation data pipeline.

The source dataset contains dealer, vehicle, regional, sales, inventory,
and target-demand information.

Source Dataset Fields
---------------------

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Column
     - Data Type
     - Description
   * - ``dealer_id``
     - String
     - Unique identifier for the BMW dealer.
   * - ``model``
     - String
     - BMW vehicle model associated with the record.
   * - ``region``
     - String
     - Geographic or business region associated with the dealer.
   * - ``month``
     - Date
     - Monthly observation date for the dealer-model combination.
   * - ``sales``
     - Integer
     - Number of vehicles sold during the month.
   * - ``current_inventory``
     - Integer
     - Number of vehicles currently available in inventory.
   * - ``previous_month_sales``
     - Integer
     - Sales recorded during the previous month.
   * - ``inventory_30_days_ago``
     - Integer
     - Inventory level approximately 30 days before the current
       observation.
   * - ``next_month_sales``
     - Integer
     - Sales during the following month. This is the target variable
       used for demand prediction.


Engineered Features
-------------------

The feature engineering pipeline creates additional variables from the
historical data.

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Feature
     - Type
     - Description
   * - ``sales_last_month``
     - Numeric
     - Sales from the immediately preceding month for the same dealer
       and model.
   * - ``sales_3_month_avg``
     - Numeric
     - Average sales across the previous three months.
   * - ``sales_6_month_avg``
     - Numeric
     - Average sales across the previous six months.
   * - ``sales_growth_1m``
     - Numeric
     - One-month sales growth based on recent historical sales.
   * - ``regional_model_sales``
     - Numeric
     - Regional demand for a specific BMW model during the corresponding
       month.
   * - ``days_of_inventory``
     - Numeric
     - Estimated number of days that the current inventory can cover
       based on recent sales.
   * - ``inventory_turnover``
     - Numeric
     - Relationship between recent sales and current inventory.
   * - ``month_number``
     - Integer
     - Numerical representation of the calendar month.
   * - ``quarter``
     - Integer
     - Calendar quarter associated with the observation.


Categorical Features
--------------------

The following categorical variables are converted into numerical
representations using one-hot encoding:

* Dealer
* Model
* Region

For example, a model column may be transformed into multiple binary
columns representing the available BMW models.

These encoded columns are used as machine learning input features.


Machine Learning Target
-----------------------

The target variable for the demand prediction model is:

``next_month_sales``

The model learns from historical sales, inventory, regional demand,
time-based, and encoded categorical features to predict the expected
sales for the following month.


Recommendation Output Fields
----------------------------

The recommendation API returns several fields to help explain the
inventory recommendation.

.. list-table::
   :header-rows: 1
   :widths: 35 20 45

   * - Output Field
     - Type
     - Description
   * - ``Dealer``
     - String
     - Dealer identifier.
   * - ``Model``
     - String
     - BMW vehicle model.
   * - ``Recommended Quantity``
     - Integer
     - Additional inventory quantity recommended by the system.
   * - ``Predicted Next Month Demand``
     - Numeric
     - Demand predicted by the machine learning model.
   * - ``Current Inventory``
     - Integer
     - Current inventory available for the dealer and model.
   * - ``Target Inventory``
     - Numeric
     - Inventory level calculated from predicted demand and the inventory
       coverage rule.
   * - ``Days of Inventory``
     - Numeric
     - Estimated current inventory coverage in days.
   * - ``Sales Trend``
     - String
     - Description of the recent sales trend.
   * - ``Reason``
     - String
     - Human-readable explanation of the recommendation.


Analytical Dataset Fields
-------------------------

The AWS Athena analytical table ``dealer_model_summary`` contains
dealer-model level aggregated information.

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Column
     - Data Type
     - Description
   * - ``dealer_id``
     - String
     - Dealer identifier.
   * - ``model``
     - String
     - BMW vehicle model.
   * - ``region``
     - String
     - Dealer region.
   * - ``total_sales``
     - Integer
     - Total sales for the dealer-model combination.
   * - ``average_sales``
     - Double
     - Average monthly sales.
   * - ``average_inventory``
     - Double
     - Average inventory level.
   * - ``number_of_months``
     - Integer
     - Number of monthly observations represented by the aggregation.