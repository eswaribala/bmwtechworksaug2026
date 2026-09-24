-- EV Battery Health Intelligence - Athena alternative
-- Run these statements in the Athena Query Editor.
-- Set the query result location to s3://ev-battery-health-data/athena-results/

CREATE DATABASE IF NOT EXISTS ev_battery_health;

CREATE EXTERNAL TABLE IF NOT EXISTS ev_battery_health.vehicle_health (
    vehicle_id string,
    avg_battery_level double,
    avg_soh double,
    min_soh double,
    max_soh double,
    soh_stddev double,
    telemetry_records bigint,
    first_seen timestamp,
    last_seen timestamp,
    model string,
    variant string,
    model_year int,
    battery_capacity_kwh double,
    battery_type string,
    manufacture_date string,
    region string,
    vehicle_age_years int,
    odometer_km double,
    charging_frequency bigint,
    avg_energy_delivered_kwh double,
    avg_charging_power_kw double,
    avg_charging_duration_min double,
    charging_interruptions_count bigint,
    initial_soh double,
    latest_soh double,
    soh_drop double,
    percent_drop double,
    health_score int
)
PARTITIONED BY (
    battery_health_category string
)
STORED AS PARQUET
LOCATION 's3://ev-battery-health-data/curated/vehicle_health/';

MSCK REPAIR TABLE ev_battery_health.vehicle_health;

SELECT
    battery_health_category,
    COUNT(*) AS vehicle_count
FROM ev_battery_health.vehicle_health
GROUP BY battery_health_category
ORDER BY battery_health_category;

CREATE OR REPLACE VIEW ev_battery_health.vehicle_health_dashboard AS
SELECT
    vehicle_id,
    model,
    variant AS vehicle_variant,
    region,
    vehicle_age_years,
    odometer_km,
    avg_soh,
    min_soh,
    max_soh,
    charging_frequency,
    avg_charging_power_kw,
    charging_interruptions_count,
    soh_drop,
    percent_drop,
    battery_health_category,
    health_score
FROM ev_battery_health.vehicle_health;

SELECT *
FROM ev_battery_health.vehicle_health_dashboard
LIMIT 10;
