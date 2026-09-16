import { useState } from 'react';
import { DEMO_QUARANTINE, ERROR_TYPE_COLORS } from '../data/mockData';
import type { QuarantineRecord } from '../types';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const ALL_ERROR_TYPES = ['ALL', 'NULL_VALUE', 'DUPLICATE_RECORD', 'INVALID_VIN', 'INVALID_DATE', 'OUT_OF_RANGE', 'REFERENTIAL_INTEGRITY'];

const ERROR_COUNTS = {
  NULL_VALUE: 210,
  DUPLICATE_RECORD: 150,
  INVALID_VIN: 80,
  INVALID_DATE: 60,
  OUT_OF_RANGE: 50,
  REFERENTIAL_INTEGRITY: 30,
};

const pieData = Object.entries(ERROR_COUNTS).map(([k, v]) => ({
  name: k.replace(/_/g, ' '),
  value: v,
  color: ERROR_TYPE_COLORS[k],
}));

function ErrorTypeBadge({ types }: { types: string }) {
  return (
    <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
      {types.split('|').map(t => {
        const color = ERROR_TYPE_COLORS[t] ?? '#888';
        return (
          <span key={t} style={{ fontSize: 10, padding: '2px 8px', background: `${color}15`, color, borderRadius: 99, border: `1px solid ${color}40`, whiteSpace: 'nowrap', fontWeight: 600 }}>
            {t}
          </span>
        );
      })}
    </div>
  );
}

interface DrawerProps {
  record: QuarantineRecord;
  onClose: () => void;
}

function RecordDrawer({ record, onClose }: DrawerProps) {
  const cleanRecord = Object.fromEntries(Object.entries(record).filter(([k]) => !k.startsWith('quarantine_')));
  const meta = Object.fromEntries(Object.entries(record).filter(([k]) => k.startsWith('quarantine_')));

  return (
    <>
      <div className="drawer-overlay" onClick={onClose} />
      <div className="drawer">
        <div className="drawer-header">
          <div>
            <h3 style={{ fontSize: 15 }}>Quarantine Record Detail</h3>
            <ErrorTypeBadge types={String(record.quarantine_error_type)} />
          </div>
          <button className="btn btn-ghost" onClick={onClose} style={{ padding: '0.375rem 0.75rem' }}>✕</button>
        </div>
        <div className="drawer-body">
          <div style={{ marginBottom: '1.5rem' }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8 }}>Error Information</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {Object.entries(meta).map(([k, v]) => (
                <div key={k} style={{ display: 'flex', gap: 12, fontSize: 13 }}>
                  <span style={{ color: 'var(--text-muted)', width: 200, flexShrink: 0 }}>{k.replace('quarantine_', '')}</span>
                  <span style={{ color: 'var(--text-primary)', wordBreak: 'break-all' }}>{String(v ?? 'NULL')}</span>
                </div>
              ))}
            </div>
          </div>
          <div>
            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8 }}>Original Record (JSON)</div>
            <div className="json-viewer">{JSON.stringify(cleanRecord, null, 2)}</div>
          </div>
        </div>
      </div>
    </>
  );
}

