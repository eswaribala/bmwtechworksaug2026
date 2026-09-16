-- BMW Data Quality & Governance Platform
-- Create Tables SQL (Amazon Athena DDL)
-- Participant 12 | Pod D

-- ═══════════════════════════════════════════════════════════════
-- Create Glue database
-- ═══════════════════════════════════════════════════════════════
CREATE DATABASE IF NOT EXISTS bmw_data_quality
COMMENT 'BMW Data Quality & Governance Platform — Participant 12';

-- ═══════════════════════════════════════════════════════════════
-- Vehicle Master (curated zone)
-- ═══════════════════════════════════════════════════════════════
CREATE EXTERNAL TABLE IF NOT EXISTS bmw_data_quality.bmw_vehicle_master (
    vehicle_id  STRING  COMMENT 'Unique vehicle identifier (e.g. BMW00001)',
    vin         STRING  COMMENT 'Vehicle Identification Number (17 chars)',
    model       STRING  COMMENT 'BMW model name (e.g. 3 Series, iX, X7)',
    model_year  INT     COMMENT 'Model year (e.g. 2025)',
    region      STRING  COMMENT 'Market region',
    status      STRING  COMMENT 'Vehicle status: Active / Inactive'
)
STORED AS PARQUET
LOCATION 's3://bmw-data-quality/curated/vehicle_master/'
TBLPROPERTIES ('parquet.compression'='SNAPPY');

-- ═══════════════════════════════════════════════════════════════
-- Telemetry (curated zone, partitioned by year/month)
-- ═══════════════════════════════════════════════════════════════
CREATE EXTERNAL TABLE IF NOT EXISTS bmw_data_quality.bmw_telemetry (
    event_id      STRING  COMMENT 'Unique telemetry event ID',
    vehicle_id    STRING  COMMENT 'FK → bmw_vehicle_master.vehicle_id',
    vin           STRING  COMMENT 'Vehicle Identification Number',
    timestamp     STRING  COMMENT 'Event timestamp (ISO 8601)',
    battery_level DOUBLE  COMMENT 'Battery charge level (0–100%)',
    speed         DOUBLE  COMMENT 'Vehicle speed (km/h)',
    temperature   DOUBLE  COMMENT 'Ambient temperature (°C)',
    latitude      DOUBLE  COMMENT 'GPS latitude',
    longitude     DOUBLE  COMMENT 'GPS longitude'
)
STORED AS PARQUET
LOCATION 's3://bmw-data-quality/curated/telemetry/'
TBLPROPERTIES ('parquet.compression'='SNAPPY');

-- ═══════════════════════════════════════════════════════════════
-- Data Quality Reports
-- ═══════════════════════════════════════════════════════════════
CREATE EXTERNAL TABLE IF NOT EXISTS bmw_data_quality.data_quality_reports (
    dataset_name               STRING   COMMENT 'Name of the processed dataset',
    execution_timestamp        STRING   COMMENT 'Pipeline execution timestamp',
    total_records              BIGINT   COMMENT 'Total records ingested',
    valid_records              BIGINT   COMMENT 'Records that passed all checks',
    rejected_records           BIGINT   COMMENT 'Records moved to quarantine',
    null_count                 BIGINT   COMMENT 'Null value violations',
    duplicate_count            BIGINT   COMMENT 'Duplicate record violations',
    invalid_vin_count          BIGINT   COMMENT 'Invalid VIN violations',
    invalid_date_count         BIGINT   COMMENT 'Invalid date violations',
    range_violation_count      BIGINT   COMMENT 'Out-of-range value violations',
    referential_error_count    BIGINT   COMMENT 'Referential integrity violations',
    quality_score              DOUBLE   COMMENT 'Data quality score (0–100)',
    score_label                STRING   COMMENT 'Quality label: EXCELLENT/GOOD/ACCEPTABLE/POOR/CRITICAL',
    duration_seconds           DOUBLE   COMMENT 'Pipeline processing duration'
)
STORED AS PARQUET
LOCATION 's3://bmw-data-quality/reports/'
TBLPROPERTIES ('parquet.compression'='SNAPPY');

-- ═══════════════════════════════════════════════════════════════
-- Quarantine (for investigation)
-- ═══════════════════════════════════════════════════════════════
CREATE EXTERNAL TABLE IF NOT EXISTS bmw_data_quality.quarantine_telemetry (
    event_id                    STRING,
    vehicle_id                  STRING,
    vin                         STRING,
    timestamp                   STRING,
    battery_level               DOUBLE,
    speed                       DOUBLE,
    temperature                 DOUBLE,
    quarantine_dataset          STRING,
    quarantine_error_type       STRING,
    quarantine_error_message    STRING,
    quarantine_validation_rule  STRING,
    quarantine_timestamp        STRING
)
STORED AS PARQUET
LOCATION 's3://bmw-data-quality/quarantine/telemetry/'
TBLPROPERTIES ('parquet.compression'='SNAPPY');
