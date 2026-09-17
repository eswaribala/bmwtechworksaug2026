import { useState, useEffect, useRef } from 'react';
import FileFilter from '../components/FileFilter';
import { usePipeline, API_URL } from '../context/PipelineContext';
import { fmt } from '../utils/constants';
import type { LogEntry } from '../types';

type LogLevel = 'ALL' | 'INFO' | 'WARN' | 'ERROR';

export default function MonitorPage() {
  const { selectedRun, datasetFilter } = usePipeline();
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [levelFilter, setLevelFilter] = useState<LogLevel>('ALL');
  const [loading, setLoading] = useState(false);
  const termRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!selectedRun?.run_id) {
      setLogs([]);
      return;
    }
    setLoading(true);
    fetch(`${API_URL}/api/logs?run_id=${selectedRun.run_id}`)
      .then(r => (r.ok ? r.json() : { logs: [] }))
      .then(d => setLogs(d.logs ?? []))
      .catch(() => setLogs([]))
      .finally(() => setLoading(false));
  }, [selectedRun?.run_id]);

  const filtered = logs.filter(l => levelFilter === 'ALL' || l.level === levelFilter);

  const levelClass = (level: string) => {
    if (level === 'INFO') return 'log-lvl-INFO';
    if (level === 'WARN') return 'log-lvl-WARN';
    return 'log-lvl-ERROR';
  };

  const totalLogs = logs.length;
  const errorLogs = logs.filter(l => l.level === 'ERROR').length;
  const warnLogs = logs.filter(l => l.level === 'WARN').length;
  const infoLogs = logs.filter(l => l.level === 'INFO').length;

  const logGroupName = '/bmw/data-quality';
  const logStreamName = selectedRun?.run_id
    ? `pipeline-${datasetFilter}-${selectedRun.run_id}`
    : `pipeline-${datasetFilter}`;

  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1>Pipeline Monitor & CloudWatch Logs</h1>
          <p>
            Log stream for {logGroupName} · Stream: {logStreamName}
          </p>
        </div>
        <div className="flex gap-2 items-center">
          <div className="page-header-badge">
            <span>Log Events</span> {totalLogs > 0 ? fmt(totalLogs) : '-'}
          </div>
        </div>
      </div>

      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        <FileFilter />

        {/* Metrics Row */}
        <div className="kpi-grid">
          {[
            { label: 'Total Events', value: totalLogs > 0 ? fmt(totalLogs) : '-', color: 'var(--bmw-blue-bright)' },
            { label: 'Info Events', value: totalLogs > 0 ? fmt(infoLogs) : '-', color: 'var(--color-excellent)' },
            { label: 'Warnings', value: totalLogs > 0 ? fmt(warnLogs) : '-', color: 'var(--color-acceptable)' },
            { label: 'Errors', value: totalLogs > 0 ? fmt(errorLogs) : '-', color: 'var(--color-critical)' },
          ].map(m => (
            <div key={m.label} className="kpi-card" style={{ '--accent-color': m.color } as React.CSSProperties}>
              <div className="kpi-label">{m.label}</div>
              <div className="kpi-value" style={{ color: m.color, fontSize: 28 }}>{m.value}</div>
            </div>
          ))}
        </div>

        {/* Log Viewer */}
        <div className="card">
          <div className="card-header">
            <h3>Pipeline Event Stream</h3>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              {(['ALL', 'INFO', 'WARN', 'ERROR'] as LogLevel[]).map(lvl => (
                <button
                  key={lvl}
                  type="button"
                  className={`btn ${levelFilter === lvl ? 'btn-primary' : 'btn-ghost'}`}
                  style={{ fontSize: 11, padding: '0.25rem 0.65rem' }}
                  onClick={() => setLevelFilter(lvl)}
                >
                  {lvl}
                </button>
              ))}
            </div>
          </div>
          <div className="card-body" style={{ padding: 0 }}>
            <div
              ref={termRef}
              className="terminal-window"
              style={{ maxHeight: 420, overflowY: 'auto', padding: '1rem' }}
            >
              {filtered.length > 0 ? (
                filtered.map((l, i) => (
                  <div key={i} className="log-line" style={{ display: 'flex', gap: '0.75rem', fontSize: 12, lineHeight: 1.6 }}>
                    <span style={{ color: 'var(--text-muted)', fontFamily: 'monospace' }}>
                      {l.timestamp ? l.timestamp.slice(0, 19).replace('T', ' ') : '-'}
                    </span>
                    <span className={levelClass(l.level)} style={{ fontWeight: 700, minWidth: 50 }}>
                      [{l.level}]
                    </span>
                    <span style={{ color: 'var(--text-secondary)', minWidth: 100 }}>
                      [{l.dataset ?? datasetFilter}]
                    </span>
                    <span style={{ color: 'var(--text-primary)', flex: 1 }}>
                      {l.message}
                    </span>
                  </div>
                ))
              ) : (
                <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
                  {loading ? 'Loading logs from server...' : '- No logs found for the selected file -'}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
