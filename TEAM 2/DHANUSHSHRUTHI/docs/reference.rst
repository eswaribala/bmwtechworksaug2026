Reference
=========

Repository layout
-----------------

.. code-block:: text

   dealer_scoreboard_performance/
   |-- datasets/                 Source CSV files
   |-- sql/dealer_score_view.sql Athena view and scoring logic
   |-- terraform/                AWS infrastructure as code
   |-- test/                     Local score and data tests
   |-- docs/                     Sphinx documentation
   |-- README.md                 Short setup guide
   `-- README_ARCHITECTURE.md    Original architecture notes

Common commands
---------------

.. list-table::
   :header-rows: 1
   :widths: 34 66

   * - Command
     - Purpose
   * - ``python -m pytest``
     - Run local data and scoring tests.
   * - ``terraform fmt -check``
     - Check Terraform formatting.
   * - ``terraform validate``
     - Validate Terraform configuration and references.
   * - ``terraform plan -out=tfplan``
     - Preview infrastructure changes and save the plan.
   * - ``terraform output``
     - Display deployed resource names and locations.
   * - ``python -m sphinx -b html docs docs/_build/html``
     - Build this documentation site locally.

Configuration
-------------

Terraform variables are declared in :file:`terraform/variables.tf` and supplied
by :file:`terraform/terraform.tfvars`:

* ``aws_region`` - AWS region for all resources.
* ``project_name`` - prefix for database, crawler, workgroup, role, and tags.
* ``environment`` - environment tag, such as ``dev``.
* ``bucket_name`` - requested S3 name; underscores are normalized to hyphens.
* ``quicksight_role_name`` - reserved optional value for future QuickSight setup.

Documentation development
-------------------------

Sphinx is available in the project virtual environment. Build the HTML output
from the repository root:

.. code-block:: powershell

   python -m sphinx -b html docs docs\_build\html -W

Open ``docs/_build/html/index.html`` after the build completes. The ``-W``
option treats warnings as errors, which keeps broken references from reaching
review.