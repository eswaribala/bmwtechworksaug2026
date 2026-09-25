CREATE OR REPLACE VIEW bmw_analytics.vw_executive_kpis AS
WITH sales_by_region AS (
  SELECT sale_month, region, SUM(revenue) AS revenue, SUM(quantity) AS sales,
         COUNT(DISTINCT vehicle_id) AS vehicles_sold
  FROM bmw_analytics.sales
  GROUP BY sale_month, region
), telemetry_by_region AS (
  SELECT vm.region, AVG(t.battery_level) AS average_battery,
         COUNT(CASE WHEN t.fault_code IS NOT NULL THEN 1 END) AS critical_faults
  FROM bmw_analytics.vehicle_telemetry t
  JOIN bmw_analytics.vehicle_master vm ON vm.vehicle_id = t.vehicle_id
  GROUP BY vm.region
), warranty_by_region AS (
  SELECT vm.region, SUM(w.claim_amount) AS warranty_cost
  FROM bmw_analytics.warranty w
  JOIN bmw_analytics.vehicle_master vm ON vm.vehicle_id = w.vehicle_id
  GROUP BY vm.region
), maintenance_by_region AS (
  SELECT vm.region, COUNT(DISTINCT m.service_id) AS service_volume
  FROM bmw_analytics.maintenance m
  JOIN bmw_analytics.vehicle_master vm ON vm.vehicle_id = m.vehicle_id
  GROUP BY vm.region
)
SELECT s.sale_month, s.region, s.revenue, s.sales, s.vehicles_sold,
       t.average_battery, t.critical_faults,
       COALESCE(w.warranty_cost, 0) AS warranty_cost,
       COALESCE(m.service_volume, 0) AS service_volume
FROM sales_by_region s
LEFT JOIN telemetry_by_region t ON t.region = s.region
LEFT JOIN warranty_by_region w ON w.region = s.region
LEFT JOIN maintenance_by_region m ON m.region = s.region;
