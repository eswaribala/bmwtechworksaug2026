Data Model
==========

Dimensional design
------------------

The analytical schema follows a practical star-schema pattern:

.. code-block:: text

                         DIM_DATE
                            |
                            |
   DIM_VEHICLE ------ FACT_SALES ------ DIM_DEALER
         |                  |
         |                  |
         +------------ DIM_REGION

                 DIM_VEHICLE
                      |
                      |
                FACT_TELEMETRY
                      |
                 DIM_REGION
                      |
                   DIM_DATE

Surrogate keys
--------------

Dimensions use surrogate integer keys for analytical joins. Business keys are
kept alongside those surrogate keys, allowing the source identifiers to remain
stable and traceable.

Unknown members
---------------

``DIM_REGION`` creates a default member with surrogate key ``0`` and region
code ``UNKNOWN``. Fact processing uses ``COALESCE(region_key, 0)`` to avoid a
hard load failure when a source record contains an unmapped region.

Fact calculations
-----------------

The telemetry fact derives two operational flags:

* ``BATTERY_ALERT`` when ``BATTERY_LEVEL < 20``.
* ``TEMPERATURE_ALERT`` when ``TEMPERATURE_C > 90``.

The sales fact resolves vehicle, dealer, region and date surrogate keys from
the staging stream before merging the transaction.

Dimension maintenance
---------------------

Vehicle and dealer dimensions are maintained using ``MERGE`` statements. When
a business key already exists, attributes are updated; otherwise a new row is
inserted.

Date dimension
--------------

``DIM_DATE`` is generated using Snowflake's ``GENERATOR`` function so that the
warehouse has a reusable calendar table rather than reconstructing date
attributes in every dashboard query.
