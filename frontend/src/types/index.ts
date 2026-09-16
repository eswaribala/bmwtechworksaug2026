// BMW Data Quality & Governance Platform — TypeScript types

export type ScoreLabel = 'EXCELLENT' | 'GOOD' | 'ACCEPTABLE' | 'POOR' | 'CRITICAL';

export interface QualityChecks {
  null_count: number;
  duplicate_count: number;
  invalid_vin_count: number;
  invalid_date_count: number;
  range_violation_count: number;
  referential_error_count: number;
}

export interface NullSummaryItem {
  column: string;
  null_count: number;
  null_pct: number;
}

export interface PenaltyBreakdown {
  [check: string]: {
    violations: number;
    violation_rate_pct: number;
    weight: number;
    penalty: number;
  };
}

export interface QualityMetrics {
  dataset: string;
  execution_time: string;
  duration_seconds: number;
  total_records: number;
  valid_records: number;
  rejected_records: number;
  quality_score: number;
  score_label: ScoreLabel;
  checks: QualityChecks;
  null_summary: NullSummaryItem[];
  penalty_breakdown: PenaltyBreakdown;
}

export interface QuarantineRecord {
  [key: string]: string | number | null;
  quarantine_error_type: string;
  quarantine_error_message: string;
  quarantine_dataset: string;
  quarantine_timestamp: string;
}

export interface TelemetryRow {
  event_id: string;
  vehicle_id: string;
  vin: string;
  timestamp: string;
  battery_level: number;
  speed: number;
  temperature: number;
  latitude: number;
  longitude: number;
}

export interface VehicleMasterRow {
  vehicle_id: string;
  vin: string;
  model: string;
  model_year: number;
  region: string;
  status: string;
}

export interface LogEntry {
  timestamp: string;
  level: 'INFO' | 'WARN' | 'ERROR';
  dataset: string;
  message: string;
}

export type DataZone = 'raw' | 'curated' | 'quarantine' | 'reports';
export type UserRole = 'Data Engineer' | 'Data Analyst' | 'Business User';

export interface GovernanceAccess {
  role: UserRole;
  zones: { [K in DataZone]: boolean };
}
