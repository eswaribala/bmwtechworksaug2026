-- BMW Data Quality & Governance Platform
-- Quality Queries (Amazon Athena)
-- Participant 12 | Pod D

-- ─── 1. Latest Quality Reports ──────────────────────────────
SELECT
    dataset_name,
    quality_score,
    score_label,
    total_records,
    valid_records,
    rejected_records,
    execution_timestamp
FROM bmw_data_quality.data_quality_reports
ORDER BY execution_timestamp DESC
LIMIT 20;

-- ─── 2. Violation Summary ────────────────────────────────────
SELECT
    dataset_name,
    null_count,
    duplicate_count,
    invalid_vin_count,
    invalid_date_count,
    range_violation_count,
    referential_error_count,
    (null_count + duplicate_count + invalid_vin_count +
     invalid_date_count + range_violation_count + referential_error_count) AS total_violations
FROM bmw_data_quality.data_quality_reports
ORDER BY total_violations DESC;

-- ─── 3. Rejection Rate ───────────────────────────────────────
SELECT
    dataset_name,
    total_records,
    rejected_records,
    ROUND(CAST(rejected_records AS DOUBLE) / total_records * 100, 2) AS rejection_rate_pct,
    quality_score
FROM bmw_data_quality.data_quality_reports;

-- ─── 4. Quarantine by Error Type ─────────────────────────────
SELECT
    quarantine_error_type,
    COUNT(*) AS record_count
FROM bmw_data_quality.quarantine_telemetry
GROUP BY quarantine_error_type
ORDER BY record_count DESC;

-- ─── 5. Score Trend ──────────────────────────────────────────
SELECT
    dataset_name,
    execution_timestamp,
    quality_score,
    score_label
FROM bmw_data_quality.data_quality_reports
ORDER BY dataset_name, execution_timestamp;