export default function QuarantinePage() {
  const [filter, setFilter] = useState('ALL');
  const [selected, setSelected] = useState<QuarantineRecord | null>(null);
  const [search, setSearch] = useState('');

  const filtered = DEMO_QUARANTINE.filter(r => {
    const matchType = filter === 'ALL' || String(r.quarantine_error_type).includes(filter);
    const matchSearch = !search || Object.values(r).some(v => String(v ?? '').toLowerCase().includes(search.toLowerCase()));
    return matchType && matchSearch;
  });

  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1>Quarantine Zone</h1>
          <p>Invalid records separated from the curated dataset · s3://bmw-data-quality/quarantine/</p>
        </div>
        <span className="page-header-badge" style={{ background: 'rgba(255,71,87,0.12)', color: 'var(--color-critical)', border: '1px solid rgba(255,71,87,0.3)' }}>
          580 Quarantined Records
        </span>
      </div>

      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

        {/* Stats + Pie */}
        <div className="charts-grid">
          <div className="card">
            <div className="card-header"><h3>Error Type Distribution</h3></div>
            <div className="card-body">
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie dataKey="value" data={pieData} cx="50%" cy="50%" outerRadius={80} stroke="none">
                    {pieData.map((d, i) => <Cell key={i} fill={d.color} />)}
                  </Pie>
                  <Tooltip contentStyle={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', borderRadius: 8 }} />
                  <Legend formatter={(v) => <span style={{ color: 'var(--text-secondary)', fontSize: 11 }}>{v}</span>} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="card">
            <div className="card-header"><h3>Quarantine Summary</h3></div>
            <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {Object.entries(ERROR_COUNTS).map(([k, v]) => {
                const color = ERROR_TYPE_COLORS[k];
                const pct = ((v / 580) * 100).toFixed(1);
                return (
                  <div key={k}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                      <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{k.replace(/_/g, ' ')}</span>
                      <span style={{ fontSize: 12, fontWeight: 700, color }}>{v} ({pct}%)</span>
                    </div>
                    <div className="progress-bar-wrap">
                      <div className="progress-bar-fill" style={{ width: `${pct}%`, background: color }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Filter + Table */}
        <div className="card">
          <div className="card-header">
            <h3>Quarantine Records</h3>
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
              <input
                className="input"
                placeholder="Search records…"
                value={search}
                onChange={e => setSearch(e.target.value)}
                style={{ width: 200 }}
                id="quarantine-search"
              />
              <select
                className="select"
                value={filter}
                onChange={e => setFilter(e.target.value)}
                id="error-type-filter"
              >
                {ALL_ERROR_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
          </div>
          <div className="card-body" style={{ padding: 0 }}>
            <div className="data-table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>event_id</th>
                    <th>vehicle_id</th>
                    <th>vin</th>
                    <th>battery_level</th>
                    <th>Error Type</th>
                    <th>Error Message</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((r, i) => (
                    <tr key={i} style={{ cursor: 'pointer' }} onClick={() => setSelected(r)}>
                      <td className="monospace">{String(r.event_id ?? 'NULL')}</td>
                      <td className="monospace" style={{ color: !r.vehicle_id || String(r.vehicle_id).startsWith('FAKE') ? 'var(--color-critical)' : 'inherit' }}>
                        {String(r.vehicle_id ?? 'NULL')}
                      </td>
                      <td className="monospace truncate" style={{ maxWidth: 160 }}>{String(r.vin ?? 'NULL')}</td>
                      <td style={{ color: Number(r.battery_level) > 100 || Number(r.battery_level) < 0 ? 'var(--color-critical)' : 'inherit' }}>
                        {r.battery_level ?? 'N/A'}
                      </td>
                      <td><ErrorTypeBadge types={String(r.quarantine_error_type)} /></td>
                      <td style={{ fontSize: 12, color: 'var(--text-secondary)', maxWidth: 200 }} className="truncate">
                        {String(r.quarantine_error_message)}
                      </td>
                      <td>
                        <button className="btn btn-ghost" style={{ padding: '0.25rem 0.625rem', fontSize: 11 }}>View</button>
                      </td>
                    </tr>
                  ))}
                  {filtered.length === 0 && (
                    <tr><td colSpan={7} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '2rem' }}>No records match the filter</td></tr>
                  )}
                </tbody>
              </table>
            </div>
            <div style={{ padding: '0.75rem 1.5rem', fontSize: 12, color: 'var(--text-muted)', borderTop: '1px solid var(--border-subtle)' }}>
              Showing {filtered.length} records · Click a row to inspect
            </div>
          </div>
        </div>
      </div>

      {selected && <RecordDrawer record={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}
