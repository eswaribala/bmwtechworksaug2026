import { useEffect, useState } from 'react';
import { API_URL } from '../context/PipelineContext';
import type { GovernanceInfo, DataZone } from '../types';

const ZONE_ORDER: DataZone[] = ['raw', 'curated', 'quarantine', 'reports'];

export default function GovernancePage() {
  const [info, setInfo] = useState<GovernanceInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetch(`${API_URL}/api/governance`)
      .then(r => (r.ok ? r.json() : null))
      .then(setInfo)
      .catch(() => setInfo(null))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="page-header">
        <div className="page-header-left">
          <h1>Governance — AWS Lake Formation</h1>
          <p>
            {info ? `s3://${info.s3_bucket} · ${info.region}` : 'Loading governance data...'}
          </p>
        </div>
        <div className="flex gap-2 items-center">
          <div className="page-header-badge">
            <span>Lake Formation</span>{' '}
            {info?.lakeformation_live ? 'Live' : 'Not Provisioned'}
          </div>
        </div>
      </div>

      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {!loading && info && !info.lakeformation_live && (
          <div className="card" style={{ borderColor: 'var(--color-acceptable)' }}>
            <div className="card-body" style={{ fontSize: 12.5, color: 'var(--text-secondary)' }}>
              Showing the designed access model. Run <code>terraform apply</code> in{' '}
              <code>terraform/modules/lakeformation</code> to register the data lake and grant real
              permissions — this page will then switch to live Lake Formation data.
            </div>
          </div>
        )}

        {/* Data Lake Admins & Registered Resources */}
        {info?.lakeformation_live && (
          <div className="kpi-grid">
            <div className="kpi-card" style={{ '--accent-color': 'var(--bmw-blue-bright)' } as React.CSSProperties}>
              <div className="kpi-label">Data Lake Admins</div>
              <div className="kpi-value" style={{ fontSize: 14, lineHeight: 1.6 }}>
                {info.data_lake_admins.length > 0 ? info.data_lake_admins.map(a => (
                  <div key={a} className="monospace" style={{ fontSize: 11, wordBreak: 'break-all' }}>{a}</div>
                )) : '-'}
              </div>
            </div>
            <div className="kpi-card" style={{ '--accent-color': 'var(--color-excellent)' } as React.CSSProperties}>
              <div className="kpi-label">Registered Resources</div>
              <div className="kpi-value" style={{ fontSize: 14, lineHeight: 1.6 }}>
                {info.registered_resources.length > 0 ? info.registered_resources.map(r => (
                  <div key={r} className="monospace" style={{ fontSize: 11, wordBreak: 'break-all' }}>{r}</div>
                )) : '-'}
              </div>
            </div>
          </div>
        )}

        {/* Zones */}
        <div className="card">
          <div className="card-header">
            <h3>Data Zones</h3>
          </div>
          <div className="card-body" style={{ padding: 0 }}>
            <div className="data-table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Zone</th>
                    <th>Description</th>
                    <th>S3 Path</th>
                  </tr>
                </thead>
                <tbody>
                  {(info?.zones ?? []).map(z => (
                    <tr key={z.id}>
                      <td style={{ fontWeight: 700 }}>{z.name}</td>
                      <td>{z.desc}</td>
                      <td className="monospace" style={{ fontSize: 11 }}>{z.path}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Role → Zone Access Matrix */}
        <div className="card">
          <div className="card-header">
            <h3>Role Access Matrix</h3>
          </div>
          <div className="card-body" style={{ padding: 0 }}>
            <div className="data-table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Role</th>
                    <th>Description</th>
                    {ZONE_ORDER.map(z => (
                      <th key={z} style={{ textTransform: 'capitalize' }}>{z}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(info?.roles ?? []).map(r => (
                    <tr key={r.role}>
                      <td style={{ fontWeight: 700 }}>{r.role}</td>
                      <td style={{ fontSize: 12 }}>{r.desc}</td>
                      {ZONE_ORDER.map(z => (
                        <td key={z} style={{ textAlign: 'center' }}>
                          <span style={{ color: r.zones[z] ? 'var(--color-excellent)' : 'var(--color-critical)' }}>
                            {r.zones[z] ? '✓' : '✕'}
                          </span>
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Permission Grants */}
        <div className="card">
          <div className="card-header">
            <h3>Lake Formation Permission Grants</h3>
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              {info?.policies.length ?? 0} grant{(info?.policies.length ?? 0) === 1 ? '' : 's'}
            </span>
          </div>
          <div className="card-body" style={{ padding: 0 }}>
            <div className="data-table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Resource</th>
                    <th>Permissions</th>
                    <th>Principal</th>
                    <th>Effect</th>
                  </tr>
                </thead>
                <tbody>
                  {(info?.policies ?? []).map(p => (
                    <tr key={p.id}>
                      <td className="monospace">{p.id}</td>
                      <td className="monospace" style={{ fontSize: 11 }}>{p.resource}</td>
                      <td style={{ fontSize: 11 }}>{p.action}</td>
                      <td className="monospace" style={{ fontSize: 11 }}>{p.principal}</td>
                      <td style={{ color: p.effect === 'Allow' ? 'var(--color-excellent)' : 'var(--color-critical)', fontWeight: 700 }}>
                        {p.effect}
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
