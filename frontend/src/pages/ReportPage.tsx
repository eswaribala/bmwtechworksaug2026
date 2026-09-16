import { useState } from 'react';
import { DEMO_METRICS } from '../data/mockData';

function generateTextReport(m: typeof DEMO_METRICS): string {
  const sep = '='.repeat(52);
  const div = '-'.repeat(52);
  return [
    sep,
    '        BMW DATA QUALITY REPORT',
    sep,
    '',
    `  Dataset              : ${m.dataset.charAt(0).toUpperCase() + m.dataset.slice(1)}`,
    `  Execution Time       : ${m.execution_time.slice(0,19).replace('T',' ')}`,
    `  Processing Duration  : ${m.duration_seconds.toFixed(3)}s`,
    '',
    div,
    '  RECORD SUMMARY',
    div,
    '',
    `  Total Records        :     ${m.total_records.toLocaleString().padStart(10)}`,
    `  Valid Records        :     ${m.valid_records.toLocaleString().padStart(10)}`,
    `  Rejected Records     :     ${m.rejected_records.toLocaleString().padStart(10)}`,
    '',
    div,
    '  QUALITY CHECKS',
    div,
    '',
    `  Null Issues          :     ${m.checks.null_count.toString().padStart(10)}`,
    `  Duplicate Records    :     ${m.checks.duplicate_count.toString().padStart(10)}`,
    `  Invalid VIN          :     ${m.checks.invalid_vin_count.toString().padStart(10)}`,
    `  Invalid Dates        :     ${m.checks.invalid_date_count.toString().padStart(10)}`,
    `  Out-of-Range Values  :     ${m.checks.range_violation_count.toString().padStart(10)}`,
    `  Referential Errors   :     ${m.checks.referential_error_count.toString().padStart(10)}`,
    '',
    div,
    '  QUALITY SCORE',
    div,
    '',
    `  Score                :      ${m.quality_score.toFixed(1)} / 100`,
    `  Status               :      ${m.score_label}`,
    '',
    sep,
  ].join('\n');
}

