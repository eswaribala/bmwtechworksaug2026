-- Executive KPI query. Use date filters in QuickSight through ${start_date}/${end_date}.
WITH kpis AS (
  SELECT
    (SELECT COUNT(DISTINCT vehicle_id) FROM bmw_analytics.vehicle_master) AS total_vehicles,
    (SELECT SUM(quantity) FROM bmw_analytics.sales) AS total_sales,
    (SELECT SUM(revenue) FROM bmw_analytics.sales) AS total_revenue,
    (SELECT AVG(battery_level) FROM bmw_analytics.vehicle_telemetry) AS average_battery,
    (SELECT COUNT(*) FROM bmw_analytics.vehicle_telemetry WHERE fault_code IS NOT NULL) AS critical_faults,
    (SELECT SUM(claim_amount) FROM bmw_analytics.warranty) AS warranty_cost,
    (SELECT COUNT(DISTINCT service_id) FROM bmw_analytics.maintenance) AS service_volume
)
SELECT * FROM kpis;

-- Monthly trends
SELECT sale_month AS month, SUM(revenue) AS revenue, SUM(quantity) AS sales
FROM bmw_analytics.sales GROUP BY sale_month ORDER BY month;

SELECT claim_month AS month, SUM(claim_amount) AS warranty_cost
FROM bmw_analytics.warranty GROUP BY claim_month ORDER BY month;

SELECT service_month AS month, COUNT(DISTINCT service_id) AS service_volume
FROM bmw_analytics.maintenance GROUP BY service_month ORDER BY month;

-- Regional analysis
SELECT region, SUM(revenue) AS revenue, SUM(quantity) AS sales
FROM bmw_analytics.sales GROUP BY region ORDER BY revenue DESC;

SELECT vm.region, COUNT(*) AS fault_count
FROM bmw_analytics.vehicle_telemetry vt
JOIN bmw_analytics.vehicle_master vm ON vm.vehicle_id = vt.vehicle_id
WHERE vt.fault_code IS NOT NULL GROUP BY vm.region ORDER BY fault_count DESC;

SELECT vm.region, SUM(w.claim_amount) AS warranty_cost
FROM bmw_analytics.warranty w
JOIN bmw_analytics.vehicle_master vm ON vm.vehicle_id = w.vehicle_id
GROUP BY vm.region ORDER BY warranty_cost DESC;

-- Top models and dealers
SELECT model, SUM(revenue) AS revenue, SUM(quantity) AS sales
FROM bmw_analytics.sales GROUP BY model ORDER BY revenue DESC LIMIT 10;

SELECT dealer_id, SUM(revenue) AS revenue, SUM(quantity) AS sales
FROM bmw_analytics.sales GROUP BY dealer_id ORDER BY revenue DESC LIMIT 10;
