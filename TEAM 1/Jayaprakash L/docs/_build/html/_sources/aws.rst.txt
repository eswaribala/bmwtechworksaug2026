AWS deployment
==============

Cloud data flow
---------------

.. code-block:: text

   S3 raw
      |
      v
   AWS Glue Spark
      |
      +--> vehicle_efficiency/
      +--> model_efficiency/
      +--> region_efficiency/
      +--> range_trend/
      |
      v
   Glue Crawler / Data Catalog
      |
      v
   Athena
      |
      v
   FastAPI / Dashboard

S3 layout
---------

A recommended object layout is:

.. code-block:: text

   s3://<bucket>/
     raw/
       vehicles/
         dataset.csv
     curated/
       vehicle_efficiency/
       model_efficiency/
       region_efficiency/
       range_trend/
       top_vehicles/
       bottom_vehicles/
     athena-results/

Glue job
--------

The complete AWS Glue source is included below.

.. literalinclude:: ../scripts/glue_job.py
   :language: python
   :linenos:

Terraform
---------

The infrastructure definitions are included directly from the repository.

.. literalinclude:: ../terraform/main.tf
   :language: terraform
   :linenos:

.. literalinclude:: ../terraform/variables.tf
   :language: terraform
   :linenos:

.. literalinclude:: ../terraform/outputs.tf
   :language: terraform
   :linenos:

.. literalinclude:: ../terraform/terraform.tfvars.example
   :language: terraform
   :linenos:

AWS notes
---------

* Ensure the S3 bucket and Athena query-results location are in the same
  AWS region.
* The Glue crawler should target the curated Parquet prefix.
* The Glue service role needs the required S3 and Glue permissions.
* Do not place AWS access keys directly in source code.
