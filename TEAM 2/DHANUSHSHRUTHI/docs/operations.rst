Operations
==========

Run the Glue crawler
--------------------

The crawler creates or updates the ``sales``, ``service``, and
``customer_feedback`` catalog tables. The ``dealer`` table already exists
because Terraform defines its schema directly.

Use the crawler name from ``terraform output``:

.. code-block:: powershell

   aws glue start-crawler `
    --name <crawler_name> `
    --region <region>

Wait for the crawler to reach ``READY``:

.. code-block:: powershell

   aws glue get-crawler `
    --name <crawler_name> `
    --region <region> `
     --query 'Crawler.State' `
     --output text

Create or refresh the Athena view
---------------------------------

1. Open Athena in the configured AWS region.
2. Select the workgroup from ``terraform output``.
3. Open :file:`sql/dealer_score_view.sql`.
4. Run the complete ``CREATE OR REPLACE VIEW`` statement.
5. Query the view and confirm that results are ranked as expected.

The workgroup enforces the Terraform-configured results location and SSE-S3
encryption. The SQL must be rerun after source schema or scoring changes.

Set up QuickSight (optional)
----------------------------

QuickSight is not provisioned by Terraform. To create a dashboard manually:

1. Create an Athena data source in the same AWS region.
2. Select the deployed workgroup.
3. Select the Glue database and ``dealer_score_vw`` view.
4. Import the view into SPICE or query it directly.
5. Add visuals for score, rank, revenue, service count, rating, and region.

Update source data
------------------

Replace the relevant CSV file in ``datasets/`` and run ``terraform apply`` so
the S3 object is updated. Run the crawler again when a discovered table's
schema or files change, then refresh the Athena view query if the reporting
logic changed.

Destroy the deployment
----------------------

.. warning::

   Destruction removes Terraform-managed cloud infrastructure. Review the
   plan and confirm that the stored data can be removed before continuing.

Because ``force_destroy`` is disabled, remove S3 objects manually if Terraform
reports that the bucket is not empty:

.. code-block:: powershell

   Set-Location .\terraform
   terraform destroy

Troubleshooting checklist
-------------------------

* **Crawler cannot start:** verify the AWS region, crawler name, credentials,
  and IAM permissions.
* **Tables are missing:** wait for the crawler to finish and confirm that each
  expected prefix exists under ``datasets/`` in S3.
* **Athena cannot find a table:** use the deployed Glue database name and run
  the crawler before executing the view SQL.
* **The bucket name is rejected:** choose a globally unique lowercase name;
  Terraform converts underscores to hyphens for S3.
* **Scores differ from local tests:** verify the reporting dates, crawler
  schema, numeric casts, and source files before changing the formula.