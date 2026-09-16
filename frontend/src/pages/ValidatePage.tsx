import { useState, useRef, type DragEvent, type ChangeEvent } from 'react';
import Papa from 'papaparse';
import { getScoreColor, getScoreLabel } from '../data/mockData';

// ── Backend API URL (set VITE_API_URL in .env to override)
const API_URL = (import.meta as any).env?.VITE_API_URL ?? 'http://localhost:8000';

interface ValidationResult {
  dataset: string;
  totalRows: number;
  nullCount: number;
  duplicateCount: number;
  invalidVinCount: number;
  invalidDateCount: number;
  rangeViolationCount: number;
  referentialErrorCount: number;
  score: number;
  columnStats: { column: string; nullCount: number; nullPct: number }[];
  // AWS metadata (only populated when backend is online)
  awsConnected?: boolean;
  rawS3Path?: string | null;
  curatedPath?: string | null;
  quarantinePath?: string | null;
  reportPath?: string | null;
  source?: 'backend' | 'browser';
}

// ── In-browser fallback constants ──────────────────────────────────
const VIN_REGEX = /^[A-HJ-NPR-Z0-9]{17}$/i;
const REQUIRED_COLS_TELEMETRY = ['event_id', 'vehicle_id', 'vin', 'timestamp', 'battery_level'];
const REQUIRED_COLS_VEHICLE_MASTER = ['vehicle_id', 'vin', 'model', 'model_year'];

function detectDataset(columns: string[]): string {
  if (columns.includes('event_id')) return 'telemetry';
  if (columns.includes('vehicle_id') || columns.includes('model') || columns.includes('vin')) return 'vehicle_master';
  return 'unknown';
}

function validateInBrowser(rows: Record<string, string>[], dataset: string): ValidationResult {
  const total = rows.length;
  const required =
    dataset === 'telemetry' ? REQUIRED_COLS_TELEMETRY : REQUIRED_COLS_VEHICLE_MASTER;
  const cols = Object.keys(rows[0] || {});

  // Null check
  let nullCount = 0;
  const colNulls: Record<string, number> = {};
  required.forEach(c => { colNulls[c] = 0; });
  rows.forEach(row => {
    let rowHasNull = false;
    required.forEach(c => {
      if (!row[c] || row[c].trim() === '' || row[c] === 'null' || row[c] === 'NULL') {
        colNulls[c] = (colNulls[c] || 0) + 1;
        rowHasNull = true;
      }
    });
    if (rowHasNull) nullCount++;
  });

  // Duplicate check
  const seen = new Set<string>();
  let duplicateCount = 0;
  const idCol = dataset === 'telemetry' ? 'event_id' : 'vehicle_id';
  rows.forEach(row => {
    const key = row[idCol];
    if (key && seen.has(key)) duplicateCount++;
    else if (key) seen.add(key);
  });

  // VIN check
  let invalidVinCount = 0;
  if (cols.includes('vin')) {
    rows.forEach(row => {
      const vin = row['vin']?.trim() ?? '';
      if (!vin || !VIN_REGEX.test(vin)) invalidVinCount++;
    });
  }

  // Date check
  let invalidDateCount = 0;
  const dateCol = dataset === 'telemetry' ? 'timestamp' : null;
  if (dateCol && cols.includes(dateCol)) {
    rows.forEach(row => {
      const d = row[dateCol]?.trim();
      if (!d || isNaN(Date.parse(d))) invalidDateCount++;
    });
  }

  // Range check
  let rangeViolationCount = 0;
  if (cols.includes('battery_level')) {
    rows.forEach(row => {
      const v = parseFloat(row['battery_level']);
      if (isNaN(v) || v < 0 || v > 100) rangeViolationCount++;
    });
  }

  const totalViolations = nullCount + duplicateCount + invalidVinCount + invalidDateCount + rangeViolationCount;
  const violationRate = totalViolations / Math.max(total, 1);
  const score = Math.max(0, +(100 - violationRate * 100).toFixed(1));

  const columnStats = required.map(c => ({
    column: c,
    nullCount: colNulls[c] || 0,
    nullPct: +((colNulls[c] || 0) / Math.max(total, 1) * 100).toFixed(2),
  }));

  return {
    dataset, totalRows: total, nullCount, duplicateCount, invalidVinCount,
    invalidDateCount, rangeViolationCount, referentialErrorCount: 0,
    score, columnStats, source: 'browser',
  };
}

