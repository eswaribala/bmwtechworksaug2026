// BMW Data Quality & Governance Platform — Mock / Demo Data
// Used for pre-loading the dashboard without a CSV file being uploaded.

import type { QualityMetrics, QuarantineRecord, LogEntry, GovernanceAccess } from '../types';

// ─────────────────────────────────────────────────────────────────────────────
// Demo Quality Metrics (matches the spec's example: 10,000 rows, 94.2 score)
// ─────────────────────────────────────────────────────────────────────────────
export const DEMO_METRICS: QualityMetrics = {
  dataset: 'telemetry',
  execution_time: '2026-09-16T10:30:00Z',
  duration_seconds: 3.421,
  total_records: 10000,
  valid_records: 9420,
  rejected_records: 580,
  quality_score: 94.2,
  score_label: 'EXCELLENT',
  checks: {
    null_count: 210,
    duplicate_count: 150,
    invalid_vin_count: 80,
    invalid_date_count: 60,
    range_violation_count: 50,
    referential_error_count: 30,
  },
  null_summary: [
    { column: 'vehicle_id', null_count: 105, null_pct: 1.05 },
    { column: 'vin',        null_count: 105, null_pct: 1.05 },
    { column: 'timestamp',  null_count: 0,   null_pct: 0.00 },
    { column: 'battery_level', null_count: 0, null_pct: 0.00 },
    { column: 'speed',      null_count: 0,   null_pct: 0.00 },
    { column: 'temperature',null_count: 0,   null_pct: 0.00 },
  ],
  penalty_breakdown: {
    null_check:             { violations: 210, violation_rate_pct: 2.10, weight: 20, penalty: 0.42 },
    duplicate_check:        { violations: 150, violation_rate_pct: 1.50, weight: 15, penalty: 0.225 },
    vin_check:              { violations: 80,  violation_rate_pct: 0.80, weight: 20, penalty: 0.16 },
    date_check:             { violations: 60,  violation_rate_pct: 0.60, weight: 15, penalty: 0.09 },
    range_check:            { violations: 50,  violation_rate_pct: 0.50, weight: 15, penalty: 0.075 },
    referential_integrity:  { violations: 30,  violation_rate_pct: 0.30, weight: 15, penalty: 0.045 },
  },
};

// ─────────────────────────────────────────────────────────────────────────────
// Demo Quarantine Records
// ─────────────────────────────────────────────────────────────────────────────
export const DEMO_QUARANTINE: QuarantineRecord[] = [
  { event_id: 'EVT0001234', vehicle_id: null, vin: 'WBA00000000000223', timestamp: '2026-01-04 01:35:00', battery_level: 54.8, speed: 71.63, temperature: 9.38, quarantine_error_type: 'NULL_VALUE', quarantine_error_message: 'Null values in: vehicle_id', quarantine_dataset: 'telemetry', quarantine_timestamp: '2026-09-16T10:30:00Z' },
  { event_id: 'EVT0005678', vehicle_id: 'BMW00110', vin: 'INVALID_VIN', timestamp: '2026-02-12 05:30:00', battery_level: 77.31, speed: 70.54, temperature: 1.13, quarantine_error_type: 'INVALID_VIN', quarantine_error_message: 'Invalid or missing VIN', quarantine_dataset: 'telemetry', quarantine_timestamp: '2026-09-16T10:30:00Z' },
  { event_id: 'EVT0009012', vehicle_id: 'BMW00213', vin: 'WBA00000000000213', timestamp: '2026-15-40 99:99:99', battery_level: 67.19, speed: 124.02, temperature: 53.58, quarantine_error_type: 'INVALID_DATE', quarantine_error_message: 'Invalid date in: timestamp', quarantine_dataset: 'telemetry', quarantine_timestamp: '2026-09-16T10:30:00Z' },
  { event_id: 'EVT0003456', vehicle_id: 'BMW00855', vin: 'WBA00000000000855', timestamp: '2026-08-13 09:20:00', battery_level: 150.0, speed: 129.28, temperature: 11.24, quarantine_error_type: 'OUT_OF_RANGE', quarantine_error_message: 'Out-of-range value in: battery_level', quarantine_dataset: 'telemetry', quarantine_timestamp: '2026-09-16T10:30:00Z' },
  { event_id: 'EVT0007890', vehicle_id: 'FAKE00001', vin: 'WBA00000000000625', timestamp: '2026-08-25 10:25:00', battery_level: 11.42, speed: 42.22, temperature: -1.47, quarantine_error_type: 'REFERENTIAL_INTEGRITY', quarantine_error_message: 'Referential integrity violation', quarantine_dataset: 'telemetry', quarantine_timestamp: '2026-09-16T10:30:00Z' },
  { event_id: 'EVT0002345', vehicle_id: 'BMW00327', vin: 'WBA00000000000327', timestamp: '2026-03-30 03:25:00', battery_level: -5.0, speed: 141.7, temperature: 13.6, quarantine_error_type: 'OUT_OF_RANGE', quarantine_error_message: 'Out-of-range value in: battery_level', quarantine_dataset: 'telemetry', quarantine_timestamp: '2026-09-16T10:30:00Z' },
  { event_id: 'EVT0001234', vehicle_id: 'BMW00867', vin: 'WBA00000000000867', timestamp: '2026-07-12 19:20:00', battery_level: 71.65, speed: 85.14, temperature: 1.05, quarantine_error_type: 'DUPLICATE_RECORD', quarantine_error_message: 'Duplicate record detected', quarantine_dataset: 'telemetry', quarantine_timestamp: '2026-09-16T10:30:00Z' },
  { event_id: 'EVT0006789', vehicle_id: null, vin: null, timestamp: '2026-08-24 11:15:00', battery_level: 66.8, speed: 0.77, temperature: 5.5, quarantine_error_type: 'NULL_VALUE', quarantine_error_message: 'Null values in: vehicle_id, vin', quarantine_dataset: 'telemetry', quarantine_timestamp: '2026-09-16T10:30:00Z' },
  { event_id: 'EVT0004567', vehicle_id: 'BMW00577', vin: 'WBA00000000000577', timestamp: 'not-a-date', battery_level: 48.86, speed: 50.0, temperature: 51.19, quarantine_error_type: 'INVALID_DATE', quarantine_error_message: 'Invalid date in: timestamp', quarantine_dataset: 'telemetry', quarantine_timestamp: '2026-09-16T10:30:00Z' },
  { event_id: 'EVT0008901', vehicle_id: 'FAKE00002', vin: 'BADVIN123', timestamp: '2026-05-01 07:00:00', battery_level: 33.5, speed: 95.1, temperature: 22.0, quarantine_error_type: 'REFERENTIAL_INTEGRITY|INVALID_VIN', quarantine_error_message: 'Referential integrity violation | Invalid or missing VIN', quarantine_dataset: 'telemetry', quarantine_timestamp: '2026-09-16T10:30:00Z' },
];

