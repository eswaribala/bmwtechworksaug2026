Operations
==========

Local development
-----------------

From the repository root, disable S3 input and output:

.. code-block:: powershell

   $env:READ_RAW_FROM_S3="false"
   $env:WRITE_CURATED_TO_S3="false"
   python .\src\battery_health_pipeline.py

The script reads ``src/datas``, prints sample rows, and stops its Spark session.

AWS-backed run
--------------

On Windows, configure Hadoop utilities and the Spark Python executables before
running the pipeline:

.. code-block:: powershell

   $env:HADOOP_HOME="C:\Users\<user>\Downloads\hadoop-win-utils"
   $env:hadoop_home_dir=$env:HADOOP_HOME
   $env:PATH="$env:HADOOP_HOME\bin;$env:PATH"
   $env:AWS_REGION="eu-north-1"
   $env:RAW_S3_PATH="s3a://ev-battery-health-data/raw"
   $env:CURATED_S3_PATH="s3a://ev-battery-health-data/curated/vehicle_health"
   $env:WRITE_CURATED_TO_S3="true"
   $env:SPARK_LOCAL_IP="127.0.0.1"
   $env:PYSPARK_PYTHON=(Get-Command python).Source
   $env:PYSPARK_DRIVER_PYTHON=(Get-Command python).Source
   python .\src\battery_health_pipeline.py

Terraform provisioning
----------------------

Run from the ``terraform`` directory:

.. code-block:: powershell

   terraform init
   terraform plan -out tfplan
   terraform apply tfplan

Terraform uploads every ``*.csv`` file in the configured data directory under
its own raw prefix. Verify the bucket name is globally unique and that the AWS
identity can create and manage the resources before applying.

Athena and QuickSight refresh
-----------------------------

Run ``sql/athena_setup.sql`` once in Athena with the query result location set
to the configured Athena results prefix. After each successful pipeline run:

#. Run ``MSCK REPAIR TABLE ev_battery_health.vehicle_health``.
#. Open QuickSight and refresh the SPICE dataset.

QuickSight should use Athena data source ``AwsDataCatalog``, database
``ev_battery_health``, and view ``vehicle_health_dashboard``. Recommended
visuals are health distribution, average SoH by model, regional critical risk,
SoH versus charging frequency, and a vehicle risk table.

Operational limitations
-----------------------

* The writer uses ``toPandas()`` and is intended for the small sample.
* The curated prefix is deleted and recreated on every successful write.
* Athena result pagination is not implemented by ``run_query``.
* There is no automated test suite or full range/duplicate/future-date data
  quality validation in the current repository.
