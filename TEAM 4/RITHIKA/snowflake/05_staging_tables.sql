-- ============================================================
-- 05_staging_tables.sql
-- BMW Incremental Data Warehouse
-- Create staging tables from RAW table structures
-- ============================================================

USE DATABASE BMW_DW;

CREATE SCHEMA IF NOT EXISTS STAGING;

USE SCHEMA STAGING;

-- ============================================================
-- 1. TELEMETRY STAGING TABLE
-- ============================================================

CREATE OR REPLACE TABLE STG_TELEMETRY
LIKE BMW_DW.RAW.RAW_TELEMETRY;


-- ============================================================
-- 2. SALES STAGING TABLE
-- ============================================================

CREATE OR REPLACE TABLE STG_SALES
LIKE BMW_DW.RAW.RAW_SALES;


-- ============================================================
-- 3. VEHICLE STAGING TABLE
-- ============================================================

CREATE OR REPLACE TABLE STG_VEHICLE
LIKE BMW_DW.RAW.RAW_VEHICLE;


-- ============================================================
-- 4. DEALER STAGING TABLE
-- ============================================================

CREATE OR REPLACE TABLE STG_DEALER
LIKE BMW_DW.RAW.RAW_DEALER;


-- ============================================================
-- 5. INITIAL LOAD INTO STAGING
-- ============================================================
-- Copy the currently available RAW records into STAGING.
-- The STREAMS should be created AFTER this initial load so
-- the initial records are not treated as incremental changes.

INSERT INTO STG_TELEMETRY
SELECT *
FROM BMW_DW.RAW.RAW_TELEMETRY;

INSERT INTO STG_SALES
SELECT *
FROM BMW_DW.RAW.RAW_SALES;

INSERT INTO STG_VEHICLE
SELECT *
FROM BMW_DW.RAW.RAW_VEHICLE;

INSERT INTO STG_DEALER
SELECT *
FROM BMW_DW.RAW.RAW_DEALER;


-- ============================================================
-- 6. VERIFY STAGING TABLES
-- ============================================================

SELECT 'STG_TELEMETRY' AS TABLE_NAME, COUNT(*) AS ROW_COUNT
FROM STG_TELEMETRY

UNION ALL

SELECT 'STG_SALES', COUNT(*)
FROM STG_SALES

UNION ALL

SELECT 'STG_VEHICLE', COUNT(*)
FROM STG_VEHICLE

UNION ALL

SELECT 'STG_DEALER', COUNT(*)
FROM STG_DEALER;