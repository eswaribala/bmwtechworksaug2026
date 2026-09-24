Recommendation Logic
====================

Overview
--------

The recommendation engine converts the machine learning demand prediction
into an actionable inventory recommendation.

The machine learning model predicts demand, while the recommendation
engine applies business rules to determine how much additional inventory
should be considered.

The overall process is:

.. code-block:: text

   Historical Sales + Inventory
                |
                v
        Feature Engineering
                |
                v
       XGBoost Demand Model
                |
                v
       Predicted Next Month
             Demand
                |
                v
        Target Inventory
                |
                v
      Compare with Current
           Inventory
                |
                v
     Recommended Quantity
                |
                v
          Reason


Input
-----

The recommendation API accepts two inputs:

* Dealer ID
* BMW model

For example:

.. code-block:: json

   {
       "dealer_id": "D001",
       "model": "2 Series"
   }

The recommendation engine then retrieves the latest available historical
information for that dealer and model.


Demand Prediction
-----------------

The trained XGBoost model predicts the expected sales for the following
month.

The prediction is represented as:

``Predicted Next Month Demand``

The prediction is constrained to a non-negative value because vehicle
demand cannot be negative.


Target Inventory
----------------

The system converts predicted demand into a target inventory level.

The current implementation uses a 45-day inventory coverage target.

The calculation is conceptually:

.. code-block:: text

   Target Inventory =
       Predicted Next Month Demand × (45 / 30)


For example, if predicted next-month demand is approximately 20 vehicles:

.. code-block:: text

   Target Inventory = 20 × 45 / 30
                    = 30 vehicles


Recommended Quantity
--------------------

The recommended additional inventory is calculated by comparing target
inventory with current inventory.

The rule is:

.. code-block:: text

   Recommended Quantity =
       max(0, Target Inventory - Current Inventory)


This prevents the system from producing a negative stocking
recommendation.


Example
~~~~~~~

Suppose the system predicts:

.. code-block:: text

   Predicted demand  = 21.44
   Current inventory = 25
   Target inventory  = 32.16

Then:

.. code-block:: text

   Recommended Quantity
       = max(0, 32.16 - 25)
       = 7.16

After rounding:

.. code-block:: text

   Recommended Quantity = 7


Inventory Coverage
------------------

The system also calculates the approximate number of days for which the
current inventory can cover recent demand.

The calculation uses recent monthly sales.

This metric helps explain whether the dealer currently has relatively
high or low inventory coverage.


Sales Trend
-----------

Recent historical sales are used to describe the sales trend.

The recommendation engine compares recent sales information to identify
patterns such as:

* Increasing demand
* Decreasing demand
* Stable demand

The sales trend is included in the final response to make the
recommendation easier to understand.


Reason Generation
-----------------

The recommendation engine generates a human-readable reason based on the
relationship between predicted demand, current inventory, and target
inventory.

The explanation can communicate situations such as:

* Inventory is below the calculated target.
* Inventory is sufficient relative to expected demand.
* Recent sales are increasing.
* Recent sales are decreasing.
* Demand is relatively stable.

This provides an explanation instead of returning only a numerical
recommendation.


Recommendation Output
---------------------

The recommendation engine returns the following information:

.. list-table::
   :header-rows: 1
   :widths: 35 20 45

   * - Field
     - Type
     - Description
   * - ``Dealer``
     - String
     - Dealer identifier.
   * - ``Model``
     - String
     - BMW model.
   * - ``Recommended Quantity``
     - Integer
     - Additional inventory recommended.
   * - ``Predicted Next Month Demand``
     - Numeric
     - Demand predicted by the ML model.
   * - ``Current Inventory``
     - Integer
     - Current inventory level.
   * - ``Target Inventory``
     - Numeric
     - Inventory level calculated from predicted demand.
   * - ``Days of Inventory``
     - Numeric
     - Estimated current inventory coverage.
   * - ``Sales Trend``
     - String
     - Recent demand trend.
   * - ``Reason``
     - String
     - Explanation of the recommendation.


ML and Business Logic Separation
---------------------------------

The system deliberately separates demand prediction from inventory
recommendation.

The machine learning model answers:

.. code-block:: text

   "How many vehicles are expected to be sold next month?"


The recommendation logic answers:

.. code-block:: text

   "Given the predicted demand and current inventory,
    how much additional inventory should be considered?"


This separation makes the system easier to understand, test, and modify.

If the business changes the inventory coverage policy, the recommendation
rules can be modified without retraining the machine learning model.


Error Handling
--------------

The recommendation engine validates the requested dealer and model.

If the dealer does not exist, the system returns an appropriate error.

If the BMW model does not exist, the system returns an appropriate error.

The API layer converts these validation errors into HTTP responses.


Example Recommendation
-----------------------

A simplified example response is:

.. code-block:: json

   {
       "Dealer": "D001",
       "Model": "2 Series",
       "Recommended Quantity": 7,
       "Predicted Next Month Demand": 21.44,
       "Current Inventory": 25,
       "Target Inventory": 32.16,
       "Days of Inventory": 35.71,
       "Sales Trend": "Stable",
       "Reason": "Demand is relatively stable, but current inventory is
                  below the calculated target inventory. Recommend stocking
                  7 additional units."
   }


Business Interpretation
-----------------------

The recommendation should be interpreted as an inventory planning
suggestion based on historical data, predicted demand, and the configured
inventory coverage rule.

It is not a direct replacement for dealer business decisions.

Future Improvements
-------------------

The recommendation logic can be extended with additional business
constraints such as:

* Dealer storage capacity
* Vehicle lead time
* Minimum order quantities
* Maximum inventory limits
* Vehicle availability
* Seasonal campaigns
* Promotions
* Supply constraints
* Dealer-specific stocking policies