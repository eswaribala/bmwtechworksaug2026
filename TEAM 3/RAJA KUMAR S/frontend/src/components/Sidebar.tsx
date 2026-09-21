import { NavLink } from 'react-router-dom';
import { usePipeline } from '../context/PipelineContext';

const NAV_ITEMS = [
  { to: '/',           label: 'Dashboard' },
  { to: '/validate',   label: 'Validate' },
  { to: '/checks',     label: 'Quality Checks' },
  { to: '/quarantine', label: 'Quarantine Zone' },
  { to: '/report',     label: 'Quality Report' },
  { to: '/monitor',    label: 'Pipeline Monitor' },
  { to: '/athena',     label: 'Athena Explorer' },
  { to: '/governance', label: 'Governance' },
];

export default function Sidebar() {
  const { backendOnline, awsConnected } = usePipeline();

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-logo-mark">
          <div className="bmw-circle">BMW</div>
          <div>
            <h2>Data Quality</h2>
            <p>Governance Platform</p>
          </div>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section-label">Navigation</div>
        {NAV_ITEMS.map(({ to, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
          >
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-status">
        <div className="status-row">
          <span className={`status-dot ${backendOnline ? 'status-dot-on' : 'status-dot-off'}`} />
          <span>Backend {backendOnline ? 'Connected' : 'Offline'}</span>
        </div>
        <div className="status-row">
          <span className={`status-dot ${awsConnected ? 'status-dot-on' : 'status-dot-off'}`} />
          <span>AWS {awsConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </div>

      <div className="sidebar-footer">
        <div style={{ marginBottom: 4 }}>Participant 12 · Pod D</div>
        <div style={{ color: 'var(--text-muted)', fontSize: 10 }}>BMW Connected Mobility 2026</div>
      </div>
    </aside>
  );
}
