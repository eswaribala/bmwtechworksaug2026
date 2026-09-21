-- BMW Enterprise Batch ETL
-- Revenue and vehicle sales by region

SELECT
    region,
    SUM(quantity) AS vehicles_sold,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM bmw_enterprise_etl.sales
GROUP BY region
ORDER BY total_revenue DESC;