import { useState, useEffect } from 'react';
import FileFilter from '../components/FileFilter';
import { usePipeline, API_URL } from '../context/PipelineContext';
import { ERROR_TYPE_COLORS, fmt } from '../utils/constants';

type CheckTab = 'null' | 'duplicate' | 'vin' | 'date' | 'range' | 'referential';

const CHECK_DEFINITIONS: Record<CheckTab, { title: string; rule: string; impact: string; color: string; errorType: string }> = {
  null: {
    title: 'Null Value Validation',
    rule: 'Mandatory columns must not contain NULL, empty strings, or string representations of null.',
    impact: 'Missing critical identifiers or measurements prevents reliable metric aggregation and pipeline ingestion.',
    color: ERROR_TYPE_COLORS.NULL_VALUE,
    errorType: 'NULL_VALUE',
  },
  duplicate: {
    title: 'Duplicate Record Detection',
    rule: 'Primary key columns (event_id for telemetry, vehicle_id for vehicle master) must be unique within the dataset.',
    impact: 'Duplicate records inflate volume counts and skew statistical analyses.',
    color: ERROR_TYPE_COLORS.DUPLICATE_RECORD,
    errorType: 'DUPLICATE_RECORD',
  },
  vin: {
    title: 'VIN Verification (ISO 3779)',
    rule: 'Vehicle Identification Numbers must be exactly 17 alphanumeric characters, excluding letters I, O, and Q.',
    impact: 'Malformed VINs cannot be resolved to physical fleet units or referenced across BMW systems.',
    color: ERROR_TYPE_COLORS.INVALID_VIN,
    errorType: 'INVALID_VIN',
  },
  date: {
    title: 'Date and Timestamp Verification',
    rule: 'Timestamp values must parse into standard ISO 8601 timestamps.',
    impact: 'Unparseable timestamps disrupt chronological ordering and time-series telemetry calculations.',
    color: ERROR_TYPE_COLORS.INVALID_DATE,
    errorType: 'INVALID_DATE',
  },
  range: {
    title: 'Sensor Range Boundaries',
    rule: 'Physical values must fall within valid operational limits (e.g., Battery: 0–100%, Speed: 0–300 km/h, Temperature: -40 to 120°C).',
    impact: 'Extreme or impossible sensor values indicate telemetry hardware malfunction or ingestion corruption.',
    color: ERROR_TYPE_COLORS.OUT_OF_RANGE,
    errorType: 'OUT_OF_RANGE',
  },
  referential: {
    title: 'Referential Integrity Verification',
    rule: 'Foreign keys in child tables (e.g., telemetry.vehicle_id) must exist in the parent bmw_vehicle_master table.',
    impact: 'Orphaned telemetry events cannot be attributed to a registered BMW fleet vehicle.',
    color: ERROR_TYPE_COLORS.REFERENTIAL_INTEGRITY,
    errorType: 'REFERENTIAL_INTEGRITY',
  },
};

