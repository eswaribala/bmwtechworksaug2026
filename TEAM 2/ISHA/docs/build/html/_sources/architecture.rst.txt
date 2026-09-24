Architecture
============

The project architecture follows a simple end-to-end flow from raw operational data to business insights.

.. code-block:: text

   Maintenance CSV             Dealer CSV
          |                          |
          +-----------+--------------+
                      |
                      v
               PySpark ETL Pipeline
                      |
                      v
          maintenance_cleaned.csv
          maintenance_dealer_joined.csv
                      |
                      v
                 Amazon S3
                      |
                      v
                Amazon Athena
                      |
                      v
             Athena KPI View
                      |
                      v
             Amazon QuickSight
                      |
                      v
             Business Insights

Key Components
--------------

- Data ingestion: dealer and maintenance files
- ETL layer: PySpark transformations and cleaning
- Storage layer: Amazon S3
- Query layer: Amazon Athena
- Visualization layer: Amazon QuickSight
- Infrastructure layer: Terraform
