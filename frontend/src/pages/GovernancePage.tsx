import { GOVERNANCE_ACCESS } from '../data/mockData';
import type { DataZone } from '../types';

const ZONES: DataZone[] = ['raw', 'curated', 'quarantine', 'reports'];

const ZONE_DESCRIPTIONS: Record<DataZone, { icon: string; desc: string; path: string }> = {
  raw:        { icon: '📥', desc: 'Original unmodified BMW datasets',             path: 's3://bmw-data-quality/raw/' },
  curated:    { icon: '✅', desc: 'Validated records ready for analytics',         path: 's3://bmw-data-quality/curated/' },
  quarantine: { icon: '🚫', desc: 'Invalid records for investigation',             path: 's3://bmw-data-quality/quarantine/' },
  reports:    { icon: '📊', desc: 'Quality reports and scoring outputs',           path: 's3://bmw-data-quality/reports/' },
};

const ROLE_DESCRIPTIONS = {
  'Data Engineer':  { icon: '🔧', desc: 'Full pipeline access — can read raw data, curated data, quarantine, and quality reports.' },
  'Data Analyst':   { icon: '📈', desc: 'Analytics access — can query curated data and review quality reports via Athena.' },
  'Business User':  { icon: '💼', desc: 'Report-only access — can view approved quality reports and dashboard summaries.' },
};

const POLICIES = [
  { id: 'P01', resource: 's3://bmw-data-quality/raw/', action: 'lakeformation:DescribeResource', principal: 'data-engineers', effect: 'Allow' },
  { id: 'P02', resource: 's3://bmw-data-quality/curated/', action: 'lakeformation:DescribeResource', principal: 'data-engineers, data-analysts', effect: 'Allow' },
  { id: 'P03', resource: 's3://bmw-data-quality/quarantine/', action: 'lakeformation:DescribeResource', principal: 'data-engineers', effect: 'Allow' },
  { id: 'P04', resource: 's3://bmw-data-quality/reports/', action: 'lakeformation:DescribeResource', principal: 'all', effect: 'Allow' },
  { id: 'P05', resource: 's3://bmw-data-quality/raw/', action: 'lakeformation:DescribeResource', principal: 'business-users', effect: 'Deny' },
];

export default function GovernancePage() {
  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1>Data Governance</h1>
          <p>AWS Lake Formation access control matrix — role-based data zone permissions</p>
        </div>
        <div className="page-header-badge" style={{ background: 'rgba(0,102,204,0.12)', color: 'var(--bmw-blue-bright)', border: '1px solid rgba(0,102,204,0.3)' }}>
          🔐 Lake Formation
        </div>
      </div>

      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

        {/* Zone overview */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
          {ZONES.map(z => {
            const d = ZONE_DESCRIPTIONS[z];
            return (
              <div key={z} className="card card-body" style={{ padding: '1.25rem' }}>
                <div style={{ fontSize: 28, marginBottom: 8 }}>{d.icon}</div>
                <div style={{ fontSize: 14, fontWeight: 700, textTransform: 'capitalize', marginBottom: 4 }}>{z}</div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 8 }}>{d.desc}</div>
                <div style={{ fontSize: 10, fontFamily: 'JetBrains Mono, monospace', color: 'var(--bmw-blue-bright)', wordBreak: 'break-all' }}>{d.path}</div>
              </div>
            );
          })}
        </div>

        {/* Access matrix */}
        <div className="card">
          <div className="card-header"><h3>Access Control Matrix</h3><span style={{ fontSize: 12, color: 'var(--text-muted)' }}>AWS Lake Formation permissions</span></div>
          <div className="card-body" style={{ padding: 0 }}>
            <table className="governance-table">
              <thead>
                <tr>
                  <th style={{ textAlign: 'left', padding: '1rem 1.25rem' }}>Role</th>
                  {ZONES.map(z => (
                    <th key={z} className="zone-header">
                      <div>{ZONE_DESCRIPTIONS[z].icon}</div>
                      <div style={{ textTransform: 'capitalize' }}>{z}</div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {GOVERNANCE_ACCESS.map(({ role, zones }) => (
                  <tr key={role}>
                    <td className="role-cell" style={{ padding: '1rem 1.25rem', textAlign: 'left' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ fontSize: 18 }}>{ROLE_DESCRIPTIONS[role].icon}</span>
                        <span>{role}</span>
                      </div>
                    </td>
                    {ZONES.map(z => (
                      <td key={z}>
                        {zones[z]
                          ? <span className="access-yes" title="Access Granted">✓</span>
                          : <span className="access-no" title="Access Denied">✗</span>
                        }
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Role descriptions */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
          {GOVERNANCE_ACCESS.map(({ role }) => {
            const d = ROLE_DESCRIPTIONS[role];
            return (
              <div key={role} className="card card-body">
                <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '0.75rem' }}>
                  <span style={{ fontSize: 24 }}>{d.icon}</span>
                  <h3 style={{ fontSize: 14 }}>{role}</h3>
                </div>
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.6 }}>{d.desc}</p>
              </div>
            );
          })}
        </div>

        {/* Lake Formation policies */}
        <div className="card">
          <div className="card-header"><h3>Lake Formation Resource Policies</h3></div>
          <div className="card-body" style={{ padding: 0 }}>
            <table className="data-table">
              <thead>
                <tr><th>Policy ID</th><th>Resource</th><th>Action</th><th>Principal</th><th>Effect</th></tr>
              </thead>
              <tbody>
                {POLICIES.map(p => (
                  <tr key={p.id}>
                    <td className="monospace" style={{ color: 'var(--bmw-blue-bright)' }}>{p.id}</td>
                    <td className="monospace" style={{ fontSize: 11 }}>{p.resource}</td>
                    <td className="monospace" style={{ fontSize: 11 }}>{p.action}</td>
                    <td style={{ fontSize: 12 }}>{p.principal}</td>
                    <td>
                      <span className={`badge ${p.effect === 'Allow' ? 'badge-excellent' : 'badge-critical'}`}>{p.effect}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Glue Catalog */}
        <div className="card">
          <div className="card-header"><h3>AWS Glue Data Catalog</h3></div>
          <div className="card-body">
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '0.75rem' }}>
              {['bmw_vehicle_master', 'bmw_telemetry', 'bmw_sales', 'bmw_maintenance', 'bmw_warranty'].map(table => (
                <div key={table} style={{ padding: '0.875rem', background: 'var(--bg-glass)', borderRadius: 8, border: '1px solid var(--border-accent)' }}>
                  <div style={{ fontSize: 16, marginBottom: 6 }}>🗄️</div>
                  <div className="monospace" style={{ fontSize: 11, color: 'var(--bmw-blue-bright)' }}>{table}</div>
                  <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4 }}>Parquet · Curated</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
