PySpark Processing
==================

PySpark is the main data processing framework used in the BMW Warranty
Claims Analytics pipeline.

Environment
-----------

The project runs PySpark inside the Python virtual environment:

::

    envwarranty

The project uses:

* Python
* PySpark 4.2.0
* Hadoop AWS
* Amazon S3A connector

Windows Hadoop Configuration
----------------------------

Because the project is developed on Windows, Hadoop Windows utilities are
configured for local Spark execution.

The Hadoop utilities are located at:

::

    C:\hadoop-win-utils

The ``HADOOP_HOME`` environment variable points to this directory.

The ``winutils.exe`` executable is located at:

::

    C:\hadoop-win-utils\bin\winutils.exe

Python Configuration
--------------------

The PySpark driver and worker Python executable are configured using:

::

    $env:PYSPARK_PYTHON
    $env:PYSPARK_DRIVER_PYTHON

S3 Integration
--------------

PySpark accesses Amazon S3 using the S3A filesystem.

The project uses the Hadoop AWS package:

::

    org.apache.hadoop:hadoop-aws:3.5.0

AWS authentication uses the AWS SDK default credential provider chain.

Validation Pipeline
-------------------

The main processing script is:

::

    src\processing\validate_warranty.py

The pipeline performs the following steps.

1. Load Warranty Claims
~~~~~~~~~~~~~~~~~~~~~~~

Warranty claims are read from:

::

    s3a://bmw-warranty-claims-532404260630/raw/warranty/warranty_claims.csv

2. Load Vehicle Master
~~~~~~~~~~~~~~~~~~~~~~

Vehicle master data is read from:

::

    s3a://bmw-warranty-claims-532404260630/raw/vehicle_master/vehicle_master.csv

3. Validate Records
~~~~~~~~~~~~~~~~~~~

Warranty records are checked for:

* Missing claim IDs.
* Invalid claim dates.
* Negative claim amounts.
* Missing vehicle references.

4. Separate Valid and Rejected Records
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Valid records are written to:

::

    processed/warranty_valid/

Rejected records are written to:

::

    processed/warranty_rejected/

Each rejected record contains a rejection reason.

5. Enrich Valid Records
~~~~~~~~~~~~~~~~~~~~~~~

Valid warranty claims are joined with vehicle master information.

The enriched dataset contains vehicle information such as:

* Vehicle ID.
* VIN.
* Model.
* Model year.
* Fuel type.
* Region.

The enriched dataset is written to:

::

    processed/warranty_enriched/

6. Parquet Output
~~~~~~~~~~~~~~~~~

Processed datasets are stored in Apache Parquet format.

Parquet provides a columnar storage format suitable for analytical
workloads.

Running the Pipeline
--------------------

Activate the project environment:

::

    .\envwarranty\Scripts\Activate.ps1

Then run:

::

    python src\processing\validate_warranty.py

Testing Spark
-------------

The local Spark installation can be tested using:

::

    python src\processing\test_spark.py

S3A connectivity can be tested using:

::

    python src\processing\test_s3_spark.py

Expected Processing Results
---------------------------

A successful pipeline run produces three processed datasets:

::

    processed/
    ├── warranty_valid/
    ├── warranty_rejected/
    └── warranty_enriched/

The pipeline logs the number of records loaded, validated, rejected, and
enriched during execution.