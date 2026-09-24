Security and Operations
=======================

Security controls
-----------------

AWS
~~~

* S3 public access is blocked.
* S3 server-side encryption is enabled.
* S3 versioning is enabled.
* Snowflake access is mediated through an IAM role and external ID trust.
* Raw object access is limited to the required prefix.

Snowflake
~~~~~~~~~

* Raw ingestion and analytical access are separated by schema.
* ``BMW_ANALYTICS_READONLY`` provides a least-privilege role for reporting/API
  consumption.
* Stored procedures use ``EXECUTE AS OWNER`` for controlled orchestration.

Secrets
~~~~~~~

Credentials are supplied through environment variables or CI secret stores.
They should never be committed in the Git repository.

Operational checks
------------------

A deployment should verify:

* stage connectivity;
* RAW row counts;
* STAGING row counts;
* dimension counts;
* fact counts;
* stream state;
* task state and recent task history;
* duplicate and null checks;
* analytics view results.

Auditability
------------

The pipeline keeps ``SOURCE_FILE`` and ``LOAD_TS`` in RAW and STAGING, making
it possible to trace records to the S3 object and ingestion timestamp.

Task history can be queried through ``INFORMATION_SCHEMA.TASK_HISTORY``.

Time Travel
-----------

``13_time_travel.sql`` demonstrates historical querying of ``FACT_SALES``.
The feature can be used to compare row counts or inspect a prior table state
within the account's retention window.

Zero-copy cloning
-----------------

``14_zero_copy_clone.sql`` creates a development copy of ``FACT_SALES`` and a
clone of the ANALYTICS schema. This provides a safe place for testing changes
without making a full physical copy of the underlying data.
