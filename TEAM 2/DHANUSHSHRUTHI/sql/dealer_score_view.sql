-- Run this query in Athena after the crawler has created the four catalog tables.
-- The view keeps all scoring logic in Athena for QuickSight consumption.

CREATE OR REPLACE VIEW bmw_dealer_score_performace_db.dealer_score_vw AS
WITH sales_metrics AS (
    SELECT
        dealer_id,
        SUM(CAST(quantity AS DOUBLE) * CAST(unit_price AS DOUBLE)) AS revenue
    FROM bmw_dealer_score_performace_db.sales
        WHERE CAST(sale_date AS DATE) >= DATE '2025-01-01'
            AND CAST(sale_date AS DATE) < DATE '2026-01-01'
    GROUP BY dealer_id
),
service_metrics AS (
    SELECT
        dealer_id,
        SUM(CAST(service_count AS BIGINT)) AS service_count
    FROM bmw_dealer_score_performace_db.service
        WHERE CAST(service_date AS DATE) >= DATE '2025-01-01'
            AND CAST(service_date AS DATE) < DATE '2026-01-01'
    GROUP BY dealer_id
),
feedback_metrics AS (
    SELECT
        dealer_id,
        AVG(CAST(rating AS DOUBLE)) AS average_rating
    FROM bmw_dealer_score_performace_db.customer_feedback
        WHERE CAST(feedback_date AS DATE) >= DATE '2025-01-01'
            AND CAST(feedback_date AS DATE) < DATE '2026-01-01'
    GROUP BY dealer_id
),
dealer_metrics AS (
    SELECT
        d.dealer_id,
        d.dealer_name,
        d.region,
        COALESCE(s.revenue, 0.0) AS revenue,
        COALESCE(sv.service_count, 0) AS service_count,
        COALESCE(f.average_rating, 0.0) AS average_rating
    FROM bmw_dealer_score_performace_db.dealer d
    LEFT JOIN sales_metrics s ON d.dealer_id = s.dealer_id
    LEFT JOIN service_metrics sv ON d.dealer_id = sv.dealer_id
    LEFT JOIN feedback_metrics f ON d.dealer_id = f.dealer_id
),
metric_bounds AS (
    SELECT
        MIN(revenue) AS min_revenue,
        MAX(revenue) AS max_revenue,
        MIN(service_count) AS min_service_count,
        MAX(service_count) AS max_service_count,
        MIN(average_rating) AS min_average_rating,
        MAX(average_rating) AS max_average_rating
    FROM dealer_metrics
),
scored_dealers AS (
    SELECT
        dm.dealer_id,
        dm.dealer_name,
        dm.region,
        dm.revenue,
        dm.service_count,
        dm.average_rating,
        (
            CASE WHEN mb.max_revenue = mb.min_revenue THEN 1.0
                 ELSE (dm.revenue - mb.min_revenue) / (mb.max_revenue - mb.min_revenue)
            END * 0.50
            + CASE WHEN mb.max_service_count = mb.min_service_count THEN 1.0
                   ELSE (dm.service_count - mb.min_service_count) / (mb.max_service_count - mb.min_service_count)
              END * 0.30
            + CASE WHEN mb.max_average_rating = mb.min_average_rating THEN 1.0
                   ELSE (dm.average_rating - mb.min_average_rating) / (mb.max_average_rating - mb.min_average_rating)
              END * 0.20
        ) * 100.0 AS dealer_performance_score
    FROM dealer_metrics dm
    CROSS JOIN metric_bounds mb
)
SELECT
    dealer_id,
    dealer_name,
    region,
    revenue,
    service_count,
    average_rating,
    ROUND(dealer_performance_score, 2) AS dealer_performance_score,
    RANK() OVER (ORDER BY dealer_performance_score DESC) AS dealer_rank
FROM scored_dealers;


