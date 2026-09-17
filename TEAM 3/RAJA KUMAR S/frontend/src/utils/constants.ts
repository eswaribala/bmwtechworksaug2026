// BMW Data Quality & Governance Platform — Shared constants & formatting helpers

export const ERROR_TYPE_COLORS: Record<string, string> = {
  NULL_VALUE: '#FF6B35',
  DUPLICATE_RECORD: '#FFD93D',
  INVALID_VIN: '#C77DFF',
  INVALID_DATE: '#74B9FF',
  OUT_OF_RANGE: '#FF4757',
  REFERENTIAL_INTEGRITY: '#00C48C',
};

export const ATHENA_PRESET_QUERIES = [
  {
    label: 'Vehicle Count by Model',
    sql: `SELECT
    model,
    COUNT(*) AS vehicle_count
FROM vehicle_master
GROUP BY model
ORDER BY vehicle_count DESC;`,
  },
  {
    label: 'Quality Report Summary',
    sql: `SELECT
    dataset_name,
    quality_score,
    total_records,
    rejected_records,
    execution_timestamp
FROM data_quality_report
ORDER BY execution_timestamp DESC;`,
  },
  {
    label: 'Avg Battery Level by Region',
    sql: `SELECT
    vm.region,
    ROUND(AVG(t.battery_level), 1) AS avg_battery,
    COUNT(*) AS events
FROM telemetry t
JOIN vehicle_master vm ON t.vehicle_id = vm.vehicle_id
GROUP BY vm.region
ORDER BY avg_battery DESC;`,
  },
  {
    label: 'Quarantine by Error Type',
    sql: `SELECT
    quarantine_error_type,
    COUNT(*) AS record_count
FROM quarantine_telemetry
GROUP BY quarantine_error_type
ORDER BY record_count DESC;`,
  },
];

export function getScoreColor(score: number | null | undefined): string {
  if (score === null || score === undefined || Number.isNaN(score)) return 'var(--text-muted)';
  if (score >= 90) return '#00C48C';
  if (score >= 80) return '#0066CC';
  if (score >= 70) return '#FFA500';
  if (score >= 50) return '#FF6B35';
  return '#FF4757';
}

export function getScoreLabel(score: number | null | undefined): string {
  if (score === null || score === undefined || Number.isNaN(score)) return '-';
  if (score >= 90) return 'EXCELLENT';
  if (score >= 80) return 'GOOD';
  if (score >= 70) return 'ACCEPTABLE';
  if (score >= 50) return 'POOR';
  return 'CRITICAL';
}

/** Format a number for display, returning '-' when data is unavailable. */
export function fmt(value: number | null | undefined, digits = 0): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '-';
  return value.toLocaleString(undefined, { maximumFractionDigits: digits, minimumFractionDigits: digits });
}

/** Format a percentage for display, returning '-' when data is unavailable. */
export function fmtPct(value: number | null | undefined, digits = 1): string {
  if (value === null || value === undefined || Number.isNaN(value)) return '-';
  return `${value.toFixed(digits)}%`;
}

/** Format an ISO timestamp for display, returning '-' when unavailable. */
export function fmtDate(value: string | null | undefined): string {
  if (!value) return '-';
  return value.slice(0, 19).replace('T', ' ');
}
