System Architecture
===================

Overview
--------

The BMW Dealer Inventory Recommendation system follows a layered data
engineering and machine learning architecture.

The overall flow is:

.. code-block:: text

   Historical Data
         |
         v
   Data Ingestion
         |
         v
   Data Validation
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
   Inventory Recommendation
         |
         v
   FastAPI
         |
         v
   React Frontend


Architecture Components
-----------------------

Data Source
~~~~~~~~~~~

The project uses a synthetic historical dataset containing dealer,
vehicle-model, sales, regional, and inventory information.

The dataset represents monthly observations for multiple dealers and BMW
vehicle models.

Data Ingestion
~~~~~~~~~~~~~~

Python-based ingestion is used to load the source CSV data into the
application pipeline.

The ingestion layer provides the initial dataset for processing and
analysis.

Data Processing
~~~~~~~~~~~~~~~

The processing layer prepares the raw data for analysis.

Major operations include:

* Data type conversion
* Sorting historical records
* Handling missing values
* Creating historical sales features
* Calculating inventory-related features
* Preparing model input data

Feature Engineering
~~~~~~~~~~~~~~~~~~~

Historical sales and inventory information is transformed into features
that can be used by the machine learning models.

Examples include:

* Previous month sales
* Three-month average sales
* Six-month average sales
* One-month sales growth
* Regional model sales
* Days of inventory
* Inventory turnover
* Month number
* Quarter

Categorical variables such as dealer, model, and region are converted into
machine-learning-compatible numerical representations.

Machine Learning Layer
~~~~~~~~~~~~~~~~~~~~~~

The machine learning layer predicts the expected sales for the following
month.

The project evaluates:

* Linear Regression
* Random Forest Regressor
* XGBoost Regressor

The models are evaluated using:

* Mean Absolute Error (MAE)
* Root Mean Squared Error (RMSE)
* R-squared

The model evaluation uses a chronological train/test split so that future
data is not used to train the model.

Recommendation Layer
~~~~~~~~~~~~~~~~~~~~

The recommendation layer converts predicted demand into an inventory
recommendation.

The process considers:

* Predicted next-month demand
* Current inventory
* Target inventory
* Historical sales trend
* Inventory coverage

The final recommendation is the additional quantity that should be
considered for stocking.

Reason Generation
~~~~~~~~~~~~~~~~~

The system also generates a human-readable explanation for the
recommendation.

The reason considers demand trends and the relationship between current
inventory and the calculated target inventory.

Application Layer
~~~~~~~~~~~~~~~~~

FastAPI exposes the recommendation functionality through REST endpoints.

The main endpoints are:

.. code-block:: text

   GET  /health
   GET  /options
   POST /recommend

The ``/options`` endpoint provides available dealers and BMW models.

The ``/recommend`` endpoint accepts a dealer and model and returns the
inventory recommendation.

Frontend Layer
~~~~~~~~~~~~~~

A React frontend provides the user interface.

The user can select:

* Dealer
* BMW model

The frontend sends the selected values to the FastAPI backend and displays
the recommendation and supporting information.

Cloud Layer
~~~~~~~~~~~

AWS services are used as part of the data platform.

AWS S3
^^^^^^

Amazon S3 provides cloud storage for raw and processed project data.

The project uses separate logical paths for:

* Raw data
* Processed data
* Athena query results

AWS Athena
^^^^^^^^^^

Amazon Athena provides SQL-based analysis over the data stored in S3.

It is used to query dealer and model-level analytical information without
requiring a separate database server.

Infrastructure as Code
~~~~~~~~~~~~~~~~~~~~~~

Terraform is used to define and manage the AWS infrastructure.

The current Terraform configuration manages the S3 bucket and its
security-related configuration, including:

* Bucket versioning
* Server-side encryption
* Public access blocking

CI/CD
~~~~~

GitHub Actions is used for continuous integration.

The CI workflow performs:

* Python dependency installation
* Automated tests
* Terraform initialization
* Terraform validation
* Terraform formatting validation

Architecture Data Flow
----------------------

The complete system flow can be represented as:

.. code-block:: text

   CSV Dataset
       |
       v
   Python / PySpark
       |
       v
   Data Validation
       |
       v
   Feature Engineering
       |
       v
   ML Model
       |
       |  Predicted Demand
       v
   Recommendation Engine
       |
       |  Recommended Quantity + Reason
       v
   FastAPI
       |
       v
   React Frontend


Separation of Responsibilities
------------------------------

The project separates different responsibilities into independent modules.

.. code-block:: text

   src/
   |
   +-- ingestion/
   |       Data loading
   |
   +-- processing/
   |       Data transformation
   |
   +-- features/
   |       Feature engineering
   |
   +-- models/
   |       Model training
   |
   +-- recommendation/
   |       Inventory recommendation
   |
   +-- api/
           FastAPI service

This modular structure makes the application easier to test, maintain,
and extend.

Technology Flow
---------------

The major technologies and their responsibilities are:

.. list-table::
   :header-rows: 1
   :widths: 25 45

   * - Technology
     - Responsibility
   * - Python
     - Application and data processing
   * - Pandas
     - Dataset manipulation
   * - PySpark
     - Distributed data processing
   * - Scikit-learn
     - Machine learning models and evaluation
   * - XGBoost
     - Gradient boosting demand prediction
   * - FastAPI
     - REST API
   * - React
     - User interface
   * - AWS S3
     - Cloud data storage
   * - AWS Athena
     - SQL analytics
   * - Terraform
     - Infrastructure as Code
   * - Pytest
     - Automated testing
   * - GitHub Actions
     - Continuous integration