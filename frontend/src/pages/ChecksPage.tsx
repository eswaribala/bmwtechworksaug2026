import { useState } from 'react';
import { DEMO_METRICS, DEMO_QUARANTINE, ERROR_TYPE_COLORS } from '../data/mockData';

type CheckTab = 'null' | 'duplicate' | 'vin' | 'date' | 'range' | 'referential';

const TABS: { key: CheckTab; label: string; count: number; color: string }[] = [
  { key: 'null',        label: '🔴 Null Values',        count: 210, color: ERROR_TYPE_COLORS.NULL_VALUE },
  { key: 'duplicate',   label: '🟡 Duplicates',          count: 150, color: ERROR_TYPE_COLORS.DUPLICATE_RECORD },
  { key: 'vin',         label: '🟣 Invalid VIN',         count: 80,  color: ERROR_TYPE_COLORS.INVALID_VIN },
  { key: 'date',        label: '🔵 Invalid Dates',       count: 60,  color: ERROR_TYPE_COLORS.INVALID_DATE },
  { key: 'range',       label: '🔴 Out-of-Range',        count: 50,  color: ERROR_TYPE_COLORS.OUT_OF_RANGE },
  { key: 'referential', label: '🟢 Ref. Integrity',      count: 30,  color: ERROR_TYPE_COLORS.REFERENTIAL_INTEGRITY },
];

const CHECK_DESCRIPTIONS: Record<CheckTab, { title: string; rule: string; impact: string }> = {
  null:        { title: 'Null Value Check', rule: 'Required columns (vehicle_id, vin, timestamp, battery_level, speed, temperature) must not contain NULL or empty values.', impact: 'NULL records cannot be used for analytics or reporting. They are quarantined.' },
  duplicate:   { title: 'Duplicate Record Detection', rule: 'Each event_id (or vehicle_id+timestamp) must be unique. Any repeat occurrences are flagged as duplicates.', impact: 'Duplicates inflate metrics and skew KPIs. Only the first occurrence is kept in the curated zone.' },
  vin:         { title: 'VIN Validation', rule: 'Vehicle Identification Number must be exactly 17 alphanumeric characters, excluding I, O, and Q (ISO 3779 standard).', impact: 'Invalid VINs cannot be linked to a physical vehicle. Records are quarantined.' },
  date:        { title: 'Date & Timestamp Validation', rule: 'All date/timestamp fields must parse successfully as ISO 8601 format (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS).', impact: 'Invalid timestamps prevent time-series analytics and event ordering.' },
  range:       { title: 'Out-of-Range Value Check', rule: 'battery_level: 0–100 | temperature: –40–120°C | speed: 0–300 km/h. Values outside these ranges are physically impossible.', impact: 'Sensor errors or data corruption. Impossible values would corrupt fleet analytics dashboards.' },
  referential: { title: 'Referential Integrity', rule: 'telemetry.vehicle_id must exist in vehicle_master.vehicle_id. A telemetry event for an unknown vehicle is invalid.', impact: 'Cannot link telemetry to a known vehicle. The record has no analytical value.' },
};

// Generate sample failing records for each check type
const SAMPLE_RECORDS: Record<CheckTab, Record<string, string | number | null>[]> = {
  null: DEMO_QUARANTINE.filter(r => r.quarantine_error_type === 'NULL_VALUE').slice(0, 5),
  duplicate: DEMO_QUARANTINE.filter(r => r.quarantine_error_type === 'DUPLICATE_RECORD').slice(0, 5),
  vin: DEMO_QUARANTINE.filter(r => r.quarantine_error_type === 'INVALID_VIN').slice(0, 5),
  date: DEMO_QUARANTINE.filter(r => r.quarantine_error_type === 'INVALID_DATE').slice(0, 5),
  range: DEMO_QUARANTINE.filter(r => r.quarantine_error_type === 'OUT_OF_RANGE').slice(0, 5),
  referential: DEMO_QUARANTINE.filter(r => r.quarantine_error_type === 'REFERENTIAL_INTEGRITY').slice(0, 5),
};

