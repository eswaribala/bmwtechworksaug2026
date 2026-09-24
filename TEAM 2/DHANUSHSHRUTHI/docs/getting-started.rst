Getting started
===============

This guide takes a new operator from a local checkout to a deployed analytics
foundation and a populated Athena score view.

Prerequisites
-------------

You need:

* An AWS account with permissions to create S3, Glue, Athena, and IAM resources.
* AWS CLI credentials configured for the target account.
* Terraform 1.5 or later.
* Python 3.10 or later if you want to run the validation tests.
* Access to Amazon Athena in the configured AWS region.

The deployment uses the AWS ``<region>`` region and the ``<environment>`` environment.
Review :file:`terraform/terraform.tfvars` before deploying.

Install the Python test environment
------------------------------------

From the repository root, create or activate a virtual environment and install
the test dependency:

.. code-block:: powershell

   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install pytest

Validate the local datasets with:

.. code-block:: powershell

   python -m pytest

Deploy with Terraform
---------------------

Run these commands from the repository root:

.. code-block:: powershell

   Set-Location .\terraform
   terraform init
   terraform fmt -check
   terraform validate
   terraform plan -out=tfplan
   terraform apply tfplan

Review the plan before applying it. Terraform creates the S3 bucket, uploads
the four CSV datasets, creates the Glue database and dealer table, configures
the crawler, and creates the Athena workgroup.

S3 bucket names are globally unique. If the requested name is unavailable,
change ``bucket_name`` in ``terraform/terraform.tfvars``. Terraform converts
underscores in that value to hyphens for the actual S3 bucket name.

Inspect deployed names
----------------------

After a successful apply:

.. code-block:: powershell

   terraform output

The outputs include the bucket name, Glue database, crawler, Athena workgroup,
and Athena results location. Use those values when operating the deployment.

Next step
---------

Start the crawler and create the Athena view by following
:doc:`operations`.