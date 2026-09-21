-- BMW Enterprise Batch ETL
-- Top 10 dealers by revenue

SELECT
    d.dealer_id,
    d.dealer_name,
    d.city,
    d.region,
    SUM(s.quantity) AS vehicles_sold,
    ROUND(SUM(s.revenue), 2) AS total_revenue
FROM bmw_enterprise_etl.sales s
INNER JOIN bmw_enterprise_etl.dealer d
    ON s.dealer_id = d.dealer_id
GROUP BY
    d.dealer_id,
    d.dealer_name,
    d.city,
    d.region
ORDER BY total_revenue DESC
LIMIT 10;