export default function ChecksPage() {
  const { selectedRun, datasetFilter } = usePipeline();
  const [activeTab, setActiveTab] = useState<CheckTab>('null');
  const [reportDetail, setReportDetail] = useState<any>(null);
  const [sampleRecords, setSampleRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Fetch report details for the selected run
  useEffect(() => {
    if (!selectedRun?.run_id) {
      setReportDetail(null);
      return;
    }
    fetch(`${API_URL}/api/history/${selectedRun.run_id}`)
      .then(r => (r.ok ? r.json() : null))
      .then(d => setReportDetail(d))
      .catch(() => setReportDetail(null));
  }, [selectedRun?.run_id]);

  // Fetch real failing records for active check tab
  useEffect(() => {
    if (!selectedRun?.run_id) {
      setSampleRecords([]);
      return;
    }
    setLoading(true);
    const errType = CHECK_DEFINITIONS[activeTab].errorType;
    fetch(`${API_URL}/api/quarantine?run_id=${selectedRun.run_id}&error_type=${errType}&limit=10`)
      .then(r => (r.ok ? r.json() : { records: [] }))
      .then(data => setSampleRecords(data.records ?? []))
      .catch(() => setSampleRecords([]))
      .finally(() => setLoading(false));
  }, [selectedRun?.run_id, activeTab]);

  const counts: Record<CheckTab, number | null> = {
    null: reportDetail ? reportDetail.null_count ?? 0 : null,
    duplicate: reportDetail ? reportDetail.duplicate_count ?? 0 : null,
    vin: reportDetail ? reportDetail.invalid_vin_count ?? 0 : null,
    date: reportDetail ? reportDetail.invalid_date_count ?? 0 : null,
    range: reportDetail ? reportDetail.range_violation_count ?? 0 : null,
    referential: reportDetail ? reportDetail.referential_error_count ?? 0 : null,
  };

  const activeDef = CHECK_DEFINITIONS[activeTab];
  const activeCount = counts[activeTab];

  const columns = sampleRecords.length > 0
    ? Object.keys(sampleRecords[0]).filter(k => !k.startsWith('quarantine_'))
    : [];

  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1>Quality Checks Detail</h1>
          <p>
            Validation rule audit and failing record inspection · File: {selectedRun?.filename ?? '-'}
          </p>
        </div>
      </div>

      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        <FileFilter />

        {/* Tab Selector */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '0.75rem' }}>
          {(Object.keys(CHECK_DEFINITIONS) as CheckTab[]).map(tabKey => {
            const def = CHECK_DEFINITIONS[tabKey];
            const cnt = counts[tabKey];
            const isSelected = activeTab === tabKey;
            return (
              <div
                key={tabKey}
                onClick={() => setActiveTab(tabKey)}
                className="kpi-card"
                style={{
                  '--accent-color': def.color,
                  cursor: 'pointer',
                  border: isSelected ? `1px solid ${def.color}` : '1px solid var(--border-subtle)',
                  boxShadow: isSelected ? `0 0 16px ${def.color}30` : undefined,
                } as React.CSSProperties}
              >
                <div className="kpi-label" style={{ fontSize: 11 }}>{def.title.split(' ')[0]}</div>
                <div className="kpi-value" style={{ color: def.color, fontSize: 24 }}>
                  {cnt !== null ? fmt(cnt) : '-'}
                </div>
              </div>
            );
          })}
        </div>

        {/* Active Rule Details */}
        <div className="card">
          <div className="card-header">
            <h3>{activeDef.title}</h3>
            <span
              style={{
                fontSize: 11,
                padding: '3px 10px',
                background: `${activeDef.color}15`,
                color: activeDef.color,
                borderRadius: 99,
                border: `1px solid ${activeDef.color}40`,
                fontWeight: 600,
              }}
            >
              {activeCount !== null ? `${fmt(activeCount)} violations recorded` : '-'}
            </span>
          </div>
          <div className="card-body" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            <div>
              <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 }}>
                Validation Rule
              </div>
              <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6, padding: '0.875rem', background: 'var(--bg-secondary)', borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
                {activeDef.rule}
              </div>
            </div>
            <div>
              <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 }}>
                Business Impact
              </div>
              <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6, padding: '0.875rem', background: 'var(--bg-secondary)', borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
                {activeDef.impact}
              </div>
            </div>
          </div>
        </div>

        {/* Failing Records Table */}
        <div className="card">
          <div className="card-header">
            <h3>Failing Records for {activeDef.title}</h3>
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              {sampleRecords.length > 0 ? `Showing ${sampleRecords.length} records` : 'No records found'}
            </span>
          </div>
          <div className="card-body" style={{ padding: 0 }}>
            {sampleRecords.length > 0 ? (
              <div className="data-table-wrap">
                <table className="data-table">
                  <thead>
                    <tr>
                      {columns.map(c => (
                        <th key={c}>{c}</th>
                      ))}
                      <th>Error Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sampleRecords.map((r, i) => (
                      <tr key={i}>
                        {columns.map(c => {
                          const val = r[c];
                          const isNull = val === null || val === '' || val === undefined;
                          return (
                            <td key={c} className="monospace">
                              {isNull ? <span style={{ color: 'var(--color-critical)' }}>NULL</span> : String(val)}
                            </td>
                          );
                        })}
                        <td style={{ color: activeDef.color, fontSize: 12 }}>
                          {r.quarantine_error_message || r.quarantine_error_type || '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div style={{ padding: '2.5rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
                {loading ? 'Loading failing records...' : '- No violations found for this check in the selected file -'}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
