Configuration
=============

Python environment
------------------

The project requires Python 3.10 through 3.12. Runtime dependencies are
listed in ``pyproject.toml``: PySpark, pandas, NumPy, PyArrow, boto3, PyAthena,
python-dotenv, matplotlib, and seaborn. Development tools include Black,
isort, and Ruff.

Environment variables
---------------------

.. list-table::
   :header-rows: 1
   :widths: 28 32 40

   * - Variable
     - Default
     - Purpose
   * - ``AWS_REGION``
     - ``eu-north-1``
     - AWS region for boto3 and pipeline clients.
   * - ``READ_RAW_FROM_S3``
     - ``true``
     - Select S3 input when truthy; use local ``data_dir`` otherwise.
   * - ``WRITE_CURATED_TO_S3``
     - ``true``
     - Enable curated Parquet upload.
   * - ``RAW_S3_PATH``
     - ``s3a://ev-battery-health-data/raw``
     - Base path for raw S3 inputs.
   * - ``CURATED_S3_PATH``
     - ``s3a://ev-battery-health-data/curated/vehicle_health``
     - Destination for curated output.
   * - ``ATHENA_DATABASE``
     - ``ev_battery_health``
     - Database used by the Athena helper.
   * - ``ATHENA_OUTPUT_LOCATION``
     - ``s3://ev-battery-health-data/athena-results/``
     - Athena query result location.
   * - ``PYSPARK_PYTHON``
     - Environment default
     - Python executable used by Spark workers.
   * - ``PYSPARK_DRIVER_PYTHON``
     - Environment default
     - Python executable used by the Spark driver.
   * - ``HADOOP_HOME``
     - Not set
     - Windows Hadoop utilities for local Spark execution.

Terraform variables
-------------------

Terraform defaults to region ``eu-north-1``, bucket
``ev-battery-health-data``, and local data directory ``../src/datas`` when run
from ``terraform/``. The example variables file can be copied or supplied with
``-var-file``. AWS credentials are resolved through the standard AWS credential
chain.
