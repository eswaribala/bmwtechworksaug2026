BMW Dealer Inventory Recommendation
===================================

Welcome to the documentation for the BMW Dealer Inventory Recommendation
project.

This project recommends the quantity of BMW vehicle models that dealers
should stock based on historical sales, inventory levels, regional demand,
and predicted future demand.

Project objective
-----------------

The system analyses dealer sales and inventory history to answer:

* Which BMW model should a dealer stock?
* How much inventory should the dealer maintain?
* What is the expected demand for the next month?
* Why is a particular inventory quantity recommended?

The system combines data engineering, machine learning, business rules,
REST APIs, cloud services, infrastructure as code, testing, and CI/CD.

Documentation contents
----------------------

.. toctree::
   :maxdepth: 2
   :caption: Project Documentation

   project_overview
   requirements
   architecture
   data_pipeline
   data_dictionary
   ml_model
   recommendation_logic
   api
   frontend
   aws
   terraform
   testing
   ci_cd
   deployment

Technology stack
----------------

* Python
* Pandas
* NumPy
* PySpark
* Scikit-learn
* XGBoost
* FastAPI
* React
* AWS S3
* AWS Athena
* Terraform
* Pytest
* GitHub Actions

Project structure
-----------------

The project follows a modular structure separating data processing,
machine learning, recommendation logic, API services, infrastructure,
and testing.

.. code-block:: text

   BMW-Dealer-Inventory-Recommendation/
   |
   +-- data/
   +-- src/
   |   +-- features/
   |   +-- models/
   |   +-- recommendation/
   |   +-- api/
   |
   +-- tests/
   +-- terraform/
   +-- frontend/
   +-- docs/
   +-- .github/
   |   +-- workflows/
   +-- requirements.txt

Key capabilities
-----------------

* Historical dealer-model sales analysis
* Inventory movement analysis
* Feature engineering
* Next-month demand prediction
* Machine learning model comparison
* Inventory recommendation
* Explanation generation
* REST API
* React-based user interface
* AWS S3 storage
* AWS Athena analytical queries
* Terraform-managed AWS infrastructure
* Automated testing
* GitHub Actions CI
