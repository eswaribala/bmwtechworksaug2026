import { useState, useEffect } from 'react';
import FileFilter from '../components/FileFilter';
import { usePipeline, API_URL } from '../context/PipelineContext';
import { getScoreColor, getScoreLabel, fmt } from '../utils/constants';

export default function ReportPage() {
  const { selectedRun, s3Bucket, datasetFilter } = usePipeline();
  const [reportData, setReportData] = useState<any>(null);
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selectedRun?.run_id) {
      setReportData(null);
      return;
    }
    setLoading(true);
    fetch(`${API_URL}/api/history/${selectedRun.run_id}`)
      .then(r => (r.ok ? r.json() : null))
      .then(d => setReportData(d))
      .catch(() => setReportData(null))
      .finally(() => setLoading(false));
  }, [selectedRun?.run_id]);

  const hasData = Boolean(reportData);
  const rep = reportData?.bmw_data_quality_report ?? reportData ?? {};
  const rec = rep?.record_summary ?? reportData ?? {};
  const chk = rep?.quality_checks ?? reportData ?? {};

  const score = hasData ? (reportData.quality_score ?? rep.quality_score ?? null) : null;
  const label = hasData ? (reportData.score_label ?? rep.score_label ?? getScoreLabel(score)) : '-';
  const scoreColor = getScoreColor(score);
  const textReport = reportData?.text_report ?? '';

  const total = hasData ? (reportData.total_records ?? rec.total_records ?? null) : null;
  const valid = hasData ? (reportData.valid_records ?? rec.valid_records ?? null) : null;
  const rejected = hasData ? (reportData.rejected_records ?? rec.rejected_records ?? null) : null;
  const duration = hasData && typeof reportData.duration_seconds === 'number'
    ? `${reportData.duration_seconds.toFixed(3)}s`
    : '-';
  const execTime = hasData && reportData.execution_time
    ? reportData.execution_time.slice(0, 19).replace('T', ' ')
    : '-';

  const downloadText = () => {
    if (!textReport) return;
    const blob = new Blob([textReport], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bmw_quality_report_${selectedRun?.run_id ?? datasetFilter}.txt`;
    a.click();
  };

  const downloadJSON = () => {
    if (!reportData) return;
    const json = JSON.stringify(reportData, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bmw_quality_report_${selectedRun?.run_id ?? datasetFilter}.json`;
    a.click();
  };

  const copyText = () => {
    if (!textReport) return;
    navigator.clipboard.writeText(textReport);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const reportS3Path = s3Bucket !== '-'
    ? `s3://${s3Bucket}/reports/${datasetFilter}/`
    : 'output/reports/';

  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1>Quality Report</h1>
          <p>
            Certified quality report artifact · Destination: {reportS3Path}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            className="btn btn-ghost"
            onClick={copyText}
            disabled={!textReport}
            id="copy-report-btn"
          >
            {copied ? 'Copied' : 'Copy Text'}
          </button>
          <button
            className="btn btn-ghost"
            onClick={downloadText}
            disabled={!textReport}
            id="download-txt-btn"
          >
            Download TXT
          </button>
          <button
            className="btn btn-primary"
            onClick={downloadJSON}
            disabled={!reportData}
            id="download-json-btn"
          >
            Download JSON
          </button>
        </div>
      </div>

      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        <FileFilter />

        {/* Score hero */}
        <div className="card" style={{ background: `linear-gradient(135deg, var(--bg-secondary), rgba(0,102,204,0.08))` }}>
          <div className="card-body">
            <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr auto', alignItems: 'center', gap: '2rem' }}>
              <div style={{ textAlign: 'center', minWidth: 140 }}>
                <div style={{ fontSize: 64, fontWeight: 900, color: scoreColor, lineHeight: 1 }}>
                  {score !== null ? score.toFixed(1) : '-'}
                </div>
                <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 4 }}>/ 100 Score</div>
              </div>
              <div>
                <div style={{ fontSize: 22, fontWeight: 700, marginBottom: 6 }}>
                  BMW Data Quality Report
                </div>
                <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 12 }}>
                  Dataset: {selectedRun?.dataset ?? datasetFilter} · File: {selectedRun?.filename ?? '-'} · Execution: {execTime} · Duration: {duration}
                </div>
                <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                  {[
                    ['Total', fmt(total), 'var(--text-primary)'],
                    ['Valid', fmt(valid), '#00C48C'],
                    ['Invalid', fmt(rejected), '#FF4757'],
                  ].map(([lbl, val, col]) => (
                    <div
                      key={String(lbl)}
                      style={{
                        textAlign: 'center',
                        padding: '0.5rem 1rem',
                        background: 'var(--bg-glass)',
                        borderRadius: 8,
                        border: '1px solid var(--border-subtle)',
                        minWidth: 100,
                      }}
                    >
                      <div style={{ fontSize: 18, fontWeight: 800, color: String(col) }}>{val}</div>
                      <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase' }}>{lbl}</div>
                    </div>
                  ))}
                </div>
              </div>
              <div style={{ textAlign: 'center', minWidth: 140 }}>
                <div
                  className={`badge ${label !== '-' ? `badge-${label.toLowerCase()}` : ''}`}
                  style={{ fontSize: 14, padding: '0.4rem 1.1rem', display: 'inline-block' }}
                >
                  {label}
                </div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 6 }}>Quality Tier</div>
              </div>
            </div>
          </div>
        </div>

        {/* Text report view */}
        <div className="card">
          <div className="card-header">
            <h3>Standard Quality Report Document</h3>
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Generated text format</span>
          </div>
          <div className="card-body">
            {textReport ? (
              <pre
                style={{
                  background: 'var(--bg-secondary)',
                  padding: '1.25rem',
                  borderRadius: 8,
                  border: '1px solid var(--border-subtle)',
                  fontFamily: 'monospace',
                  fontSize: 12,
                  lineHeight: 1.6,
                  color: 'var(--text-primary)',
                  overflowX: 'auto',
                }}
              >
                {textReport}
              </pre>
            ) : (
              <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
                {loading ? 'Loading report...' : '- No quality report available for the selected file -'}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
