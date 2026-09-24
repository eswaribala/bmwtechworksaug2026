Architecture
============

End-to-end flow
---------------

.. mermaid::

   flowchart LR
       A[Local CSV files] --> B[Terraform uploads raw CSVs]
       B --> C[S3 raw prefixes]
       C --> D[Local Spark ETL]
       D --> E[Partitioned Parquet]
       E --> F[Athena external table]
       F --> G[Athena dashboard view]
       G --> H[QuickSight SPICE dashboard]

The implementation runs Spark with ``local[*]``. S3 is used for raw inputs,
curated output, and Athena query results; there is no managed Spark cluster in
the current deployment.

Input data
----------

The pipeline consumes three files. Each is read with a header and inferred
schema before the executable applies explicit casts and required-field null
removal.

* ``telemetry.csv``: vehicle ID, timestamp, SoC, SoH, electrical and thermal
  readings, speed, odometer, and a generated source health label.
* ``vehicle_master.csv``: model, variant, model year, battery capacity/type,
  manufacture date, region, age, and odometer.
* ``charging_sessions.csv``: session boundaries, energy, SoC, duration, power,
  charging type, interruptions, and temperatures.

The source ``Health_Category`` field is not used for production classification.
The pipeline derives its own category from measured SoH and degradation fields.

Processing stages
-----------------

#. Read the three inputs from local files or S3.
#. Parse timestamps and cast numeric columns.
#. Drop rows missing the required vehicle ID, timestamps, or SoH values.
#. Aggregate telemetry by ``Vehicle_ID``.
#. Calculate ordered initial/latest SoH and percentage change.
#. Aggregate charging frequency, energy, power, duration, and interruptions.
#. Left-join metrics with vehicle master data.
#. Assign category and score from average SoH, then apply degradation overrides.
#. Optionally replace the curated S3 prefix with partitioned Parquet.

Output contract
---------------

The final Spark DataFrame contains one row per vehicle for the current sample.
Important fields include:

``avg_battery_level``, ``avg_soh``, ``min_soh``, ``max_soh``, ``soh_stddev``,
``telemetry_records``, ``first_seen``, ``last_seen``, vehicle attributes,
``charging_frequency``, ``avg_energy_delivered_kwh``,
``avg_charging_power_kw``, ``avg_charging_duration_min``,
``charging_interruptions_count``, ``initial_soh``, ``latest_soh``, ``soh_drop``,
``percent_drop``, ``battery_health_category``, and ``health_score``.

The writer produces this Hive-style layout::

   s3://ev-battery-health-data/curated/vehicle_health/
     battery_health_category=Healthy/part-00000.parquet
     battery_health_category=Watch/part-00000.parquet
     battery_health_category=Critical/part-00000.parquet

AWS infrastructure
------------------

Terraform creates an S3 bucket with public-access blocking, bucket-owner
object ownership, AES-256 default encryption, versioning, and managed raw CSV
objects. It does not create Athena, Glue Catalog, or QuickSight resources.
Those are configured by ``sql/athena_setup.sql`` and the QuickSight workflow.

Athena creates database ``ev_battery_health``, external table ``vehicle_health``,
and view ``vehicle_health_dashboard``. ``MSCK REPAIR TABLE`` is required after
new category partitions are published.
