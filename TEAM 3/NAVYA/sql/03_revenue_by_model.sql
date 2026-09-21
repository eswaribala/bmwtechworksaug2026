-- BMW Enterprise Batch ETL
-- Revenue and vehicle sales by BMW model

SELECT
    model,
    SUM(quantity) AS vehicles_sold,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM bmw_enterprise_etl.sales
GROUP BY model
ORDER BY total_revenue DESC;