// ── Map backend JSON report to our UI shape ─────────────────────────
function mapBackendReport(data: any, _filename?: string): ValidationResult {
  const report = data.bmw_data_quality_report || {};
  const recSummary = report.record_summary || {};
  const checks = report.quality_checks || {};
  const s3 = data.s3_paths ?? {};

  const rawNullList = report.null_analysis ?? data.null_summary ?? [];
  const nullSummary: { column: string; nullCount: number; nullPct: number }[] =
    rawNullList.map((s: any) => ({
      column: s.column,
      nullCount: s.null_count ?? s.nullCount ?? 0,
      nullPct: s.null_pct ?? s.nullPct ?? 0,
    }));

  return {
    dataset:               report.dataset ?? data.dataset ?? 'unknown',
    totalRows:             recSummary.total_records ?? data.total_records ?? data.totalRows ?? 0,
    nullCount:             checks.null_issues ?? data.null_count ?? 0,
    duplicateCount:        checks.duplicate_records ?? data.duplicate_count ?? 0,
    invalidVinCount:       checks.invalid_vin ?? data.invalid_vin_count ?? 0,
    invalidDateCount:      checks.invalid_dates ?? data.invalid_date_count ?? 0,
    rangeViolationCount:   checks.range_violations ?? data.range_violation_count ?? 0,
    referentialErrorCount: checks.referential_errors ?? data.referential_error_count ?? 0,
    score:                 report.quality_score ?? data.quality_score ?? 0,
    columnStats:           nullSummary,
    awsConnected:          data.aws_connected ?? false,
    rawS3Path:             data.raw_s3_path ?? null,
    curatedPath:           s3.curated ?? null,
    quarantinePath:        s3.quarantine ?? null,
    reportPath:            s3.report ?? null,
    source:                'backend',
  };
}

// ────────────────────────────────────────────────────────────────────
// Component
// ────────────────────────────────────────────────────────────────────

