QuickSight Dashboard
====================

Dashboard Overview
-------------------

The BMW Predictive Maintenance Dashboard provides an operational view of
vehicle maintenance risk using the curated Athena dataset.

Dashboard Name
--------------

.. code-block:: text

	BMW Predictive Maintenance Dashboard

Dashboard Features
------------------

Total Vehicles Monitored
~~~~~~~~~~~~~~~~~~~~~~~~

Displays the total number of vehicles in the analytical dataset. The completed
project monitors 210 vehicles.

Risk Category Distribution
~~~~~~~~~~~~~~~~~~~~~~~~~~

Shows the count or percentage of High, Medium, and Low risk vehicles.

Top 10 High-Risk Vehicles
~~~~~~~~~~~~~~~~~~~~~~~~~

Lists vehicles with the highest risk scores so service teams can prioritize
urgent reviews.

Average Risk Score by Region
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Compares average risk scores geographically and may reveal differences in
operating conditions, usage, or maintenance practices.

Primary Risk Factors Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Highlights high mileage, frequent faults, frequent maintenance, and temperature
trends as contributors to maintenance risk.

Recommended Dashboard Layout
----------------------------

.. code-block:: text

	Row 1: Total Vehicles | High-Risk Vehicles | Average Risk Score
	Row 2: Risk Category Distribution | Average Risk Score by Region
	Row 3: Top 10 High-Risk Vehicles
	Row 4: Primary Risk Factors Analysis

Useful Filters
--------------

* Risk category
* Region
* Vehicle identifier
* Risk-score range
* Mileage range

Business Usage
--------------

Maintenance managers can identify vehicles requiring review, compare regions,
investigate risk causes, plan preventive work, and monitor fleet risk trends.

Governance
----------

Access should be restricted to authorized users. Dataset refreshes should
follow successful ETL runs, and calculated fields and filters should be
documented and reviewed.