// ─────────────────────────────────────────────────────────────────────────────
// Pipeline Log Stream
// ─────────────────────────────────────────────────────────────────────────────
export const DEMO_LOGS: LogEntry[] = [
  { timestamp: '2026-09-16T10:29:57Z', level: 'INFO', dataset: 'telemetry', message: 'Pipeline started' },
  { timestamp: '2026-09-16T10:29:57Z', level: 'INFO', dataset: 'telemetry', message: 'Dataset: telemetry' },
  { timestamp: '2026-09-16T10:29:57Z', level: 'INFO', dataset: 'telemetry', message: 'Records received: 10,000' },
  { timestamp: '2026-09-16T10:29:58Z', level: 'INFO', dataset: 'telemetry', message: 'Schema validation passed' },
  { timestamp: '2026-09-16T10:29:58Z', level: 'INFO', dataset: 'telemetry', message: 'Null issues: 210' },
  { timestamp: '2026-09-16T10:29:58Z', level: 'INFO', dataset: 'telemetry', message: 'Duplicate records: 150' },
  { timestamp: '2026-09-16T10:29:59Z', level: 'INFO', dataset: 'telemetry', message: 'Invalid VIN: 80' },
  { timestamp: '2026-09-16T10:29:59Z', level: 'INFO', dataset: 'telemetry', message: 'Invalid dates: 60' },
  { timestamp: '2026-09-16T10:29:59Z', level: 'INFO', dataset: 'telemetry', message: 'Range violations: 50' },
  { timestamp: '2026-09-16T10:29:59Z', level: 'INFO', dataset: 'telemetry', message: 'Referential errors: 30' },
  { timestamp: '2026-09-16T10:30:00Z', level: 'INFO', dataset: 'telemetry', message: 'Records processed: 10,000' },
  { timestamp: '2026-09-16T10:30:00Z', level: 'INFO', dataset: 'telemetry', message: 'Valid records: 9,420' },
  { timestamp: '2026-09-16T10:30:00Z', level: 'WARN', dataset: 'telemetry', message: 'Rejected records: 580' },
  { timestamp: '2026-09-16T10:30:00Z', level: 'INFO', dataset: 'telemetry', message: 'Quality score: 94.2' },
  { timestamp: '2026-09-16T10:30:00Z', level: 'INFO', dataset: 'telemetry', message: 'Writing curated data to S3…' },
  { timestamp: '2026-09-16T10:30:01Z', level: 'INFO', dataset: 'telemetry', message: 'Curated records written: 9,420' },
  { timestamp: '2026-09-16T10:30:01Z', level: 'WARN', dataset: 'telemetry', message: 'Writing 580 records to quarantine…' },
  { timestamp: '2026-09-16T10:30:01Z', level: 'INFO', dataset: 'telemetry', message: 'Quarantine records saved: 580' },
  { timestamp: '2026-09-16T10:30:01Z', level: 'INFO', dataset: 'telemetry', message: 'Quality report generated' },
  { timestamp: '2026-09-16T10:30:01Z', level: 'INFO', dataset: 'telemetry', message: 'Glue Catalog updated: bmw_telemetry' },
  { timestamp: '2026-09-16T10:30:02Z', level: 'INFO', dataset: 'telemetry', message: 'CloudWatch logs uploaded' },
  { timestamp: '2026-09-16T10:30:02Z', level: 'INFO', dataset: 'telemetry', message: 'Pipeline completed in 3.421s' },
];

