VEHICLE_SALES_QUERY = """
SELECT
    vehicle_id,
    model,
    city,
    sale_date,
    sales_amount,
    quantity
FROM BMW_ANALYTICS.BMW_DATA.BMW_VEHICLE_SALES
"""


WARRANTY_COST_QUERY = """
SELECT
    vehicle_id,
    model,
    city,
    warranty_date,
    fault_type,
    warranty_cost
FROM BMW_ANALYTICS.BMW_DATA.BMW_WARRANTY
"""


FAULT_SUMMARY_QUERY = """
SELECT
    fault_type,
    severity,
    COUNT(*) AS fault_count
FROM BMW_ANALYTICS.BMW_DATA.BMW_FAULTS
GROUP BY
    fault_type,
    severity
ORDER BY
    fault_count DESC
"""


BATTERY_STATUS_QUERY = """
SELECT
    vehicle_id,
    model,
    city,
    battery_date,
    battery_percentage,
    battery_status
FROM BMW_ANALYTICS.BMW_DATA.BMW_BATTERY
"""