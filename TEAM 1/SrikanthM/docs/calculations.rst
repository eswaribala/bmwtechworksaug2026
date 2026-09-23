Calculations and scoring
=========================

Vehicle metrics
---------------

For each ``Vehicle_ID``, telemetry produces:

* average SoC as ``avg_battery_level``;
* average, minimum, maximum, and standard deviation of SoH;
* telemetry record count and first/last observed timestamps.

Charging metrics include session count, average delivered energy, average power,
average duration, and the count of sessions with at least one interruption.

Degradation fields
------------------

Telemetry is ordered by vehicle and timestamp. The pipeline then calculates:

.. math::

   soh\_drop = latest\_soh - initial\_soh

.. math::

   percent\_drop = \frac{latest\_soh - initial\_soh}{initial\_soh} \times 100

Under this formula, a declining battery has a negative ``percent_drop``. For
example, a change from 95 to 88 gives ``soh_drop = -7`` and
``percent_drop = -7.37`` percent.

Classification
--------------

The initial category and score are assigned from ``avg_soh``:

.. list-table::
   :header-rows: 1

   * - Average SoH
     - Category
     - Score
   * - 90 or higher
     - Healthy
     - 100
   * - 80 to less than 90
     - Watch
     - 70
   * - Less than 80
     - Critical
     - 40

The executable then applies the current overrides:

* Healthy with ``percent_drop > 10`` becomes Watch.
* Watch with ``percent_drop > 15`` becomes Critical.

Interpretation warning
----------------------

Because ``percent_drop`` is negative for a decline, the current ``>`` checks
trigger on sufficiently large increases rather than declines. The numeric
``health_score`` is also assigned before category overrides, so an overridden
category may retain its original threshold score. These are documented current
behaviors and should be resolved deliberately if the business rule is changed.

The reusable ``health_scoring`` module applies only the initial SoH thresholds;
it does not apply the executable's degradation override logic.
