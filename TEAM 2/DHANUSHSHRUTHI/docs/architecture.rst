Architecture
============

System overview
---------------

The project separates infrastructure, raw data, and analytical logic:

.. code-block:: text

   Local CSV files
          |
          v
   Amazon S3: datasets/<dataset>/
          |
          +--> AWS Glue crawler --> sales, service, customer_feedback tables
          |
          +--> Terraform-managed Glue table --> dealer table
                                      |
                                      v
                              Amazon Athena view
                                      |
                                      v
                    Optional Amazon QuickSight dashboard

Athena query results are written to ``athena-results/`` in the same S3 bucket.

AWS components
--------------

.. list-table::
   :header-rows: 1
   :widths: 22 58 20

   * - Component
     - Responsibility
     - Managed by
   * - Amazon S3
     - Stores source CSV files and Athena query results. Public access is blocked and SSE-S3 encryption is enabled.
     - Terraform
   * - AWS Glue database
     - Provides the catalog namespace ``bmw_dealer_score_performace_db``.
     - Terraform
   * - Glue ``dealer`` table
     - Stores the dealer master schema and points to ``datasets/dealer/``.
     - Terraform
   * - Glue crawler
     - Discovers or updates the ``sales``, ``service``, and ``customer_feedback`` tables.
     - Terraform and AWS runtime
   * - Amazon Athena
     - Aggregates source metrics and exposes ``dealer_score_vw``.
     - SQL in this repository
   * - Amazon QuickSight
     - Optional visualization layer consuming the Athena view.
     - Manual setup

Infrastructure behavior
-----------------------

Terraform applies the ``Project``, ``Environment``, and ``ManagedBy`` default
tags. The S3 bucket uses ``force_destroy = false`` so non-empty data is not
silently removed during cleanup. The Glue role has access to the project
bucket, Glue catalog operations, and the Athena query APIs needed by the
workflow.

Repository boundaries
---------------------

* ``datasets/`` contains source CSV files and is uploaded by Terraform.
* ``sql/`` contains the Athena view definition and scoring logic.
* ``terraform/`` contains AWS infrastructure as code and deployment settings.
* ``test/`` validates the score calculation locally against the CSV data.
* ``docs/`` contains this Sphinx documentation.

The Terraform state files are deployment artifacts. Protect them as they may
contain resource metadata and should not be treated as source documentation.