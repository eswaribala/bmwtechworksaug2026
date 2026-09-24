Deployment Runbook
==================

Prerequisites
-------------

* Python 3.10-3.12.
* AWS CLI configured for the deployment account.
* Terraform 1.7+ for infrastructure management.
* A Snowflake account with the required administrative privileges for setup.
* Access to the project S3 bucket.

Phase 1: Python environment
----------------------------

.. code-block:: powershell

   cd C:\path\to\bmw-snowflake-incremental-dw
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   python -m pip install -e ".[dev]"

Phase 2: AWS/Terraform
----------------------

.. code-block:: powershell

   cd terraform
   terraform init
   terraform fmt -recursive
   terraform validate
   terraform plan
   terraform apply

For an existing environment, do not recreate resources blindly. Confirm
Terraform state and AWS resources first.

Phase 3: Python initial upload
------------------------------

.. code-block:: powershell

   cd ..
   python -m python.main --type telemetry --file data/telemetry/telemetry_initial.csv
   python -m python.main --type sales --file data/sales/sales_initial.csv
   python -m python.main --type vehicle --file data/vehicle/vehicle_master.csv
   python -m python.main --type dealer --file data/dealer/dealer_master.csv

Phase 4: Snowflake bootstrap
----------------------------

Run these scripts in order from Snowsight:

.. code-block:: text

   01_database.sql
   02_file_formats.sql
   03_storage_integration.sql
   04_stages.sql
   05_raw_tables.sql
   06_staging_tables.sql
   07_dimensions.sql
   08_facts.sql
   09_initial_load.sql
   10_streams.sql
   11_procedures.sql
   12_tasks.sql
   13_time_travel.sql
   14_zero_copy_clone.sql
   15_analytics.sql
   16_security_grants.sql
   17_health_checks.sql

The key control point is the S3 integration validation before executing the
stage-dependent load.

Phase 5: Incremental demo
--------------------------

1. Capture initial fact counts.
2. Upload incremental telemetry and sales files.
3. Run the incremental ``COPY INTO`` statements in
   ``scripts/run_incremental_load.sql``.
4. Check RAW stream readiness.
5. Execute the Task immediately for a live demonstration or wait for the
   five-minute schedule.
6. Check Task History.
7. Re-run fact counts.
8. Capture before/after screenshots for the evaluation document.

Phase 6: Final verification
----------------------------

Run:

.. code-block:: sql

   SELECT * FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
     SCHEDULED_TIME_RANGE_START => DATEADD('hour', -24, CURRENT_TIMESTAMP())
   ))
   WHERE NAME = 'TASK_INCREMENTAL_PIPELINE'
   ORDER BY SCHEDULED_TIME DESC;

and the object-count checks from ``17_health_checks.sql``.
