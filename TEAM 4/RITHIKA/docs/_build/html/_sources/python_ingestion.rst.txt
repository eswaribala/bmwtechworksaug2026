Python Ingestion Layer
======================

Responsibilities
----------------

The Python layer prevents malformed data from entering the cloud landing zone
and standardizes source schemas before upload.

``python/main.py``
   CLI entry point. Reads the requested CSV, loads its dataset contract,
runs validation and uploads the normalized file.

``python/schemas.py``
   Data contracts, required columns, key columns and aliases.

``python/canonicalize.py``
   Normalizes field names, resolves aliases, enforces canonical column order,
deduplicates by business key and converts data types.

``python/data_validation.py``
   Validates schema, key presence, duplicates, telemetry ranges and sales
amounts.

``python/s3_ingestion.py``
   Uploads normalized files to the correct S3 raw prefix using boto3.

``python/config.py``
   Loads environment-driven configuration.

``python/logger.py``
   Central logging configuration.

Command examples
-----------------

Initial files:

.. code-block:: powershell

   python -m python.main --type telemetry --file data/telemetry/telemetry_initial.csv
   python -m python.main --type sales --file data/sales/sales_initial.csv
   python -m python.main --type vehicle --file data/vehicle/vehicle_master.csv
   python -m python.main --type dealer --file data/dealer/dealer_master.csv

Incremental files:

.. code-block:: powershell

   python -m python.main --type telemetry --file data/telemetry/telemetry_incremental.csv
   python -m python.main --type sales --file data/sales/sales_incremental.csv

Validation guarantees
---------------------

The ingestion layer rejects:

* missing required columns;
* empty datasets;
* null/blank business keys;
* duplicate business keys in the same source file;
* invalid telemetry latitude/longitude values;
* battery values outside 0-100;
* negative sale amounts.

The data is normalized before it reaches S3, which gives Snowflake a stable
upstream contract.
