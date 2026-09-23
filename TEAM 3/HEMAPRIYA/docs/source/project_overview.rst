Project Overview
================

Introduction
------------

The BMW Dealer Inventory Recommendation system is designed to recommend
inventory quantities for BMW vehicle models at individual dealerships.

The system analyses historical sales, inventory levels, regional demand,
and recent sales trends to estimate future demand and determine whether
additional inventory should be stocked.

Business Problem
----------------

Dealers need to maintain sufficient vehicle inventory to satisfy expected
customer demand while avoiding unnecessary excess inventory.

The system addresses this problem by combining:

* Historical sales analysis
* Inventory movement analysis
* Regional demand analysis
* Machine learning based demand prediction
* Inventory business rules
* Explainable recommendation generation

Objective
---------

The primary objective is to generate an inventory recommendation for a
given dealer and BMW model.

The expected output contains:

* Dealer
* Model
* Recommended Quantity
* Predicted Next Month Demand
* Current Inventory
* Target Inventory
* Days of Inventory
* Sales Trend
* Reason

Solution Approach
-----------------

The solution follows a data-to-recommendation pipeline:

.. code-block:: text

   Historical Sales + Inventory Data
                |
                v
        Data Processing
                |
                v
        Feature Engineering
                |
                v
       Demand Prediction
                |
                v
       Inventory Business Rules
                |
                v
       Recommendation + Reason

Machine Learning
----------------

Multiple regression models are evaluated for next-month demand prediction:

* Linear Regression
* Random Forest Regressor
* XGBoost Regressor

The models are evaluated using MAE, RMSE, and R-squared on a chronological
test period.

Application
-----------

The prediction and recommendation functionality is exposed through a
FastAPI REST service.

A React frontend provides a user interface where a dealer and BMW model
can be selected and the recommendation can be displayed.

Cloud and Infrastructure
------------------------

AWS S3 is used for cloud data storage and AWS Athena is used for SQL-based
analytical queries.

Terraform is used to define and manage the AWS infrastructure.

Testing and CI/CD
-----------------

The project includes automated unit tests using Pytest and a GitHub Actions
workflow for continuous integration.

The CI workflow validates the Python project, executes tests, and validates
the Terraform configuration.