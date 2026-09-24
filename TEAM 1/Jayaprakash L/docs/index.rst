EV Range & Driving Efficiency Analytics
=======================================

Project documentation
---------------------

This documentation describes the end-to-end EV analytics project:

.. code-block:: text

   CSV
     |
     v
   Python ingestion + validation
     |
     +--------------------------+
     |                          |
     v                          v
   Local pandas path        Amazon S3 raw
     |                          |
     v                          v
   Curated CSV             AWS Glue / PySpark
     |                          |
     v                          v
   FastAPI                S3 curated Parquet
     |                          |
     v                          v
   Streamlit               Glue Catalog
                                |
                                v
                              Athena

The project analyzes EV telemetry to calculate battery consumption,
driving efficiency, estimated range, and aggregate metrics by vehicle,
model, region, and date.

.. toctree::
   :maxdepth: 2
   :caption: Documentation

   architecture
   installation
   pipeline
   api
   aws
   sql
   source_code

Key analytics
-------------

* Vehicle efficiency: total distance divided by positive battery consumed.
* Model efficiency: model-level aggregation of vehicle metrics.
* Region efficiency: region-level aggregation of vehicle metrics.
* Range trend: daily average estimated range.
* Top/bottom vehicles: efficiency-based rankings.

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
