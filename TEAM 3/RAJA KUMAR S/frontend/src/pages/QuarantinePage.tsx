import { useState, useEffect } from 'react';
import FileFilter from '../components/FileFilter';
import { usePipeline, API_URL } from '../context/PipelineContext';
import { ERROR_TYPE_COLORS, fmt } from '../utils/constants';
import type { QuarantineRecord } from '../types';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const ALL_ERROR_TYPES = [
  'ALL',
  'NULL_VALUE',
  'DUPLICATE_RECORD',
  'INVALID_VIN',
  'INVALID_DATE',
  'OUT_OF_RANGE',
  'REFERENTIAL_INTEGRITY',
];

function ErrorTypeBadge({ types }: { types: string }) {
  return (
    <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
      {types.split('|').map(t => {
        const color = ERROR_TYPE_COLORS[t] ?? '#888';
        return (
          <span
            key={t}
            style={{
              fontSize: 10,
              padding: '2px 8px',
              background: `${color}15`,
              color,
              borderRadius: 99,
              border: `1px solid ${color}40`,
              whiteSpace: 'nowrap',
              fontWeight: 600,
            }}
          >
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
  const cleanRecord = Object.fromEntries(
    Object.entries(record).filter(([k]) => !k.startsWith('quarantine_'))
  );
  const meta = Object.fromEntries(
    Object.entries(record).filter(([k]) => k.startsWith('quarantine_'))
  );

  return (
    <>
      <div className="drawer-overlay" onClick={onClose} />
      <div className="drawer">
        <div className="drawer-header">
          <div>
            <h3 style={{ fontSize: 15 }}>Quarantine Record Detail</h3>
            <ErrorTypeBadge types={String(record.quarantine_error_type || 'UNKNOWN')} />
          </div>
          <button className="btn btn-ghost" onClick={onClose} style={{ padding: '0.375rem 0.75rem' }}>
            Close
          </button>
        </div>
        <div className="drawer-body">
          <div style={{ marginBottom: '1.5rem' }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 }}>
              Quarantine Metadata
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {Object.entries(meta).map(([k, v]) => (
                <div key={k} style={{ display: 'flex', gap: 12, fontSize: 13 }}>
                  <span style={{ color: 'var(--text-muted)', width: 180, flexShrink: 0 }}>
                    {k.replace('quarantine_', '')}
                  </span>
                  <span style={{ color: 'var(--text-primary)', wordBreak: 'break-all' }}>
                    {String(v ?? 'NULL')}
                  </span>
                </div>
              ))}
            </div>
          </div>
          <div>
            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 }}>
              Original Ingested Record
            </div>
            <div className="json-viewer">{JSON.stringify(cleanRecord, null, 2)}</div>
          </div>
        </div>
      </div>
    </>
  );
}

export default function QuarantinePage() {
  const { selectedRun, s3Bucket, datasetFilter } = usePipeline();
  const [filter, setFilter] = useState('ALL');
  const [selected, setSelected] = useState<QuarantineRecord | null>(null);
  const [search, setSearch] = useState('');
  const [records, setRecords] = useState<QuarantineRecord[]>([]);
  const [totalCount, setTotalCount] = useState<number | null>(null);
  const [errorCounts, setErrorCounts] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!selectedRun?.run_id) {
      setRecords([]);
      setTotalCount(null);
      setErrorCounts({});
      return;
    }
    setLoading(true);
    const url = new URL(`${API_URL}/api/quarantine`);
    url.searchParams.set('run_id', selectedRun.run_id);
    url.searchParams.set('dataset', datasetFilter);
    if (filter !== 'ALL') url.searchParams.set('error_type', filter);
    if (search.trim()) url.searchParams.set('search', search.trim());
    url.searchParams.set('limit', '200');

    fetch(url.toString())
      .then(r => (r.ok ? r.json() : { records: [], total: 0, error_counts: {} }))
      .then(data => {
        setRecords(data.records ?? []);
        setTotalCount(data.total ?? 0);
        setErrorCounts(data.error_counts ?? {});
      })
      .catch(() => {
        setRecords([]);
        setTotalCount(0);
        setErrorCounts({});
      })
      .finally(() => setLoading(false));
  }, [selectedRun?.run_id, datasetFilter, filter, search]);

  const pieData = Object.entries(errorCounts).map(([k, v]) => ({
    name: k.replace(/_/g, ' '),
    value: v,
    color: ERROR_TYPE_COLORS[k] ?? '#888',
  }));

  const columns = records.length > 0
    ? Object.keys(records[0]).filter(k => !k.startsWith('quarantine_'))
    : [];

  const quarantineS3Uri = s3Bucket !== '-'
    ? `s3://${s3Bucket}/quarantine/${datasetFilter}/`
    : `output/quarantine/`;

  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1>Quarantine Zone</h1>
          <p>
            Isolated invalid records partitioned from curated datasets · Path: {quarantineS3Uri}
          </p>
        </div>
        <span
          className="page-header-badge"
          style={{
            background: 'rgba(255,71,87,0.12)',
            color: 'var(--color-critical)',
            border: '1px solid rgba(255,71,87,0.3)',
          }}
        >
          {totalCount !== null ? `${fmt(totalCount)} Quarantined Records` : '-'}
        </span>
      </div>

      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        <FileFilter />

        {/* Stats + Distribution */}
        <div className="charts-grid">
          <div className="card">
            <div className="card-header"><h3>Error Type Distribution</h3></div>
            <div className="card-body">
              {pieData.length > 0 ? (
                <ResponsiveContainer width="100%" height={220}>
                  <PieChart>
                    <Pie dataKey="value" data={pieData} cx="50%" cy="50%" outerRadius={80} stroke="none">
                      {pieData.map((d, i) => <Cell key={i} fill={d.color} />)}
                    </Pie>
                    <Tooltip contentStyle={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', borderRadius: 8 }} />
                    <Legend formatter={(v) => <span style={{ color: 'var(--text-secondary)', fontSize: 11 }}>{v}</span>} />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
                  - No quarantined records for selected file -
                </div>
              )}
            </div>
          </div>

          <div className="card">
            <div className="card-header"><h3>Error Breakdown Counts</h3></div>
            <div className="card-body">
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                {Object.entries(ERROR_TYPE_COLORS).map(([type, color]) => {
                  const cnt = errorCounts[type] ?? (totalCount === 0 ? 0 : null);
                  return (
                    <div
                      key={type}
                      style={{
                        padding: '0.75rem',
                        background: 'var(--bg-secondary)',
                        borderRadius: 8,
                        border: '1px solid var(--border-subtle)',
                      }}
                    >
                      <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{type.replace(/_/g, ' ')}</div>
                      <div style={{ fontSize: 20, fontWeight: 800, color, marginTop: 2 }}>
                        {cnt !== null ? fmt(cnt) : '-'}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        {/* Filter and Search Bar */}
        <div className="card" style={{ padding: '1rem 1.25rem' }}>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', flex: 1 }}>
              {ALL_ERROR_TYPES.map(t => (
                <button
                  key={t}
                  className={`btn ${filter === t ? 'btn-primary' : 'btn-ghost'}`}
                  style={{ fontSize: 11, padding: '0.35rem 0.75rem' }}
                  onClick={() => setFilter(t)}
                >
                  {t.replace(/_/g, ' ')}
                </button>
              ))}
            </div>
            <input
              type="text"
              className="search-input"
              placeholder="Search records by ID, VIN, reason..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              style={{ width: 280 }}
            />
          </div>
        </div>

        {/* Records Table */}
        <div className="card">
          <div className="card-header">
            <h3>Quarantine Records</h3>
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              {totalCount !== null ? `Showing ${records.length} of ${fmt(totalCount)}` : '-'}
            </span>
          </div>
          <div className="card-body" style={{ padding: 0 }}>
            {records.length > 0 ? (
              <div className="data-table-wrap">
                <table className="data-table">
                  <thead>
                    <tr>
                      {columns.map(c => (
                        <th key={c}>{c}</th>
                      ))}
                      <th>Error Type</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {records.map((r, i) => (
                      <tr key={i}>
                        {columns.map(c => {
                          const val = r[c];
                          const isNull = val === null || val === '' || val === undefined;
                          return (
                            <td key={c} className="monospace">
                              {isNull ? <span style={{ color: 'var(--color-critical)' }}>NULL</span> : String(val)}
                            </td>
                          );
                        })}
                        <td>
                          <ErrorTypeBadge types={String(r.quarantine_error_type || 'UNKNOWN')} />
                        </td>
                        <td>
                          <button
                            className="btn btn-ghost"
                            style={{ fontSize: 11, padding: '0.25rem 0.5rem' }}
                            onClick={() => setSelected(r)}
                          >
                            Inspect
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
                {loading ? 'Loading quarantine records...' : '- No quarantine records matched the criteria -'}
              </div>
            )}
          </div>
        </div>
      </div>

      {selected && <RecordDrawer record={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}
