Analytics and KPIs
==================

The analytics layer uses Amazon Athena SQL queries to derive operational insights from the integrated
maintenance and dealer dataset.

Primary Table
-------------

The main analytics source is:

- maintenance_dealer_joined

Key Performance Indicators
--------------------------

The project calculates the following KPIs:

1. Services per day
2. Average repair cost
3. Average service interval
4. Dealer capacity utilization

Key calculations include:

- counting completed services by day
- calculating average repair cost
- measuring the time gap between service visits
- evaluating service centre utilization against capacity

Dealer Classification Logic
---------------------------

Each dealer is classified according to utilization thresholds:

.. code-block:: sql

   CASE
       WHEN capacity_utilization_pct > 90 THEN 'OVERLOADED'
       WHEN capacity_utilization_pct < 60 THEN 'UNDER_UTILIZED'
       ELSE 'OPTIMAL'
   END

This classification helps the business focus on overloaded service centres and identify underperforming
locations that may require strategic action.
