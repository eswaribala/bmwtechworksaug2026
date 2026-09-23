Data pipeline
=============

Input telemetry
---------------

The main dataset is ``data/dataset.csv``. The validation contract expects:

* ``vehicle_id``
* ``model``
* ``region``
* ``timestamp``
* ``speed_kmh``
* ``battery_percent``
* ``distance_km``
* ``temperature_c``
* ``charging``

Transformation logic
---------------------

The reusable Spark transformation is implemented in
``src/pyspark/transform.py``.

1. Remove rows with required null values.
2. Keep non-negative speed.
3. Keep positive distance.
4. Keep battery percentage between 0 and 100.
5. Partition telemetry by vehicle and order it by timestamp.
6. Use ``lag`` to obtain the previous battery reading.
7. Calculate battery consumed.
8. Calculate event efficiency only when battery consumption is positive.
9. Estimate range from current battery percentage and event efficiency.

Efficiency formula
------------------

For an event:

.. math::

   battery\\_consumed = previous\\_battery - current\\_battery

.. math::

   event\\_efficiency =
   \\frac{distance\\_km}{battery\\_consumed}

For vehicle-level analytics:

.. math::

   overall\\_efficiency =
   \\frac{total\\_distance\\_km}{total\\_battery\\_consumed}

Aggregation outputs
-------------------

The pipeline produces:

* ``vehicle_efficiency``
* ``model_efficiency``
* ``region_efficiency``
* ``range_trend``
* ``top_vehicles``
* ``bottom_vehicles``

Spark features demonstrated
---------------------------

The project demonstrates the following data-processing techniques:

* ``dropna`` for null handling.
* ``filter`` for data-quality constraints.
* ``groupBy`` and ``agg`` for analytical summaries.
* Window functions with ``lag`` and ``row_number``.
* Derived columns with Spark SQL functions.
* Caching in the local Spark pipeline.
* Ordering and limiting for rankings.

Local versus Glue
-----------------

``scripts/run_local_pipeline.py`` uses pandas and is convenient for local
API/dashboard development.

``scripts/glue_job.py`` uses AWS Glue and PySpark, writes Parquet to S3,
and is the production-oriented path for the cloud architecture.
