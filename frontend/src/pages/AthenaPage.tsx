import { useState } from 'react';
import { ATHENA_QUERIES } from '../data/mockData';

export default function AthenaPage() {
  const [selectedQuery, setSelectedQuery] = useState(0);
  const [sql, setSql] = useState(ATHENA_QUERIES[0].sql);
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState<Record<string, string | number>[] | null>(null);
  const [duration, setDuration] = useState<string | null>(null);

  function runQuery() {
    setRunning(true);
    setResults(null);
    const start = Date.now();
    setTimeout(() => {
      // Find which preset query matches (or return first)
      const match = ATHENA_QUERIES.find(q => sql.trim().startsWith(q.sql.trim().slice(0, 20)));
      setResults((match ?? ATHENA_QUERIES[selectedQuery]).results);
      setDuration(((Date.now() - start) / 1000).toFixed(3) + 's');
      setRunning(false);
    }, 1200);
  }

  function loadPreset(idx: number) {
    setSelectedQuery(idx);
    setSql(ATHENA_QUERIES[idx].sql);
    setResults(null);
    setDuration(null);
  }

  const columns = results && results.length > 0 ? Object.keys(results[0]) : [];

  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1>Athena Query Explorer</h1>
          <p>Query curated BMW datasets using Amazon Athena SQL — simulated results from in-memory data</p>
        </div>
        <div className="page-header-badge" style={{ background: 'rgba(0,102,204,0.12)', color: 'var(--bmw-blue-bright)', border: '1px solid rgba(0,102,204,0.3)' }}>
          🔎 Athena
        </div>
      </div>

      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

        {/* Preset queries */}
        <div className="card">
          <div className="card-header"><h3>Preset Queries</h3></div>
          <div className="card-body">
            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              {ATHENA_QUERIES.map((q, i) => (
                <button
                  key={i}
                  className={`btn ${selectedQuery === i ? 'btn-primary' : 'btn-ghost'}`}
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
              {duration && <span style={{ fontSize: 12, color: 'var(--color-excellent)' }}>⏱ {duration}</span>}
              <button className="btn btn-primary" onClick={runQuery} disabled={running} id="run-query-btn">
                {running ? '⏳ Executing…' : '▶ Run Query'}
              </button>
            </div>
          </div>
          <div className="card-body">
            <textarea
              id="sql-editor"
              className="sql-editor"
              value={sql}
              onChange={e => { setSql(e.target.value); setResults(null); }}
              spellCheck={false}
            />
            <div style={{ marginTop: 8, fontSize: 11, color: 'var(--text-muted)' }}>
              Database: <span style={{ color: 'var(--bmw-blue-bright)' }}>bmw_data_quality</span> ·
              Region: <span style={{ color: 'var(--bmw-blue-bright)' }}>eu-central-1</span> ·
              Output: <span style={{ color: 'var(--bmw-blue-bright)' }}>s3://bmw-data-quality/reports/athena/</span>
            </div>
          </div>
        </div>

        {/* Results */}
        {running && (
          <div className="card card-body">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>Executing query against curated dataset…</div>
              <div className="progress-bar-wrap">
                <div className="progress-bar-fill" style={{ width: '70%', animation: 'shimmer 1s infinite', backgroundSize: '200% 100%' }} />
              </div>
            </div>
          </div>
        )}

        {results && (
          <div className="card" style={{ animation: 'countUp 0.4s ease' }}>
            <div className="card-header">
              <h3>Query Results</h3>
              <div className="flex gap-3 items-center">
                <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{results.length} rows · {duration}</span>
                <button
                  className="btn btn-ghost"
                  style={{ fontSize: 11 }}
                  onClick={() => {
                    const csv = [columns.join(','), ...results.map(r => columns.map(c => r[c]).join(','))].join('\n');
                    const blob = new Blob([csv], { type: 'text/csv' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a'); a.href = url; a.download = 'athena_results.csv'; a.click();
                  }}
                  id="download-results-btn"
                >
                  ⬇ Export CSV
                </button>
              </div>
            </div>
            <div className="card-body" style={{ padding: 0 }}>
              <div className="data-table-wrap">
                <table className="data-table">
                  <thead>
                    <tr>{columns.map(c => <th key={c}>{c}</th>)}</tr>
                  </thead>
                  <tbody>
                    {results.map((row, i) => (
                      <tr key={i}>
                        {columns.map(c => (
                          <td key={c} className={typeof row[c] === 'number' ? '' : 'monospace'}>
                            {typeof row[c] === 'number' ? Number(row[c]).toLocaleString() : String(row[c])}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Schema reference */}
        <div className="card">
          <div className="card-header"><h3>Available Tables (Glue Catalog)</h3></div>
          <div className="card-body" style={{ padding: 0 }}>
            <table className="data-table">
              <thead>
                <tr><th>Table Name</th><th>Columns</th><th>Format</th><th>Location</th></tr>
              </thead>
              <tbody>
                {[
                  { name: 'bmw_vehicle_master',   cols: 'vehicle_id, vin, model, model_year, region, status',    fmt: 'Parquet', loc: 's3://bmw-data-quality/curated/vehicle_master/' },
                  { name: 'bmw_telemetry',        cols: 'event_id, vehicle_id, vin, timestamp, battery_level, speed, temperature, latitude, longitude', fmt: 'Parquet', loc: 's3://bmw-data-quality/curated/telemetry/' },
                  { name: 'data_quality_reports', cols: 'dataset_name, quality_score, total_records, valid_records, rejected_records, execution_timestamp', fmt: 'Parquet', loc: 's3://bmw-data-quality/reports/' },
                ].map(t => (
                  <tr key={t.name}>
                    <td className="monospace" style={{ color: 'var(--bmw-blue-bright)' }}>{t.name}</td>
                    <td style={{ fontSize: 11, maxWidth: 300 }} className="monospace truncate">{t.cols}</td>
                    <td><span className="badge badge-good">{t.fmt}</span></td>
                    <td className="monospace" style={{ fontSize: 10, color: 'var(--text-muted)' }}>{t.loc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
