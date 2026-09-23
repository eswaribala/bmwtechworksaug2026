Results and Business Insights
=============================

Processing Results
------------------

The completed solution processed 210 vehicles and generated curated analytical
outputs for reporting.

Generated Files
---------------

.. code-block:: text

	 maintenance_risk_score.csv
	 top10_risk_vehicles.csv

The files were uploaded to the curated S3 layer and made available to Athena
and QuickSight.

Risk Categories
---------------

Vehicles are classified as High, Medium, or Low risk. This converts technical
measurements into an operational prioritization framework.

Business Insights
-----------------

* **Maintenance prioritization:** High-risk vehicles can be reviewed first.
* **Reliability monitoring:** Frequent faults and repeated maintenance can
	reveal recurring problems.
* **Usage and wear analysis:** High mileage can indicate accumulated wear.
* **Operating-condition monitoring:** Temperature trends can highlight abnormal
	conditions.
* **Regional comparison:** Average regional risk can support resource planning.

Decision Support
----------------

The system moves maintenance analysis from a purely reactive process toward a
risk-based process. Teams can focus attention on vehicles most likely to need
intervention instead of treating all vehicles equally.

Interpretation Considerations
-----------------------------

Risk scores are decision-support indicators, not guaranteed failure
predictions. They should be considered alongside engineering judgment,
inspection results, vehicle age, operating conditions, and service history.
