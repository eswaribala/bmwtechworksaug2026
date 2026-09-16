import KpiCard from '../components/KpiCard';
import ScoreGauge from '../components/ScoreGauge';
import { DEMO_METRICS, ERROR_TYPE_COLORS } from '../data/mockData';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, Legend,
  AreaChart, Area
} from 'recharts';

const errorBreakdown = [
  { name: 'Null Values',    count: 210, color: ERROR_TYPE_COLORS.NULL_VALUE },
  { name: 'Duplicates',     count: 150, color: ERROR_TYPE_COLORS.DUPLICATE_RECORD },
  { name: 'Invalid VIN',    count: 80,  color: ERROR_TYPE_COLORS.INVALID_VIN },
  { name: 'Invalid Dates',  count: 60,  color: ERROR_TYPE_COLORS.INVALID_DATE },
  { name: 'Out-of-Range',   count: 50,  color: ERROR_TYPE_COLORS.OUT_OF_RANGE },
  { name: 'Ref. Integrity', count: 30,  color: ERROR_TYPE_COLORS.REFERENTIAL_INTEGRITY },
];

const donutData = [
  { name: 'Valid Records',   value: DEMO_METRICS.valid_records,    color: '#00C48C' },
  { name: 'Rejected Records', value: DEMO_METRICS.rejected_records, color: '#FF4757' },
];

const timelineData = [
  { time: '08:00', score: 88.5 }, { time: '09:00', score: 90.1 },
  { time: '10:00', score: 91.3 }, { time: '11:00', score: 94.2 },
  { time: '12:00', score: 93.8 }, { time: '13:00', score: 95.0 },
  { time: '14:00', score: 94.2 },
];

const penaltyData = Object.entries(DEMO_METRICS.penalty_breakdown).map(([k, v]) => ({
  name: k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
  penalty: v.penalty,
  weight: v.weight,
}));

export default function Dashboard() {
  const m = DEMO_METRICS;

  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1>Data Quality Dashboard</h1>
          <p>Real-time overview of BMW dataset quality metrics · Dataset: Telemetry · {m.execution_time.slice(0,10)}</p>
        </div>
        <div className="flex gap-2 items-center">
          <div className="page-header-badge badge-excellent">
            <span>●</span> Pipeline Healthy
          </div>
          <button className="btn btn-primary">▶ Run Pipeline</button>
        </div>
      </div>

      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

        {/* KPI Row */}
        <div className="kpi-grid">
          <KpiCard label="Total Records"    value={m.total_records}    color="var(--bmw-blue-bright)" sub="from BMW telemetry dataset" />
          <KpiCard label="Valid Records"    value={m.valid_records}    color="var(--color-excellent)" sub="passed all quality checks" />
          <KpiCard label="Rejected Records" value={m.rejected_records} color="var(--color-critical)"  sub="moved to quarantine zone" />
          <KpiCard label="Quality Score"    value={m.quality_score}    color={m.quality_score >= 90 ? 'var(--color-excellent)' : 'var(--color-acceptable)'} unit="/ 100" format="score" sub={m.score_label} />
        </div>

        {/* Score Gauge + Donut */}
        <div className="charts-grid">
          <div className="card">
            <div className="card-header">
              <h3>Data Quality Score</h3>
              <span className={`badge badge-${m.score_label.toLowerCase()}`}>{m.score_label}</span>
            </div>
            <div className="card-body">
              <ScoreGauge score={m.quality_score} label={m.score_label} />
              <div style={{ textAlign: 'center', marginTop: '0.5rem', fontSize: 12, color: 'var(--text-secondary)' }}>
                Processing time: {m.duration_seconds.toFixed(3)}s · {m.total_records.toLocaleString()} records
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
                  <Legend formatter={(v) => <span style={{ color: 'var(--text-secondary)', fontSize: 12 }}>{v}</span>} />
                </PieChart>
              </ResponsiveContainer>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginTop: '0.5rem' }}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 22, fontWeight: 800, color: '#00C48C' }}>{((m.valid_records/m.total_records)*100).toFixed(1)}%</div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Valid Rate</div>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 22, fontWeight: 800, color: '#FF4757' }}>{((m.rejected_records/m.total_records)*100).toFixed(1)}%</div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Rejection Rate</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Error Breakdown Bar */}
        <div className="card">
          <div className="card-header"><h3>Quality Issue Breakdown</h3><span style={{ fontSize: 12, color: 'var(--text-muted)' }}>580 total violations</span></div>
          <div className="card-body">
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
          </div>
        </div>

        <div className="charts-grid">
          {/* Score Trend */}
          <div className="card">
            <div className="card-header"><h3>Quality Score Trend (Today)</h3></div>
            <div className="card-body">
              <ResponsiveContainer width="100%" height={180}>
                <AreaChart data={timelineData} margin={{ top: 0, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="var(--bmw-blue)" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="var(--bmw-blue)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
                  <XAxis dataKey="time" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
                  <YAxis domain={[85, 100]} tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
                  <Tooltip contentStyle={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', borderRadius: 8 }} />
                  <Area type="monotone" dataKey="score" stroke="var(--bmw-blue-bright)" fill="url(#scoreGrad)" strokeWidth={2} dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Penalty Breakdown */}
          <div className="card">
            <div className="card-header"><h3>Score Penalty Breakdown</h3></div>
            <div className="card-body">
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {penaltyData.map((d) => (
                  <div key={d.name} style={{ display: 'grid', gridTemplateColumns: '1fr auto auto', alignItems: 'center', gap: '0.75rem' }}>
                    <div style={{ fontSize: 12, color: 'var(--text-secondary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{d.name}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)', width: 60, textAlign: 'right' }}>w={d.weight}</div>
                    <div style={{ fontSize: 12, fontWeight: 700, color: d.penalty > 0.2 ? 'var(--color-poor)' : 'var(--color-excellent)', width: 54, textAlign: 'right' }}>
                      -{d.penalty.toFixed(3)}
                    </div>
                  </div>
                ))}
                <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '0.5rem', display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: 12, fontWeight: 600 }}>Final Score</span>
                  <span style={{ fontSize: 14, fontWeight: 800, color: 'var(--color-excellent)' }}>{m.quality_score}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Null Summary */}
        <div className="card">
          <div className="card-header"><h3>Null Value Analysis</h3></div>
          <div className="card-body">
            <div className="data-table-wrap">
              <table className="data-table">
                <thead>
                  <tr><th>Column</th><th>Null Count</th><th>Null %</th><th>Visual</th><th>Status</th></tr>
                </thead>
                <tbody>
                  {m.null_summary.map((item) => (
                    <tr key={item.column}>
                      <td className="monospace">{item.column}</td>
                      <td>{item.null_count.toLocaleString()}</td>
                      <td>{item.null_pct.toFixed(2)}%</td>
                      <td style={{ width: 120 }}>
                        <div className="progress-bar-wrap">
                          <div className="progress-bar-fill" style={{ width: `${Math.min(item.null_pct * 10, 100)}%`, background: item.null_pct > 1 ? '#FF4757' : 'var(--bmw-blue)' }} />
                        </div>
                      </td>
                      <td>
                        <span className={`badge ${item.null_pct === 0 ? 'badge-excellent' : item.null_pct < 1 ? 'badge-good' : 'badge-poor'}`}>
                          {item.null_pct === 0 ? 'CLEAN' : item.null_pct < 1 ? 'WARNING' : 'FAIL'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