// ─────────────────────────────────────────────────────────────────────────────
// Lake Formation Governance Access Matrix
// ─────────────────────────────────────────────────────────────────────────────
export const GOVERNANCE_ACCESS: GovernanceAccess[] = [
  { role: 'Data Engineer',  zones: { raw: true,  curated: true,  quarantine: true,  reports: true  } },
  { role: 'Data Analyst',   zones: { raw: false, curated: true,  quarantine: false, reports: true  } },
  { role: 'Business User',  zones: { raw: false, curated: false, quarantine: false, reports: true  } },
];

// ─────────────────────────────────────────────────────────────────────────────
// Athena Sample Queries
// ─────────────────────────────────────────────────────────────────────────────
export const ATHENA_QUERIES = [
  {
    label: 'Vehicle Count by Model',
    sql: `SELECT
    model,
    COUNT(*) AS vehicle_count
FROM bmw_vehicle_master
GROUP BY model
ORDER BY vehicle_count DESC;`,
    results: [
      { model: 'X3',        vehicle_count: 188 },
      { model: '3 Series',  vehicle_count: 180 },
      { model: 'i4',        vehicle_count: 175 },
      { model: 'X7',        vehicle_count: 163 },
      { model: '7 Series',  vehicle_count: 158 },
      { model: 'i5',        vehicle_count: 136 },
    ],
  },
  {
    label: 'Quality Report Summary',
    sql: `SELECT
    dataset_name,
    quality_score,
    total_records,
    rejected_records,
    execution_timestamp
FROM data_quality_reports
ORDER BY execution_timestamp DESC;`,
    results: [
      { dataset_name: 'telemetry', quality_score: 94.2, total_records: 10000, rejected_records: 580, execution_timestamp: '2026-09-16 10:30:00' },
    ],
  },
  {
    label: 'Avg Battery Level by Region',
    sql: `SELECT
    vm.region,
    ROUND(AVG(t.battery_level), 1) AS avg_battery,
    COUNT(*) AS events
FROM bmw_telemetry t
JOIN bmw_vehicle_master vm ON t.vehicle_id = vm.vehicle_id
GROUP BY vm.region
ORDER BY avg_battery DESC;`,
    results: [
      { region: 'North America', avg_battery: 53.1, events: 2100 },
      { region: 'Europe',        avg_battery: 51.8, events: 3200 },
      { region: 'Asia',          avg_battery: 50.4, events: 1800 },
      { region: 'Middle East',   avg_battery: 48.9, events: 1500 },
      { region: 'Oceania',       avg_battery: 47.2, events: 820  },
    ],
  },
];

// ─────────────────────────────────────────────────────────────────────────────
// Score helpers
// ─────────────────────────────────────────────────────────────────────────────
export function getScoreColor(score: number): string {
  if (score >= 90) return '#00C48C';
  if (score >= 80) return '#0066CC';
  if (score >= 70) return '#FFA500';
  if (score >= 50) return '#FF6B35';
  return '#FF4757';
}

export function getScoreLabel(score: number): string {
  if (score >= 90) return 'EXCELLENT';
  if (score >= 80) return 'GOOD';
  if (score >= 70) return 'ACCEPTABLE';
  if (score >= 50) return 'POOR';
  return 'CRITICAL';
}

export const ERROR_TYPE_COLORS: Record<string, string> = {
  NULL_VALUE:             '#FF6B35',
  DUPLICATE_RECORD:       '#FFD93D',
  INVALID_VIN:            '#C77DFF',
  INVALID_DATE:           '#74B9FF',
  OUT_OF_RANGE:           '#FF4757',
  REFERENTIAL_INTEGRITY:  '#00C48C',
};
