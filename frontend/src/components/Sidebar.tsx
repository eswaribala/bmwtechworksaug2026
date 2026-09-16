import { NavLink } from 'react-router-dom';

const NAV_ITEMS = [
  { to: '/',           icon: '📊', label: 'Dashboard' },
  { to: '/validate',   icon: '🔍', label: 'Validate' },
  { to: '/checks',     icon: '✅', label: 'Quality Checks' },
  { to: '/quarantine', icon: '🚫', label: 'Quarantine Zone' },
  { to: '/report',     icon: '📋', label: 'Quality Report' },
  { to: '/monitor',    icon: '📡', label: 'Pipeline Monitor' },
  { to: '/governance', icon: '🔐', label: 'Governance' },
  { to: '/athena',     icon: '🔎', label: 'Athena Explorer' },
];

export default function Sidebar() {
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
        {NAV_ITEMS.map(({ to, icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
          >
            <span className="nav-icon">{icon}</span>
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div style={{ marginBottom: 4 }}>Participant 12 · Pod D</div>
        <div style={{ color: 'var(--text-muted)', fontSize: 10 }}>BMW Connected Mobility 2026</div>
      </div>
    </aside>
  );
}