export default function ChecksPage() {
  const [activeTab, setActiveTab] = useState<CheckTab>('null');
  const desc = CHECK_DESCRIPTIONS[activeTab];
  const tab = TABS.find(t => t.key === activeTab)!;

  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1>Quality Checks Detail</h1>
          <p>Drill down into each validation rule — failing records, explanation, and impact</p>
        </div>
      </div>

      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

        {/* Summary row */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '0.75rem' }}>
          {TABS.map(t => (
            <div
              key={t.key}
              onClick={() => setActiveTab(t.key)}
              className="kpi-card"
              style={{
                '--accent-color': t.color,
                cursor: 'pointer',
                border: activeTab === t.key ? `1px solid ${t.color}` : undefined,
                boxShadow: activeTab === t.key ? `0 0 16px ${t.color}40` : undefined,
              } as React.CSSProperties}
            >
              <div className="kpi-label" style={{ fontSize: 10 }}>{t.label.split(' ').slice(1).join(' ')}</div>
              <div className="kpi-value" style={{ color: t.color, fontSize: 28 }}>{t.count}</div>
            </div>
          ))}
        </div>

        {/* Rule description */}
        <div className="card">
          <div className="card-header">
            <h3>{desc.title}</h3>
            <span style={{ fontSize: 11, padding: '2px 10px', background: `${tab.color}20`, color: tab.color, borderRadius: 99, border: `1px solid ${tab.color}40` }}>
              {tab.count} violations
            </span>
          </div>
          <div className="card-body" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            <div>
              <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8 }}>Validation Rule</div>
              <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.7, padding: '0.75rem', background: 'var(--bg-glass)', borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
                {desc.rule}
              </div>
            </div>
            <div>
              <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8 }}>Business Impact</div>
              <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.7, padding: '0.75rem', background: 'var(--bg-glass)', borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
                {desc.impact}
              </div>
            </div>
          </div>
        </div>

        {/* Failing records table */}
        <div className="card">
          <div className="card-header">
            <h3>Sample Failing Records</h3>
            <div className="flex gap-2">
              <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Showing 5 of {tab.count}</span>
            </div>
          </div>
          <div className="card-body" style={{ padding: 0 }}>
            <div className="data-table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>event_id</th>
                    <th>vehicle_id</th>
                    <th>vin</th>
                    <th>timestamp</th>
                    <th>battery_level</th>
                    <th>Error</th>
                  </tr>
                </thead>
                <tbody>
                  {(SAMPLE_RECORDS[activeTab].length > 0 ? SAMPLE_RECORDS[activeTab] : DEMO_QUARANTINE.slice(0, 5)).map((r, i) => (
                    <tr key={i}>
                      <td className="monospace">{r.event_id ?? <span style={{ color: 'var(--color-critical)' }}>NULL</span>}</td>
                      <td className="monospace">{r.vehicle_id ?? <span style={{ color: 'var(--color-critical)' }}>NULL</span>}</td>
                      <td className="monospace truncate" style={{ maxWidth: 140 }}>{String(r.vin ?? 'NULL')}</td>
                      <td className="monospace" style={{ fontSize: 11 }}>{String(r.timestamp ?? 'NULL')}</td>
                      <td>
                        <span style={{ color: Number(r.battery_level) > 100 || Number(r.battery_level) < 0 ? 'var(--color-critical)' : 'inherit' }}>
                          {r.battery_level ?? 'N/A'}
                        </span>
                      </td>
                      <td>
                        <span style={{ fontSize: 11, padding: '2px 8px', background: `${tab.color}15`, color: tab.color, borderRadius: 99, whiteSpace: 'nowrap' }}>
                          {String(r.quarantine_error_type).split('|')[0]}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Weight / Scoring info */}
        <div className="card">
          <div className="card-header"><h3>Scoring Weight for this Check</h3></div>
          <div className="card-body">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
              {(() => {
                const keyMap: Record<CheckTab, string> = {
                  null: 'null_check', duplicate: 'duplicate_check', vin: 'vin_check',
                  date: 'date_check', range: 'range_check', referential: 'referential_integrity',
                };
                const p = DEMO_METRICS.penalty_breakdown[keyMap[activeTab]];
                return [
                  { label: 'Weight', value: `${p.weight} / 100`, color: tab.color },
                  { label: 'Violation Rate', value: `${p.violation_rate_pct.toFixed(2)}%`, color: 'var(--text-primary)' },
                  { label: 'Penalty Applied', value: `−${p.penalty.toFixed(4)}`, color: 'var(--color-critical)' },
                  { label: 'Violations', value: p.violations.toLocaleString(), color: tab.color },
                ].map(({ label, value, color }) => (
                  <div key={label} style={{ padding: '0.875rem', background: 'var(--bg-glass)', borderRadius: 8, border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 6 }}>{label}</div>
                    <div style={{ fontSize: 22, fontWeight: 800, color }}>{value}</div>
                  </div>
                ));
              })()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
