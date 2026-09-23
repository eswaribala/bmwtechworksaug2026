Project Requirements
====================

Business Requirements
---------------------

The system is designed to help BMW dealers determine which vehicle models
should be stocked and how much inventory should be maintained.

The system must analyse:

* Model demand
* Recent sales
* Regional demand
* Inventory movement
* Current inventory levels
* Historical sales patterns

Functional Requirements
-----------------------

The application shall:

1. Accept a dealer and BMW model as input.
2. Analyse historical sales and inventory information.
3. Generate features required for demand prediction.
4. Predict next-month demand for the selected dealer and model.
5. Calculate the required target inventory.
6. Calculate the recommended additional inventory quantity.
7. Generate an explanation for the recommendation.
8. Return the recommendation through a REST API.
9. Display the recommendation through the frontend application.

Expected Output
---------------

The recommendation output must contain:

* Dealer
* Model
* Recommended Quantity
* Reason

The application also provides additional information to support the
recommendation:

* Predicted Next Month Demand
* Current Inventory
* Target Inventory
* Days of Inventory
* Sales Trend

Data Requirements
-----------------

The system uses historical dealer-level and model-level information.

The primary dataset contains:

* Dealer identifier
* BMW model
* Region
* Month
* Monthly sales
* Current inventory
* Previous month sales
* Inventory from 30 days ago
* Next-month sales

The synthetic dataset is used for development and testing. It does not
represent actual BMW sales statistics.

Technical Requirements
----------------------

The project uses the following technologies:

Data Engineering
~~~~~~~~~~~~~~~~

* Python
* Pandas
* NumPy
* PySpark

Machine Learning
~~~~~~~~~~~~~~~~

* Scikit-learn
* XGBoost

Application
~~~~~~~~~~~

* FastAPI
* React

Cloud
~~~~~

* AWS S3
* AWS Athena

Infrastructure
~~~~~~~~~~~~~~

* Terraform

Testing
~~~~~~~

* Pytest

CI/CD
~~~~~

* GitHub Actions

Non-Functional Requirements
---------------------------

The system should be:

Scalable
~~~~~~~~

The data processing and feature engineering pipeline should be capable of
handling a larger dealer and vehicle dataset.

Maintainable
~~~~~~~~~~~~

The application is organized into separate modules for data processing,
feature engineering, machine learning, recommendation logic, API services,
and testing.

Testable
~~~~~~~~

The recommendation logic should be covered by automated tests, including
valid and invalid input scenarios.

Secure
~~~~~~

Credentials, passwords, and other sensitive configuration values must not
be stored in the source code or Git repository.

Reproducible
~~~~~~~~~~~~

The project should provide sufficient configuration and documentation for
another developer to understand and run the system.

Observable
~~~~~~~~~~

The application should provide meaningful errors and logging so that
failures can be identified and investigated.

Acceptance Criteria
-------------------

The system is considered functionally complete when it can:

* Accept a valid dealer and model.
* Generate a next-month demand prediction.
* Calculate a recommended inventory quantity.
* Generate a human-readable reason.
* Return the required recommendation fields.
* Reject invalid dealer or model inputs appropriately.
* Pass the automated test suite.
* Validate the Terraform configuration.
* Run through the documented application workflow.