-- BMW Enterprise Batch ETL
-- Overall sales KPIs

SELECT
    COUNT(*) AS sales_records,
    SUM(quantity) AS vehicles_sold,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(AVG(revenue), 2) AS average_sale_revenue
FROM bmw_enterprise_etl.sales;