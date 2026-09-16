import { useState, useEffect, useRef } from 'react';
import { DEMO_LOGS } from '../data/mockData';
import type { LogEntry } from '../types';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

type LogLevel = 'ALL' | 'INFO' | 'WARN' | 'ERROR';

const METRICS_DATA = [
  { t: '10:29:57', records: 0,    duration: 0 },
  { t: '10:29:58', records: 2500, duration: 0.8 },
  { t: '10:29:59', records: 6000, duration: 1.8 },
  { t: '10:30:00', records: 9000, duration: 2.7 },
  { t: '10:30:01', records: 10000, duration: 3.4 },
];

export default function MonitorPage() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [levelFilter, setLevelFilter] = useState<LogLevel>('ALL');
  const [running, setRunning] = useState(false);
  const termRef = useRef<HTMLDivElement>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const indexRef = useRef(0);

  function startStream() {
    setLogs([]);
    indexRef.current = 0;
    setRunning(true);

    timerRef.current = setInterval(() => {
      if (indexRef.current < DEMO_LOGS.length) {
        const entry = DEMO_LOGS[indexRef.current];
        setLogs(prev => [...prev, entry]);
        indexRef.current++;
        // Auto-scroll
        setTimeout(() => {
          if (termRef.current) termRef.current.scrollTop = termRef.current.scrollHeight;
        }, 0);
      } else {
        clearInterval(timerRef.current!);
        setRunning(false);
      }
    }, 280);
  }

  function clearLogs() {
    if (timerRef.current) clearInterval(timerRef.current);
    setLogs([]);
    setRunning(false);
    indexRef.current = 0;
  }

  useEffect(() => () => { if (timerRef.current) clearInterval(timerRef.current); }, []);

  const filtered = logs.filter(l => levelFilter === 'ALL' || l.level === levelFilter);

  const levelClass = (level: string) => {
    if (level === 'INFO') return 'log-lvl-INFO';
    if (level === 'WARN') return 'log-lvl-WARN';
    return 'log-lvl-ERROR';
  };

  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1>Pipeline Monitor</h1>
          <p>Simulated CloudWatch log stream — /bmw/data-quality/pipeline-telemetry</p>
        </div>
        <div className="flex gap-2 items-center">
          {running && (
            <div className="page-header-badge" style={{ background: 'rgba(0,196,140,0.12)', color: '#00C48C', border: '1px solid rgba(0,196,140,0.3)', animation: 'pulse 1.5s infinite' }}>
              ● STREAMING
            </div>
          )}
          <button className="btn btn-ghost" onClick={clearLogs} id="clear-logs-btn">✕ Clear</button>
          <button className="btn btn-primary" onClick={startStream} disabled={running} id="start-pipeline-btn">
            {running ? '⏳ Running…' : '▶ Start Pipeline'}
          </button>
        </div>
      </div>

      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

        {/* Metrics row */}
        <div className="kpi-grid">
          {[
            { label: 'Records Processed', value: '10,000',    color: 'var(--bmw-blue-bright)' },
            { label: 'Processing Time',   value: '3.421s',    color: 'var(--color-excellent)' },
            { label: 'Throughput',        value: '~2,924/s',  color: '#C77DFF' },
            { label: 'Error Rate',        value: '5.8%',      color: 'var(--color-poor)' },
          ].map(m => (
            <div key={m.label} className="kpi-card" style={{ '--accent-color': m.color } as React.CSSProperties}>
              <div className="kpi-label">{m.label}</div>
              <div className="kpi-value" style={{ color: m.color, fontSize: 28 }}>{m.value}</div>
            </div>
          ))}
        </div>

        {/* Processing chart */}
        <div className="card">
          <div className="card-header"><h3>Processing Timeline</h3></div>
          <div className="card-body">
            <ResponsiveContainer width="100%" height={180}>
              <AreaChart data={METRICS_DATA} margin={{ top: 0, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="procGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="var(--bmw-blue)" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="var(--bmw-blue)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" />
                <XAxis dataKey="t" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} />
                <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 10 }} />
                <Tooltip contentStyle={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', borderRadius: 8 }} />
                <Area type="monotone" dataKey="records" stroke="var(--bmw-blue-bright)" fill="url(#procGrad)" strokeWidth={2} dot={false} name="Records" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Log terminal */}
        <div className="card">
          <div className="card-header">
            <h3>CloudWatch Log Stream</h3>
            <div className="flex gap-2 items-center">
              <div className="tab-bar">
                {(['ALL', 'INFO', 'WARN', 'ERROR'] as LogLevel[]).map(l => (
                  <button key={l} className={`tab-btn ${levelFilter === l ? 'active' : ''}`} onClick={() => setLevelFilter(l)} id={`log-filter-${l.toLowerCase()}`}>{l}</button>
                ))}
              </div>
              <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{filtered.length} entries</span>
            </div>
          </div>
          <div className="card-body" style={{ padding: '0.75rem' }}>
            <div className="log-terminal" ref={termRef}>
              {filtered.length === 0 ? (
                <div style={{ color: 'var(--text-muted)', padding: '1rem' }}>
                  {running ? 'Streaming…' : 'Click "▶ Start Pipeline" to replay the log stream'}
                </div>
              ) : (
                filtered.map((log, i) => (
                  <div key={i} className="log-line">
                    <span className="log-ts">{log.timestamp.slice(11, 19)}</span>
                    <span className={`log-lvl ${levelClass(log.level)}`}>{log.level}</span>
                    <span className="log-ds">{log.dataset}</span>
                    <span className="log-msg">{log.message}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Pipeline stages */}
        <div className="card">
          <div className="card-header"><h3>Pipeline Stage Timeline</h3></div>
          <div className="card-body">
            <div className="pipeline-timeline">
              {[
                { step: 'Upload',               desc: 'Dataset received and stored in S3 raw zone',       done: true },
                { step: 'Schema Validation',    desc: 'All required columns present in telemetry.csv',    done: true },
                { step: 'Null Check',           desc: '210 null values detected in vehicle_id and vin',   done: true },
                { step: 'Duplicate Detection',  desc: '150 duplicate event_id records identified',         done: true },
                { step: 'VIN Validation',       desc: '80 invalid VIN formats detected',                  done: true },
                { step: 'Date Validation',      desc: '60 invalid timestamp values detected',             done: true },
                { step: 'Range Validation',     desc: '50 out-of-range battery_level values detected',    done: true },
                { step: 'Referential Integrity',desc: '30 unknown vehicle_id references detected',        done: true },
                { step: 'Quality Score',        desc: 'Score calculated: 94.2 / 100 (EXCELLENT)',         done: true },
                { step: 'Curated Output',       desc: '9,420 valid records → s3://bmw-data-quality/curated/', done: true },
                { step: 'Quarantine Output',    desc: '580 invalid records → s3://bmw-data-quality/quarantine/', done: true },
                { step: 'Glue Catalog',         desc: 'bmw_telemetry table registered/updated',           done: true },
                { step: 'CloudWatch',           desc: 'All logs and metrics published',                   done: true },
              ].map((s, i) => (
                <div key={i} className="timeline-step">
                  <div className="timeline-dot" style={{ background: s.done ? 'var(--color-excellent)' : 'var(--text-muted)' }} />
                  <div className="timeline-content">
                    <h4>{s.step}</h4>
                    <p>{s.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
