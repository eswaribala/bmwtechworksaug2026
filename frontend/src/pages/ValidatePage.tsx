import { useState, useRef, type DragEvent, type ChangeEvent } from 'react';
import Papa from 'papaparse';
import { usePipeline, API_URL } from '../context/PipelineContext';
import { getScoreColor, getScoreLabel, fmt } from '../utils/constants';

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
  awsConnected?: boolean;
  rawS3Path?: string | null;
  curatedPath?: string | null;
  quarantinePath?: string | null;
  reportPath?: string | null;
  source?: 'backend' | 'browser';
  filename?: string;
  runId?: string;
}

const VIN_REGEX = /^[A-HJ-NPR-Z0-9]{17}$/i;
const REQUIRED_COLS_TELEMETRY = ['event_id', 'vehicle_id', 'vin', 'timestamp', 'battery_level'];
const REQUIRED_COLS_VEHICLE_MASTER = ['vehicle_id', 'vin', 'model', 'model_year'];

function validateInBrowser(rows: Record<string, string>[], dataset: string): ValidationResult {
  const total = rows.length;
  const required = dataset === 'telemetry' ? REQUIRED_COLS_TELEMETRY : REQUIRED_COLS_VEHICLE_MASTER;
  const cols = Object.keys(rows[0] || {});

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

  const seen = new Set<string>();
  let duplicateCount = 0;
  const idCol = dataset === 'telemetry' ? 'event_id' : 'vehicle_id';
  rows.forEach(row => {
    const key = row[idCol];
    if (key && seen.has(key)) duplicateCount++;
    else if (key) seen.add(key);
  });

  let invalidVinCount = 0;
  if (cols.includes('vin')) {
    rows.forEach(row => {
      const vin = row['vin']?.trim() ?? '';
      if (!vin || !VIN_REGEX.test(vin)) invalidVinCount++;
    });
  }

  let invalidDateCount = 0;
  const dateCol = dataset === 'telemetry' ? 'timestamp' : null;
  if (dateCol && cols.includes(dateCol)) {
    rows.forEach(row => {
      const d = row[dateCol]?.trim();
      if (!d || isNaN(Date.parse(d))) invalidDateCount++;
    });
  }

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
    dataset,
    totalRows: total,
    nullCount,
    duplicateCount,
    invalidVinCount,
    invalidDateCount,
    rangeViolationCount,
    referentialErrorCount: 0,
    score,
    columnStats,
    source: 'browser',
  };
}