export default function ValidatePage() {
  const [dragging, setDragging]     = useState(false);
  const [progress, setProgress]     = useState(0);
  const [processing, setProcessing] = useState(false);
  const [result, setResult]         = useState<ValidationResult | null>(null);
  const [fileName, setFileName]     = useState('');
  const [statusMsg, setStatusMsg]   = useState('');
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // ── Try real backend first, fall back to browser ────────────────
  async function processFile(file: File) {
    setFileName(file.name);
    setProcessing(true);
    setProgress(10);
    setResult(null);
    setStatusMsg('Connecting to quality engine…');

    // 1. Try backend
    try {
      const form = new FormData();
      form.append('file', file);
      setProgress(20);
      setStatusMsg('Uploading to S3 raw/ and running quality checks…');

      const res = await fetch(`${API_URL}/upload`, { method: 'POST', body: form });
      if (!res.ok) throw new Error(`Backend returned ${res.status}`);

      const data = await res.json();
      setBackendOnline(true);
      setProgress(95);
      setStatusMsg('Quality checks complete!');
      setTimeout(() => {
        setResult(mapBackendReport(data, file.name));
        setProgress(100);
        setProcessing(false);
        setStatusMsg('');
      }, 300);
      return;
    } catch {
      setBackendOnline(false);
      setStatusMsg('Backend offline — running in-browser checks (no S3)…');
    }

    // 2. In-browser fallback
    setProgress(30);
    const allRows: Record<string, string>[] = [];
    let processed = 0;

    Papa.parse<Record<string, string>>(file, {
      header: true,
      skipEmptyLines: true,
      chunk: (results, parser) => {
        allRows.push(...results.data);
        processed += results.data.length;
        parser.pause();
        setProgress(30 + Math.min(55, Math.round((processed / (file.size / 120)) * 55)));
        setTimeout(() => parser.resume(), 0);
      },
      complete: () => {
        setProgress(90);
        const dataset = detectDataset(Object.keys(allRows[0] || {}));
        const res = validateInBrowser(allRows, dataset);
        setTimeout(() => {
          setResult(res);
          setProgress(100);
          setProcessing(false);
          setStatusMsg('');
        }, 400);
      },
      error: () => {
        setProcessing(false);
        setStatusMsg('Failed to parse CSV.');
      },
    });
  }

  function onDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) processFile(file);
  }

  function onChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) processFile(file);
  }

  const scoreColor = result ? getScoreColor(result.score) : 'var(--bmw-blue)';
  const scoreLabel = result ? getScoreLabel(result.score) : '';

  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1>Dataset Validation</h1>
          <p>Upload a BMW CSV dataset — automatically processed through the full quality engine</p>
        </div>
        {/* Backend status badge */}
        {backendOnline !== null && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{
              display: 'inline-flex', alignItems: 'center', gap: 6,
              padding: '4px 12px', borderRadius: 20, fontSize: 12, fontWeight: 600,
              background: backendOnline ? 'rgba(46,204,113,0.15)' : 'rgba(255,107,53,0.15)',
              border: `1px solid ${backendOnline ? '#2ecc71' : '#FF6B35'}`,
              color: backendOnline ? '#2ecc71' : '#FF6B35',
            }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'currentColor' }} />
              {backendOnline ? 'AWS Pipeline Online' : 'Browser Mode (No AWS)'}
            </span>
          </div>
        )}
      </div>

      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

        {/* Upload Zone */}
        <div className="card card-body"
          style={{ padding: 0 }}
          onDragOver={e => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
        >
          <div className={`upload-zone ${dragging ? 'drag-over' : ''}`} onClick={() => inputRef.current?.click()}>
            <div className="upload-icon">📂</div>
            <h3>Drop a BMW CSV file here</h3>
            <p style={{ marginBottom: '0.5rem' }}>
              Supports: bmw_telemetry.csv · bmw_vehicle_master.csv · bmw_sales.csv · bmw_maintenance.csv
            </p>
            <p style={{ marginBottom: '1rem', fontSize: 12, color: 'var(--text-muted)' }}>
              File is automatically uploaded to S3 raw/ and processed through the quality engine
            </p>
            <button className="btn btn-primary" type="button">Browse File</button>
            <input ref={inputRef} type="file" accept=".csv" style={{ display: 'none' }} onChange={onChange} id="file-upload" />
          </div>
        </div>

        {/* Progress */}
        {(processing || progress > 0) && (
          <div className="card card-body">
            <div className="flex justify-between mb-2">
              <span style={{ fontSize: 13 }}>Processing: <strong>{fileName}</strong></span>
              <span style={{ fontSize: 13, color: 'var(--bmw-blue-bright)' }}>{progress}%</span>
            </div>
            <div className="progress-bar-wrap">
              <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
            </div>
            {statusMsg && <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 8 }}>{statusMsg}</p>}
          </div>
        )}

        {/* Results */}
        {result && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', animation: 'countUp 0.4s ease' }}>

            {/* AWS pipeline paths */}
            {result.source === 'backend' && (
              <div className="card card-body" style={{
                background: 'rgba(0,90,200,0.08)', border: '1px solid rgba(0,90,200,0.25)',
                display: 'flex', flexDirection: 'column', gap: 6,
              }}>
                <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 4 }}>
                  {result.awsConnected ? '☁️ AWS S3 Paths' : '💾 Local Output Paths'}
                </div>
                {result.rawS3Path && (
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                    <strong>Raw:</strong> <code style={{ fontSize: 11 }}>{result.rawS3Path}</code>
                  </div>
                )}
                {result.curatedPath && (
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                    <strong>Curated:</strong> <code style={{ fontSize: 11 }}>{result.curatedPath}</code>
                  </div>
                )}
                {result.quarantinePath && (
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                    <strong>Quarantine:</strong> <code style={{ fontSize: 11 }}>{result.quarantinePath}</code>
                  </div>
                )}
                {result.reportPath && (
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                    <strong>Report:</strong> <code style={{ fontSize: 11 }}>{result.reportPath}</code>
                  </div>
                )}
              </div>
            )}

            {/* Score cards row 1 */}
            <div className="kpi-grid">
              <div className="kpi-card" style={{ '--accent-color': scoreColor } as React.CSSProperties}>
                <div className="kpi-label">Quality Score</div>
                <div className="kpi-value" style={{ color: scoreColor }}>{result.score.toFixed(1)}</div>
                <div className="kpi-sub"><span className={`badge badge-${scoreLabel.toLowerCase()}`}>{scoreLabel}</span></div>
              </div>
              <div className="kpi-card" style={{ '--accent-color': 'var(--bmw-blue-bright)' } as React.CSSProperties}>
                <div className="kpi-label">Total Records</div>
                <div className="kpi-value">{result.totalRows.toLocaleString()}</div>
              </div>
              <div className="kpi-card" style={{ '--accent-color': '#FF6B35' } as React.CSSProperties}>
                <div className="kpi-label">Null Issues</div>
                <div className="kpi-value" style={{ color: '#FF6B35' }}>{result.nullCount.toLocaleString()}</div>
              </div>
              <div className="kpi-card" style={{ '--accent-color': '#FFD93D' } as React.CSSProperties}>
                <div className="kpi-label">Duplicates</div>
                <div className="kpi-value" style={{ color: '#FFD93D' }}>{result.duplicateCount.toLocaleString()}</div>
              </div>
            </div>

            {/* Score cards row 2 */}
            <div className="kpi-grid">
              <div className="kpi-card" style={{ '--accent-color': '#C77DFF' } as React.CSSProperties}>
                <div className="kpi-label">Invalid VIN</div>
                <div className="kpi-value" style={{ color: '#C77DFF' }}>{result.invalidVinCount.toLocaleString()}</div>
              </div>
              <div className="kpi-card" style={{ '--accent-color': '#74B9FF' } as React.CSSProperties}>
                <div className="kpi-label">Invalid Dates</div>
                <div className="kpi-value" style={{ color: '#74B9FF' }}>{result.invalidDateCount.toLocaleString()}</div>
              </div>
              <div className="kpi-card" style={{ '--accent-color': '#FF4757' } as React.CSSProperties}>
                <div className="kpi-label">Range Violations</div>
                <div className="kpi-value" style={{ color: '#FF4757' }}>{result.rangeViolationCount.toLocaleString()}</div>
              </div>
              <div className="kpi-card" style={{ '--accent-color': '#FFA502' } as React.CSSProperties}>
                <div className="kpi-label">Referential Errors</div>
                <div className="kpi-value" style={{ color: '#FFA502' }}>{result.referentialErrorCount.toLocaleString()}</div>
              </div>
            </div>

            {/* Valid vs Rejected summary */}
            <div className="kpi-grid" style={{ gridTemplateColumns: '1fr 1fr 1fr' }}>
              <div className="kpi-card" style={{ '--accent-color': 'var(--color-excellent)' } as React.CSSProperties}>
                <div className="kpi-label">Valid Records</div>
                <div className="kpi-value" style={{ color: 'var(--color-excellent)' }}>
                  {(result.totalRows - result.nullCount - result.duplicateCount).toLocaleString()}
                </div>
                <div className="kpi-sub">→ Curated S3</div>
              </div>
              <div className="kpi-card" style={{ '--accent-color': '#FF4757' } as React.CSSProperties}>
                <div className="kpi-label">Rejected Records</div>
                <div className="kpi-value" style={{ color: '#FF4757' }}>
                  {(result.nullCount + result.duplicateCount + result.invalidVinCount + result.invalidDateCount + result.rangeViolationCount + result.referentialErrorCount).toLocaleString()}
                </div>
                <div className="kpi-sub">→ Quarantine S3</div>
              </div>
              <div className="kpi-card" style={{ '--accent-color': 'var(--bmw-blue-bright)' } as React.CSSProperties}>
                <div className="kpi-label">Dataset Detected</div>
                <div className="kpi-value" style={{ fontSize: 18, color: 'var(--bmw-blue-bright)', textTransform: 'capitalize' }}>
                  {result.dataset}
                </div>
                <div className="kpi-sub">{result.source === 'backend' ? '🔴 Live Pipeline' : '🟡 Browser Mode'}</div>
              </div>
            </div>

            {/* Column null stats */}
            {result.columnStats.length > 0 && (
              <div className="card">
                <div className="card-header"><h3>Null Analysis by Column</h3></div>
                <div className="card-body">
                  <table className="data-table">
                    <thead>
                      <tr><th>Column</th><th>Null Count</th><th>Null %</th><th>Progress</th><th>Status</th></tr>
                    </thead>
                    <tbody>
                      {result.columnStats.map(s => (
                        <tr key={s.column}>
                          <td className="monospace">{s.column}</td>
                          <td>{s.nullCount.toLocaleString()}</td>
                          <td>{s.nullPct.toFixed(2)}%</td>
                          <td style={{ width: 140 }}>
                            <div className="progress-bar-wrap">
                              <div className="progress-bar-fill" style={{
                                width: `${Math.min(s.nullPct * 20, 100)}%`,
                                background: s.nullPct > 1 ? '#FF4757' : 'var(--bmw-blue)',
                              }} />
                            </div>
                          </td>
                          <td>
                            <span className={`badge ${s.nullPct === 0 ? 'badge-excellent' : s.nullPct < 2 ? 'badge-good' : 'badge-poor'}`}>
                              {s.nullPct === 0 ? 'CLEAN' : s.nullPct < 2 ? 'WARN' : 'FAIL'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Validation rules reference */}
        <div className="card">
          <div className="card-header"><h3>Validation Rules Applied</h3></div>
          <div className="card-body">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
              {[
                { icon: '🔴', rule: 'Null Check', desc: 'Required columns must not be empty' },
                { icon: '🟡', rule: 'Duplicate Detection', desc: 'Unique key columns must not repeat' },
                { icon: '🟣', rule: 'VIN Validation', desc: '17-char alphanumeric (no I/O/Q)' },
                { icon: '🔵', rule: 'Date Validation', desc: 'ISO 8601 timestamp format check' },
                { icon: '🔴', rule: 'Range Validation', desc: 'battery: 0–100, temp: –40–120, speed: 0–300' },
                { icon: '🟢', rule: 'Referential Integrity', desc: 'vehicle_id must exist in master' },
              ].map(r => (
                <div key={r.rule} style={{
                  padding: '0.875rem', background: 'var(--bg-glass)',
                  borderRadius: 8, border: '1px solid var(--border-subtle)',
                }}>
                  <div style={{ fontSize: 20, marginBottom: 6 }}>{r.icon}</div>
                  <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 4 }}>{r.rule}</div>
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{r.desc}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