export default function ReportPage() {
  const m = DEMO_METRICS;
  const [copied, setCopied] = useState(false);
  const textReport = generateTextReport(m);

  const downloadText = () => {
    const blob = new Blob([textReport], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = 'bmw_quality_report.txt'; a.click();
  };

  const downloadJSON = () => {
    const json = JSON.stringify({ bmw_data_quality_report: m }, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = 'bmw_quality_report.json'; a.click();
  };

  const copyText = () => {
    navigator.clipboard.writeText(textReport);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const scoreColor = m.quality_score >= 90 ? '#00C48C' : m.quality_score >= 80 ? '#0066CC' : m.quality_score >= 70 ? '#FFA500' : '#FF4757';

  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1>Quality Report</h1>
          <p>Generated BMW Data Quality Report — s3://bmw-data-quality/reports/</p>
        </div>
        <div className="flex gap-2">
          <button className="btn btn-ghost" onClick={copyText} id="copy-report-btn">{copied ? '✓ Copied' : '📋 Copy'}</button>
          <button className="btn btn-ghost" onClick={downloadText} id="download-txt-btn">⬇ TXT</button>
          <button className="btn btn-primary" onClick={downloadJSON} id="download-json-btn">⬇ JSON</button>
        </div>
      </div>

      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

        {/* Score hero */}
        <div className="card" style={{ background: `linear-gradient(135deg, var(--bg-secondary), rgba(0,102,204,0.1))` }}>
          <div className="card-body">
            <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr auto', alignItems: 'center', gap: '2rem' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 72, fontWeight: 900, color: scoreColor, lineHeight: 1 }}>{m.quality_score}</div>
                <div style={{ fontSize: 14, color: 'var(--text-muted)' }}>/ 100</div>
              </div>
              <div>
                <div style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>BMW Data Quality Score</div>
                <div style={{ fontSize: 14, color: 'var(--text-secondary)', marginBottom: 12 }}>
                  Dataset: {m.dataset} · Execution: {m.execution_time.slice(0,10)} · Duration: {m.duration_seconds}s
                </div>
                <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                  {[
                    ['Total',   m.total_records.toLocaleString(),    'var(--text-primary)'],
                    ['Valid',   m.valid_records.toLocaleString(),     '#00C48C'],
                    ['Invalid', m.rejected_records.toLocaleString(), '#FF4757'],
                  ].map(([label, val, color]) => (
                    <div key={String(label)} style={{ textAlign: 'center', padding: '0.5rem 1rem', background: 'var(--bg-glass)', borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
                      <div style={{ fontSize: 20, fontWeight: 800, color: String(color) }}>{val}</div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase' }}>{label}</div>
                    </div>
                  ))}
                </div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div className={`badge badge-${m.score_label.toLowerCase()}`} style={{ fontSize: 16, padding: '0.5rem 1.25rem', display: 'block', textAlign: 'center' }}>
                  {m.score_label}
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 8 }}>Quality Status</div>
              </div>
            </div>
          </div>
        </div>

        {/* Score interpretation */}
        <div className="card">
          <div className="card-header"><h3>Quality Score Thresholds</h3></div>
          <div className="card-body">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '0.75rem' }}>
              {[
                { range: '90–100', label: 'Excellent', color: '#00C48C' },
                { range: '80–89',  label: 'Good',      color: '#0066CC' },
                { range: '70–79',  label: 'Acceptable',color: '#FFA500' },
                { range: '50–69',  label: 'Poor',       color: '#FF6B35' },
                { range: '0–49',   label: 'Critical',   color: '#FF4757' },
              ].map(s => (
                <div key={s.label} style={{ padding: '0.875rem', background: m.score_label.toUpperCase() === s.label.toUpperCase() ? `${s.color}15` : 'var(--bg-glass)', border: `1px solid ${m.score_label.toUpperCase() === s.label.toUpperCase() ? s.color : 'var(--border-subtle)'}`, borderRadius: 8, textAlign: 'center' }}>
                  <div style={{ fontSize: 18, fontWeight: 800, color: s.color }}>{s.range}</div>
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>{s.label}</div>
                  {m.score_label.toUpperCase() === s.label.toUpperCase() && <div style={{ fontSize: 10, color: s.color, marginTop: 4 }}>◀ CURRENT</div>}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Text report terminal */}
        <div className="card">
          <div className="card-header">
            <h3>Quality Report Output</h3>
            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>BMW standard format</span>
          </div>
          <div className="card-body" style={{ padding: '1rem' }}>
            <pre className="log-terminal" style={{ height: 'auto', maxHeight: 480, whiteSpace: 'pre' }}>
              <span style={{ color: '#a8c5da', fontFamily: 'JetBrains Mono, monospace', fontSize: 12 }}>{textReport}</span>
            </pre>
          </div>
        </div>

        {/* Penalty breakdown table */}
        <div className="card">
          <div className="card-header"><h3>Scoring Breakdown</h3></div>
          <div className="card-body" style={{ padding: 0 }}>
            <table className="data-table">
              <thead>
                <tr><th>Quality Check</th><th>Violations</th><th>Violation Rate</th><th>Weight</th><th>Penalty</th></tr>
              </thead>
              <tbody>
                {Object.entries(m.penalty_breakdown).map(([k, v]) => (
                  <tr key={k}>
                    <td style={{ fontWeight: 500 }}>{k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</td>
                    <td>{v.violations.toLocaleString()}</td>
                    <td>{v.violation_rate_pct.toFixed(2)}%</td>
                    <td>{v.weight}</td>
                    <td style={{ color: v.penalty > 0.2 ? 'var(--color-poor)' : v.penalty > 0 ? 'var(--color-acceptable)' : 'var(--color-excellent)', fontWeight: 700 }}>
                      −{v.penalty.toFixed(4)}
                    </td>
                  </tr>
                ))}
                <tr style={{ fontWeight: 800, background: 'rgba(0,102,204,0.08)' }}>
                  <td colSpan={3} style={{ textAlign: 'right', paddingRight: '1rem' }}>Total Penalty</td>
                  <td>100</td>
                  <td style={{ color: 'var(--color-excellent)' }}>−{(100 - m.quality_score).toFixed(4)}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
