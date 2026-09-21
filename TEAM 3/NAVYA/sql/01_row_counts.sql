-- BMW Enterprise Batch ETL
-- Athena row-count validation

SELECT
    'vehicle_master' AS dataset,
    COUNT(*) AS row_count
FROM bmw_enterprise_etl.vehicle_master

UNION ALL

SELECT
    'sales' AS dataset,
    COUNT(*) AS row_count
FROM bmw_enterprise_etl.sales

UNION ALL

SELECT
    'maintenance' AS dataset,
    COUNT(*) AS row_count
FROM bmw_enterprise_etl.maintenance

UNION ALL

SELECT
    'dealer' AS dataset,
    COUNT(*) AS row_count
FROM bmw_enterprise_etl.dealer;