function mapBackendReport(data: any, filename?: string): ValidationResult {
  const report = data.bmw_data_quality_report || {};
  const recSummary = report.record_summary || {};
  const checks = report.quality_checks || {};
  const s3 = data.s3_paths ?? {};

  const rawNullList = report.null_analysis ?? data.null_summary ?? [];
  const nullSummary = rawNullList.map((s: any) => ({
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
    filename,
    runId:                 data.run_id,
  };
}

export default function ValidatePage() {
  const { refreshHistory, setSelectedRunId, setDatasetFilter } = usePipeline();
  const [targetDataset, setTargetDataset] = useState<'telemetry' | 'vehicle_master'>('telemetry');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [validating, setValidating] = useState(false);
  const [result, setResult] = useState<ValidationResult | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = (file: File) => {
    if (!file.name.endsWith('.csv')) {
      setErrorMsg('Please upload a .csv file');
      return;
    }
    setSelectedFile(file);
    setResult(null);
    setErrorMsg(null);

    // Auto-select target dataset based on filename as a convenience
    if (file.name.toLowerCase().includes('vehicle')) {
      setTargetDataset('vehicle_master');
    } else if (file.name.toLowerCase().includes('telemetry')) {
      setTargetDataset('telemetry');
    }
  };

  const onDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files?.[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const onFileInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleValidate = async () => {
    if (!selectedFile) return;
    setValidating(true);
    setErrorMsg(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('dataset', targetDataset);

      const resp = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (resp.ok) {
        const data = await resp.json();
        const mapped = mapBackendReport(data, selectedFile.name);
        setResult(mapped);
        setDatasetFilter(targetDataset);
        if (data.run_id) setSelectedRunId(data.run_id);
        await refreshHistory();
        setValidating(false);
        return;
      }
      const err = await resp.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Backend validation returned error');
    } catch (backendErr: any) {
      console.warn('Backend upload failed, falling back to in-browser validation:', backendErr);
      // Browser fallback
      Papa.parse<Record<string, string>>(selectedFile, {
        header: true,
        skipEmptyLines: true,
        complete: parsed => {
          try {
            const res = validateInBrowser(parsed.data, targetDataset);
            res.filename = selectedFile.name;
            setResult(res);
          } catch (e: any) {
            setErrorMsg(`Validation error: ${e.message}`);
          } finally {
            setValidating(false);
          }
        },
        error: parseErr => {
          setErrorMsg(`CSV parse error: ${parseErr.message}`);
          setValidating(false);
        },
      });
    }
  };

  const scoreLabel = result ? getScoreLabel(result.score) : '-';
  const scoreColor = result ? getScoreColor(result.score) : 'var(--text-muted)';

  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1>Dataset Validation & Ingestion</h1>
          <p>Validate CSV datasets against governance rules, segregate invalid records, and upload to S3</p>
        </div>
      </div>

      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {/* Step 1: Target dataset selection */}
        <div className="card">
          <div className="card-header">
            <h3>1. Select Target Dataset</h3>
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Choose storage partition</span>
          </div>
          <div className="card-body">
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <label
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.75rem',
                  padding: '1rem',
                  background: targetDataset === 'telemetry' ? 'rgba(0, 102, 204, 0.12)' : 'var(--bg-secondary)',
                  border: targetDataset === 'telemetry' ? '1px solid var(--bmw-blue-bright)' : '1px solid var(--border-subtle)',
                  borderRadius: 8,
                  cursor: 'pointer',
                }}
              >
                <input
                  type="radio"
                  name="target_dataset"
                  value="telemetry"
                  checked={targetDataset === 'telemetry'}
                  onChange={() => setTargetDataset('telemetry')}
                  style={{ marginTop: 3 }}
                />
                <div>
                  <div style={{ fontWeight: 700, fontSize: 14, color: 'var(--text-primary)' }}>
                    Telemetry (raw/telemetry/)
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
                    Event streams (speed, battery, temperature, GPS). Validates schema, ranges, dates, VIN, and foreign key against vehicle master.
                  </div>
                </div>
              </label>

              <label
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.75rem',
                  padding: '1rem',
                  background: targetDataset === 'vehicle_master' ? 'rgba(0, 102, 204, 0.12)' : 'var(--bg-secondary)',
                  border: targetDataset === 'vehicle_master' ? '1px solid var(--bmw-blue-bright)' : '1px solid var(--border-subtle)',
                  borderRadius: 8,
                  cursor: 'pointer',
                }}
              >
                <input
                  type="radio"
                  name="target_dataset"
                  value="vehicle_master"
                  checked={targetDataset === 'vehicle_master'}
                  onChange={() => setTargetDataset('vehicle_master')}
                  style={{ marginTop: 3 }}
                />
                <div>
                  <div style={{ fontWeight: 700, fontSize: 14, color: 'var(--text-primary)' }}>
                    Vehicle Master (raw/vehicle_master/)
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
                    Vehicle fleet master table (vehicle_id, VIN, model, year, region, status). Used as reference catalog for foreign key checks.
                  </div>
                </div>
              </label>
            </div>
          </div>
        </div>

        {/* Step 2: Upload dropzone */}
        <div className="card">
          <div className="card-header">
            <h3>2. Upload CSV File</h3>
            {selectedFile && (
              <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                {selectedFile.name} · {(selectedFile.size / 1024).toFixed(1)} KB
              </span>
            )}
          </div>
          <div className="card-body">
            <div
              className={`dropzone ${dragOver ? 'drag-over' : ''}`}
              onDragOver={e => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={onDrop}
              onClick={() => fileInputRef.current?.click()}
              id="csv-dropzone"
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                style={{ display: 'none' }}
                onChange={onFileInputChange}
              />
              <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)' }}>
                {selectedFile ? selectedFile.name : 'Select or Drop BMW CSV File'}
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
                Target partition: <strong style={{ color: 'var(--bmw-blue-bright)' }}>{targetDataset}</strong> · Maximum size: 50MB
              </div>
            </div>

            {errorMsg && (
              <div style={{ marginTop: '0.75rem', padding: '0.5rem 0.75rem', background: 'rgba(255,71,87,0.12)', border: '1px solid rgba(255,71,87,0.3)', borderRadius: 6, color: 'var(--color-critical)', fontSize: 13 }}>
                {errorMsg}
              </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem', gap: '0.75rem' }}>
              {selectedFile && (
                <button
                  type="button"
                  className="btn btn-ghost"
                  onClick={() => { setSelectedFile(null); setResult(null); setErrorMsg(null); }}
                >
                  Clear
                </button>
              )}
              <button
                type="button"
                className="btn btn-primary"
                disabled={!selectedFile || validating}
                onClick={handleValidate}
                id="validate-btn"
              >
                {validating ? 'Processing Quality Pipeline...' : `Validate & Ingest to ${targetDataset}`}
              </button>
            </div>
          </div>
        </div>

        {/* Step 3: Result Summary */}
        {result && (
          <div className="card" style={{ animation: 'countUp 0.35s ease' }}>
            <div className="card-header">
              <h3>Validation Results — {result.filename ?? result.dataset}</h3>
              <span className={`badge badge-${scoreLabel.toLowerCase()}`}>{scoreLabel}</span>
            </div>
            <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
                <div style={{ padding: '1rem', background: 'var(--bg-secondary)', borderRadius: 8, border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
                  <div style={{ fontSize: 32, fontWeight: 900, color: scoreColor }}>{result.score.toFixed(1)}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Quality Score</div>
                </div>
                <div style={{ padding: '1rem', background: 'var(--bg-secondary)', borderRadius: 8, border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
                  <div style={{ fontSize: 32, fontWeight: 900, color: 'var(--text-primary)' }}>{fmt(result.totalRows)}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Total Records</div>
                </div>
                <div style={{ padding: '1rem', background: 'var(--bg-secondary)', borderRadius: 8, border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
                  <div style={{ fontSize: 32, fontWeight: 900, color: 'var(--color-excellent)' }}>
                    {fmt(result.totalRows - (result.nullCount + result.duplicateCount + result.invalidVinCount + result.invalidDateCount + result.rangeViolationCount + result.referentialErrorCount))}
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Valid Records</div>
                </div>
                <div style={{ padding: '1rem', background: 'var(--bg-secondary)', borderRadius: 8, border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
                  <div style={{ fontSize: 32, fontWeight: 900, color: 'var(--color-critical)' }}>
                    {fmt(result.nullCount + result.duplicateCount + result.invalidVinCount + result.invalidDateCount + result.rangeViolationCount + result.referentialErrorCount)}
                  </div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Violations</div>
                </div>
              </div>

              {/* Checks breakdown */}
              <div className="data-table-wrap">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Quality Check Rule</th>
                      <th>Violations</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Null Value Check</td>
                      <td>{fmt(result.nullCount)}</td>
                      <td style={{ color: result.nullCount > 0 ? 'var(--color-critical)' : 'var(--color-excellent)' }}>
                        {result.nullCount > 0 ? 'FAIL' : 'PASS'}
                      </td>
                    </tr>
                    <tr>
                      <td>Duplicate Record Detection</td>
                      <td>{fmt(result.duplicateCount)}</td>
                      <td style={{ color: result.duplicateCount > 0 ? 'var(--color-critical)' : 'var(--color-excellent)' }}>
                        {result.duplicateCount > 0 ? 'FAIL' : 'PASS'}
                      </td>
                    </tr>
                    <tr>
                      <td>VIN Format Verification (ISO 3779)</td>
                      <td>{fmt(result.invalidVinCount)}</td>
                      <td style={{ color: result.invalidVinCount > 0 ? 'var(--color-critical)' : 'var(--color-excellent)' }}>
                        {result.invalidVinCount > 0 ? 'FAIL' : 'PASS'}
                      </td>
                    </tr>
                    <tr>
                      <td>Date / Timestamp Parsing</td>
                      <td>{fmt(result.invalidDateCount)}</td>
                      <td style={{ color: result.invalidDateCount > 0 ? 'var(--color-critical)' : 'var(--color-excellent)' }}>
                        {result.invalidDateCount > 0 ? 'FAIL' : 'PASS'}
                      </td>
                    </tr>
                    <tr>
                      <td>Out-of-Range Sensor Boundaries</td>
                      <td>{fmt(result.rangeViolationCount)}</td>
                      <td style={{ color: result.rangeViolationCount > 0 ? 'var(--color-critical)' : 'var(--color-excellent)' }}>
                        {result.rangeViolationCount > 0 ? 'FAIL' : 'PASS'}
                      </td>
                    </tr>
                    <tr>
                      <td>Referential Integrity (vehicle_master)</td>
                      <td>{fmt(result.referentialErrorCount)}</td>
                      <td style={{ color: result.referentialErrorCount > 0 ? 'var(--color-critical)' : 'var(--color-excellent)' }}>
                        {result.referentialErrorCount > 0 ? 'FAIL' : 'PASS'}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* S3 Output Paths */}
              <div style={{ padding: '0.875rem 1rem', background: 'var(--bg-secondary)', borderRadius: 8, border: '1px solid var(--border-subtle)', fontSize: 12, display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                <div style={{ fontWeight: 700, color: 'var(--text-primary)', marginBottom: 2 }}>Storage Destinations</div>
                <div>Curated: <span style={{ fontFamily: 'monospace', color: 'var(--bmw-blue-bright)' }}>{result.curatedPath ?? '-'}</span></div>
                <div>Quarantine: <span style={{ fontFamily: 'monospace', color: 'var(--color-critical)' }}>{result.quarantinePath ?? '-'}</span></div>
                <div>Report: <span style={{ fontFamily: 'monospace', color: 'var(--text-secondary)' }}>{result.reportPath ?? '-'}</span></div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
