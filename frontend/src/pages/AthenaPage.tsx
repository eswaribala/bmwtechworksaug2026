import { useState } from 'react';
import { usePipeline, API_URL } from '../context/PipelineContext';
import { ATHENA_PRESET_QUERIES, fmt } from '../utils/constants';
import type { AthenaQueryResult } from '../types';

export default function AthenaPage() {
  const { s3Bucket } = usePipeline();
  const [selectedPreset, setSelectedPreset] = useState(0);
  const [sql, setSql] = useState(ATHENA_PRESET_QUERIES[0].sql);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<AthenaQueryResult | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const runQuery = async () => {
    if (!sql.trim()) return;
    setRunning(true);
    setErrorMsg(null);
    try {
      const resp = await fetch(`${API_URL}/api/athena/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sql }),
      });
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.detail ?? 'Athena query execution failed');
      }
      const data: AthenaQueryResult = await resp.json();
      setResult(data);
    } catch (e: any) {
      setErrorMsg(e.message ?? 'Query failed');
      setResult(null);
    } finally {
      setRunning(false);
    }
  };

  const loadPreset = (idx: number) => {
    setSelectedPreset(idx);
    setSql(ATHENA_PRESET_QUERIES[idx].sql);
    setErrorMsg(null);
  };

  const columns = result?.columns ?? [];
  const rows = result?.rows ?? [];
  const outputPath = s3Bucket !== '-'
    ? `s3://${s3Bucket}/reports/athena-results/`
    : 'output/reports/';

  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1>Athena Query Explorer</h1>
          <p>
            Execute SQL queries directly against curated BMW datasets in Amazon Athena
          </p>
        </div>
        <div className="page-header-badge">
          <span>Athena Workgroup</span> bmw-data-quality
        </div>
      </div>

      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {/* Preset Queries */}
        <div className="card">
          <div className="card-header">
            <h3>Preset SQL Queries</h3>
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Curated & Quarantine analytics</span>
          </div>
          <div className="card-body">
            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              {ATHENA_PRESET_QUERIES.map((q, i) => (
                <button
                  key={i}
                  type="button"
                  className={`btn ${selectedPreset === i ? 'btn-primary' : 'btn-ghost'}`}
                  onClick={() => loadPreset(i)}
                  id={`preset-query-${i}`}
                >
                  {q.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* SQL Editor */}
        <div className="card">
          <div className="card-header">
            <h3>SQL Editor</h3>
            <div className="flex gap-2 items-center">
              {result && (
                <span style={{ fontSize: 12, color: 'var(--color-excellent)' }}>
                  Execution: {result.duration} · {fmt(result.rowCount)} rows
                </span>
              )}
              <button
                type="button"
                className="btn btn-primary"
                onClick={runQuery}
                disabled={running}
                id="run-query-btn"
              >
                {running ? 'Executing Query...' : 'Run Query'}
              </button>
            </div>
          </div>
          <div className="card-body">
            <textarea
              id="sql-editor"
              className="sql-editor"
              value={sql}
              onChange={e => {
                setSql(e.target.value);
                setErrorMsg(null);
              }}
              spellCheck={false}
              rows={8}
            />
            <div style={{ marginTop: 8, fontSize: 11, color: 'var(--text-muted)' }}>
              Database: <span style={{ color: 'var(--bmw-blue-bright)' }}>bmw_data_quality</span> · Region: <span style={{ color: 'var(--bmw-blue-bright)' }}>eu-central-1</span> · Results: <span style={{ color: 'var(--bmw-blue-bright)' }}>{outputPath}</span>
            </div>
          </div>
        </div>

        {errorMsg && (
          <div style={{ padding: '0.875rem 1rem', background: 'rgba(255,71,87,0.12)', border: '1px solid rgba(255,71,87,0.3)', borderRadius: 8, color: 'var(--color-critical)', fontSize: 13 }}>
            {errorMsg}
          </div>
        )}

        {/* Results */}
        {running && (
          <div className="card card-body">
            <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
              Executing SQL against curated data lake...
            </div>
          </div>
        )}

        {result && !running && (
          <div className="card">
            <div className="card-header">
              <h3>Query Results</h3>
              <div className="flex gap-3 items-center">
                <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                  {fmt(result.rowCount)} rows returned in {result.duration}
                </span>
                <button
                  type="button"
                  className="btn btn-ghost"
                  style={{ fontSize: 11 }}
                  onClick={() => {
                    if (rows.length === 0) return;
                    const csv = [
                      columns.join(','),
                      ...rows.map(r => columns.map(c => JSON.stringify(r[c] ?? '')).join(',')),
                    ].join('\n');
                    const blob = new Blob([csv], { type: 'text/csv' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'athena_results.csv';
                    a.click();
                  }}
                  id="download-results-btn"
                >
                  Export CSV
                </button>
              </div>
            </div>
            <div className="card-body" style={{ padding: 0 }}>
              {rows.length > 0 ? (
                <div className="data-table-wrap">
                  <table className="data-table">
                    <thead>
                      <tr>
                        {columns.map(c => (
                          <th key={c}>{c}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {rows.map((r, i) => (
                        <tr key={i}>
                          {columns.map(c => (
                            <td key={c} className="monospace">
                              {r[c] !== null && r[c] !== undefined && r[c] !== '' ? String(r[c]) : '-'}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div style={{ padding: '2.5rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
                  - Query returned 0 rows -
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
