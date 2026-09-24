BMW Dealer Scoreboard Performance
=================================

The BMW Dealer Scoreboard Performance project provisions an AWS analytics
foundation for comparing dealer performance. It stores source CSV files in
Amazon S3, catalogs them with AWS Glue, calculates a weighted performance
score in Amazon Athena, and exposes the result through a queryable view for
optional Amazon QuickSight dashboards.

This documentation is written for engineers and operators who need to deploy,
understand, validate, or extend the project.

.. toctree::
   :maxdepth: 2
   :caption: Use the project

   getting-started
   operations

.. toctree::
   :maxdepth: 2
   :caption: Understand the project

   architecture
   data-and-scoring

.. toctree::
   :maxdepth: 2
   :caption: Reference

   reference

Quick links
-----------

* :doc:`getting-started` - prerequisites and the first deployment.
* :doc:`operations` - crawler, Athena, QuickSight, and cleanup procedures.
* :doc:`architecture` - AWS resources and data flow.
* :doc:`data-and-scoring` - input schemas and scoring methodology.
* :doc:`reference` - repository layout, commands, and troubleshooting.

Project status
--------------

The current implementation processes the fixed 2025 reporting period. Replace
the placeholders in the deployment examples with the values from your own
Terraform configuration and outputs.