Installation
============

This project uses Python and a local virtual environment for ETL and forecasting work.

Prerequisites
-------------

Before running the project, ensure the following tools are installed:

- Python 3.10 or newer
- pip
- AWS CLI, if uploading files to S3
- Terraform, for infrastructure setup
- Snowflake access credentials
- QuickSight access for dashboard publishing

Local environment setup
-----------------------

It is recommended to use a dedicated virtual environment for the project.

.. code-block:: powershell

   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip

Project dependencies
--------------------

Install the core application dependencies:

.. code-block:: powershell

   pip install pyspark python-dotenv pyarrow pandas pydotenv

For forecast model execution, install the ML stack:

.. code-block:: powershell

   pip install numpy scipy scikit-learn xgboost

Optional developer tooling
--------------------------

For documentation and tests:

.. code-block:: powershell

   pip install pytest sphinx sphinx-rtd-theme

Project execution
-----------------

Run the ETL pipeline from the project directory:

.. code-block:: powershell

   python src\pysparkmodule\utils\etl.py

Run the forecasting workflow separately:

.. code-block:: powershell

   python src\pysparkmodule\forecasting\bmw_sales_forecasting.py

Important note
--------------

The original ETL pipeline remains the source of truth for the cleaned dataset. The forecasting workflow reads from the cleaned Parquet file but does not overwrite the historical ETL output.
