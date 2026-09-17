import { useEffect, useState } from 'react';
import KpiCard from '../components/KpiCard';
import ScoreGauge from '../components/ScoreGauge';
import FileFilter from '../components/FileFilter';
import { usePipeline, API_URL } from '../context/PipelineContext';
import { ERROR_TYPE_COLORS, fmt, fmtPct, getScoreLabel } from '../utils/constants';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, Legend
} from 'recharts';

export default function Dashboard() {
  const { selectedRun, backendOnline } = usePipeline();
  const [detail, setDetail] = useState<any>(null);

  useEffect(() => {
    if (!selectedRun?.run_id) {
      setDetail(null);
      return;
    }
    let isCurrent = true;
    fetch(`${API_URL}/api/history/${selectedRun.run_id}`)
      .then(res => (res.ok ? res.json() : null))
      .then(data => {
        if (isCurrent) setDetail(data);
      })
      .catch(() => {
        if (isCurrent) setDetail(null);
      });
    return () => {
      isCurrent = false;
    };
  }, [selectedRun?.run_id]);

  const hasData = Boolean(selectedRun && detail);
  const total = hasData ? detail.total_records : null;
  const valid = hasData ? detail.valid_records : null;
  const rejected = hasData ? detail.rejected_records : null;
  const score = hasData ? detail.quality_score : null;
  const label = hasData ? (detail.score_label ?? getScoreLabel(score)) : '-';
  const duration = hasData && typeof detail.duration_seconds === 'number' ? `${detail.duration_seconds.toFixed(3)}s` : '-';
  const execTime = hasData && detail.execution_time ? detail.execution_time.slice(0, 19).replace('T', ' ') : '-';

  const validRate = hasData && total && total > 0 ? (valid / total) * 100 : null;
  const rejectRate = hasData && total && total > 0 ? (rejected / total) * 100 : null;

  const donutData = hasData
    ? [
        { name: 'Valid Records', value: valid ?? 0, color: '#00C48C' },
        { name: 'Rejected Records', value: rejected ?? 0, color: '#FF4757' },
      ]
    : [
        { name: 'No Data', value: 1, color: '#2a3342' },
      ];

  const errorBreakdown = hasData
    ? [
        { name: 'Null Values', count: detail.null_count ?? 0, color: ERROR_TYPE_COLORS.NULL_VALUE },
        { name: 'Duplicates', count: detail.duplicate_count ?? 0, color: ERROR_TYPE_COLORS.DUPLICATE_RECORD },
        { name: 'Invalid VIN', count: detail.invalid_vin_count ?? 0, color: ERROR_TYPE_COLORS.INVALID_VIN },
        { name: 'Invalid Dates', count: detail.invalid_date_count ?? 0, color: ERROR_TYPE_COLORS.INVALID_DATE },
        { name: 'Out-of-Range', count: detail.range_violation_count ?? 0, color: ERROR_TYPE_COLORS.OUT_OF_RANGE },
        { name: 'Ref. Integrity', count: detail.referential_error_count ?? 0, color: ERROR_TYPE_COLORS.REFERENTIAL_INTEGRITY },
      ]
    : [];

  const penaltyBreakdownObj = hasData && detail.penalty_breakdown ? detail.penalty_breakdown : {};
  const penaltyData = Object.entries(penaltyBreakdownObj).map(([k, v]: [string, any]) => ({
    name: k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
    penalty: typeof v.penalty === 'number' ? v.penalty : 0,
    weight: typeof v.weight === 'number' ? v.weight : 0,
  }));

  const totalViolations = hasData
    ? (detail.null_count ?? 0) +
      (detail.duplicate_count ?? 0) +
      (detail.invalid_vin_count ?? 0) +
      (detail.invalid_date_count ?? 0) +
      (detail.range_violation_count ?? 0) +
      (detail.referential_error_count ?? 0)
    : null;

  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1>Data Quality Dashboard</h1>
          <p>
            Real-time quality metrics for validated BMW datasets · File: {selectedRun?.filename ?? '-'} · {execTime}
          </p>
        </div>
        <div className="flex gap-2 items-center">
          <div className={`page-header-badge ${hasData ? 'badge-excellent' : ''}`}>
            <span>Status</span> {backendOnline ? (hasData ? 'Ready' : 'Awaiting Data') : 'Backend Offline'}
          </div>
        </div>
      </div>

      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        <FileFilter />

        {!hasData && (
          <div className="card card-body" style={{ textAlign: 'center', padding: '2rem 1rem' }}>
            <h3 style={{ fontSize: 16, marginBottom: 6 }}>
              {backendOnline ? 'No Processed Records Found for this Dataset' : 'Backend Server Not Connected'}
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: 13, maxWidth: 520, margin: '0 auto' }}>
              {backendOnline
                ? 'Upload a CSV file in the Validate page or run the pipeline via CLI to view quality metrics.'
                : 'Start the FastAPI backend server (port 8000) to load live validation results.'}
            </p>
          </div>
        )}

        {/* KPI Row */}
        <div className="kpi-grid">
          <KpiCard
            label="Total Records"
            value={total}
            color="var(--bmw-blue-bright)"
            sub={hasData ? `File: ${selectedRun?.filename}` : 'Dataset unavailable'}
          />
          <KpiCard
            label="Valid Records"
            value={valid}
            color="var(--color-excellent)"
            sub={hasData ? 'Passed all checks' : '-'}
          />
          <KpiCard
            label="Rejected Records"
            value={rejected}
            color="var(--color-critical)"
            sub={hasData ? 'Quarantine zone' : '-'}
          />
          <KpiCard
            label="Quality Score"
            value={score}
            format="score"
            color={score !== null && score >= 90 ? 'var(--color-excellent)' : 'var(--color-acceptable)'}
            unit={score !== null ? '/ 100' : ''}
            sub={label}
          />
        </div>

        {/* Score Gauge + Donut */}
        <div className="charts-grid">
          <div className="card">
            <div className="card-header">
              <h3>Data Quality Score</h3>
              <span className={`badge ${label !== '-' ? `badge-${label.toLowerCase()}` : ''}`}>{label}</span>
            </div>
            <div className="card-body">
              <ScoreGauge score={score} label={label} />
              <div style={{ textAlign: 'center', marginTop: '0.5rem', fontSize: 12, color: 'var(--text-secondary)' }}>
                Processing time: {duration} · Records: {fmt(total)}
              </div>
            </div>
          </div>

          <div className="card">
            <div className="card-header"><h3>Record Distribution</h3></div>
            <div className="card-body">
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie dataKey="value" data={donutData} cx="50%" cy="50%" innerRadius={55} outerRadius={85} paddingAngle={4} stroke="none">
                    {donutData.map((d, i) => <Cell key={i} fill={d.color} />)}
                  </Pie>
                  <Tooltip contentStyle={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', borderRadius: 8 }} />
                  {hasData && <Legend formatter={(v) => <span style={{ color: 'var(--text-secondary)', fontSize: 12 }}>{v}</span>} />}
                </PieChart>
              </ResponsiveContainer>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginTop: '0.5rem' }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 22, fontWeight: 800, color: '#00C48C' }}>{fmtPct(validRate)}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Valid Rate</div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 22, fontWeight: 800, color: '#FF4757' }}>{fmtPct(rejectRate)}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Rejection Rate</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Error Breakdown Bar */}
        <div className="card">
          <div className="card-header">
            <h3>Quality Issue Breakdown</h3>
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              {totalViolations !== null ? `${fmt(totalViolations)} total violations` : '-'}
            </span>
          </div>
          <div className="card-body">
            {hasData && errorBreakdown.length > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={errorBreakdown} margin={{ top: 0, right: 20, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
                  <XAxis dataKey="name" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
                  <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
                  <Tooltip contentStyle={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', borderRadius: 8 }} />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {errorBreakdown.map((d, i) => <Cell key={i} fill={d.color} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
                - No violation breakdown available -
              </div>
            )}
          </div>
        </div>

        {/* Penalty Breakdown */}
        {hasData && penaltyData.length > 0 && (
          <div className="card">
            <div className="card-header"><h3>Scoring Penalty Analysis</h3></div>
            <div className="card-body" style={{ padding: 0 }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Check Type</th>
                    <th>Weight</th>
                    <th>Penalty Deducted</th>
                  </tr>
                </thead>
                <tbody>
                  {penaltyData.map(p => (
                    <tr key={p.name}>
                      <td>{p.name}</td>
                      <td>{p.weight}%</td>
                      <td style={{ color: p.penalty > 0 ? 'var(--color-critical)' : 'var(--color-excellent)' }}>
                        -{p.penalty.toFixed(3)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
