Appendix
========

Snowflake script inventory
--------------------------

.. list-table:: SQL scripts
   :header-rows: 1
   :widths: 25 75

   * - File
     - Responsibility
   * - ``01_database.sql``
     - Database, schemas and warehouse.
   * - ``02_file_formats.sql``
     - CSV parsing definition.
   * - ``03_storage_integration.sql``
     - S3 storage integration.
   * - ``04_stages.sql``
     - External S3 stage.
   * - ``05_raw_tables.sql``
     - RAW source-aligned tables.
   * - ``06_staging_tables.sql``
     - STAGING tables.
   * - ``07_dimensions.sql``
     - Date, region, vehicle and dealer dimensions.
   * - ``08_facts.sql``
     - Telemetry and sales facts.
   * - ``09_initial_load.sql``
     - Initial S3 -> RAW -> STAGING -> ANALYTICS load.
   * - ``10_streams.sql``
     - RAW and STAGING Streams.
   * - ``11_procedures.sql``
     - RAW-to-STAGING, STAGING-to-ANALYTICS and orchestrator procedures.
   * - ``12_tasks.sql``
     - Scheduled incremental Task.
   * - ``13_time_travel.sql``
     - Historical data access example.
   * - ``14_zero_copy_clone.sql``
     - Test/development clone examples.
   * - ``15_analytics.sql``
     - Business-facing views.
   * - ``16_security_grants.sql``
     - Read-only analytics role.
   * - ``17_health_checks.sql``
     - Counts and Task History checks.

Key commands
------------

Initial source upload:

.. code-block:: powershell

   python -m python.main --type telemetry --file data/telemetry/telemetry_initial.csv
   python -m python.main --type sales --file data/sales/sales_initial.csv
   python -m python.main --type vehicle --file data/vehicle/vehicle_master.csv
   python -m python.main --type dealer --file data/dealer/dealer_master.csv

Incremental source upload:

.. code-block:: powershell

   python -m python.main --type telemetry --file data/telemetry/telemetry_incremental.csv
   python -m python.main --type sales --file data/sales/sales_incremental.csv

Core verification:

.. code-block:: sql

   LIST @BMW_DW.RAW.BMW_S3_STAGE;
   SHOW STREAMS IN SCHEMA BMW_DW.RAW;
   SHOW STREAMS IN SCHEMA BMW_DW.STAGING;
   SHOW TASKS IN SCHEMA BMW_DW.ANALYTICS;
   SELECT * FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
     SCHEDULED_TIME_RANGE_START => DATEADD('hour', -1, CURRENT_TIMESTAMP())
   ));

Documentation build
-------------------

The documentation is authored as a native Sphinx project under
``docs/sphinx``. From the project root, after installing Sphinx, build it with:

.. code-block:: powershell

   python -m pip install "Sphinx>=7,<9"
   sphinx-build -b html docs/sphinx docs/_build/html

The resulting site is written to ``docs/_build/html``. Open
``docs/_build/html/index.html`` in a browser.

A minimal Windows workflow is:

.. code-block:: powershell

   cd C:\path\to\bmw-snowflake-incremental-dw
   python -m pip install "Sphinx>=7,<9"
   sphinx-build -b html docs/sphinx docs/_build/html

Submission guidance
-------------------

For the capstone submission, include:

* the GitHub repository;
* this Sphinx documentation source;
* the rendered HTML site or screenshots/PDF export if required;
* the architecture diagram;
* before/after incremental evidence;
* Task History evidence;
* health-check output;
* test output.
