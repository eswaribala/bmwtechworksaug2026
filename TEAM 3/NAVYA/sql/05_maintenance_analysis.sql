-- BMW Enterprise Batch ETL
-- Maintenance cost analysis by service type

SELECT
    service_type,
    COUNT(*) AS service_count,
    ROUND(SUM(total_service_cost), 2) AS total_maintenance_cost,
    ROUND(AVG(total_service_cost), 2) AS average_service_cost
FROM bmw_enterprise_etl.maintenance
GROUP BY service_type
ORDER BY total_maintenance_cost DESC;