Infrastructure and Deployment
=============================

The cloud infrastructure for this project is provisioned using Terraform.

Core Resources
--------------

The Terraform configuration creates and manages:

- Amazon S3 bucket for processed datasets
- Athena database
- Athena workgroup
- relevant output values and metadata

S3 Structure
------------

The bucket is structured for both data storage and query output:

.. code-block:: text

   s3://<bucket-name>/
   ├── processed/
   │   ├── maintenance_cleaned.csv
   │   └── maintenance_dealer_joined.csv
   └── athena-results/

Athena configuration
--------------------

The Athena workgroup is configured to write query results to the `athena-results` prefix in S3.
This allows query outputs to be stored in a dedicated location and kept separate from the raw and
processed dataset folders.
