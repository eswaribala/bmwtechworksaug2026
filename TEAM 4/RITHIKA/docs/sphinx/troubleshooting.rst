Troubleshooting
===============

Snowflake says "table does not exist or not authorized"
--------------------------------------------------------

Check the execution order. Streams on STAGING tables can only be created after
the STAGING tables exist. Run:

.. code-block:: sql

   SHOW TABLES IN SCHEMA BMW_DW.STAGING;

If the schema is empty, execute ``06_staging_tables.sql`` first.

Snowflake says "query produced no results"
-------------------------------------------

This message is normal for DDL/DCL statements such as ``CREATE``, ``ALTER`` and
``USE``. It is also a valid success outcome for a query intentionally expected
to return zero rows, such as a duplicate check. A ``SELECT COUNT(*)`` should,
however, return one row if the table exists and the statement is actually run.

Snowflake cannot assume AWS role
--------------------------------

Start with:

.. code-block:: sql

   DESC STORAGE INTEGRATION BMW_S3_INTEGRATION;

Compare the returned values with the AWS trust policy:

* ``STORAGE_AWS_IAM_USER_ARN`` must equal the role principal.
* ``STORAGE_AWS_EXTERNAL_ID`` must equal the trust-policy external ID.
* ``STORAGE_AWS_ROLE_ARN`` must equal the current AWS role ARN.

Then inspect the role:

.. code-block:: powershell

   aws iam get-role --role-name vrr-snowflake-capstone --no-cli-pager
   aws iam list-attached-role-policies --role-name vrr-snowflake-capstone --no-cli-pager

The trust relationship and the S3 permissions are separate controls.
``sts:AssumeRole`` must be allowed by the trust relationship; S3 permissions
matter only after the role is assumed.

Terraform wants to destroy an existing policy
----------------------------------------------

Do not apply a destructive plan blindly. This usually means the policy exists
in AWS but is no longer represented by the current Terraform configuration or
state. Check:

.. code-block:: powershell

   terraform state list
   terraform plan

If an existing policy should remain managed elsewhere, reference it with a
Terraform data source rather than defining a second managed resource.

COPY INTO reload behavior
-------------------------

Use ``FORCE = FALSE`` and meaningful file patterns. The initial file pattern
and incremental file pattern should be separated so the demo loads the new
objects without duplicating the original batch.

Stream appears empty
--------------------

Streams show changes and are consumed when downstream statements read from the
stream. Check whether a prior procedure/task already consumed the data. For a
clean demo, check stream readiness before executing the Task.

Task does not run
-----------------

New Snowflake Tasks are created suspended. Verify with:

.. code-block:: sql

   SHOW TASKS IN SCHEMA BMW_DW.ANALYTICS;

For an immediate demo, use ``EXECUTE TASK`` after the Task has been configured.
For scheduled operation, resume the task explicitly.
