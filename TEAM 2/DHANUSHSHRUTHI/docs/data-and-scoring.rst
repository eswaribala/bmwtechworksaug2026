Data and scoring
================

Reporting period
----------------

The Athena view includes records from ``2025-01-01`` (inclusive) through
``2026-01-01`` (exclusive). The Python tests use the equivalent ``2025-``
filter. Update both implementations when introducing a new reporting year.

Input datasets
--------------

.. list-table::
   :header-rows: 1
   :widths: 22 42 36

   * - Dataset
     - Required columns
     - Purpose
   * - ``dealer.csv``
     - ``dealer_id``, ``dealer_name``, ``region``, ``city``
     - Dealer master data and the base population for ranking.
   * - ``sales.csv``
     - ``sale_id``, ``dealer_id``, ``sale_date``, ``vehicle_model``, ``quantity``, ``unit_price``
     - Revenue contribution, calculated as ``quantity * unit_price``.
   * - ``service.csv``
     - ``service_id``, ``dealer_id``, ``service_date``, ``service_type``, ``service_count``
     - Service activity contribution.
   * - ``customer_feedback.csv``
     - ``feedback_id``, ``dealer_id``, ``feedback_date``, ``rating``, ``feedback_category``
     - Average customer rating contribution.

Calculation steps
-----------------

The view in :file:`sql/dealer_score_view.sql`:

1. Filters each activity dataset to the reporting period.
2. Aggregates revenue, service count, and average rating by ``dealer_id``.
3. Left joins those aggregates to the dealer master, retaining dealers with no activity.
4. Replaces missing metrics with zero.
5. Calculates minimum and maximum values for each metric across all dealers.
6. Min-max normalizes each metric. If all dealers have the same value, that metric receives ``1.0`` for every dealer.
7. Applies the weights: revenue 50%, service count 30%, and rating 20%.
8. Scales the weighted result to 0-100, rounds it to two decimals, and ranks dealers in descending order.

The formula is:

.. math::

   score = 100 \times (0.50 \times revenue_{normalized} + 0.30 \times service_{normalized} + 0.20 \times rating_{normalized})

Output view
-----------

The view is:

.. code-block:: text

  bmw_dealer_score_performace_db.dealer_score_vw

It returns ``dealer_id``, ``dealer_name``, ``region``, ``revenue``,
``service_count``, ``average_rating``, ``dealer_performance_score``, and
``dealer_rank``.

Example query:

.. code-block:: sql

   SELECT *
  FROM bmw_dealer_score_performace_db.dealer_score_vw
   ORDER BY dealer_rank;

Local verification
------------------

The tests independently implement the same aggregation and normalization
logic. They verify the expected dealer population, leading rankings, sample
scores, and aggregate 2025 revenue and service totals.