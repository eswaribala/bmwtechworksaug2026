import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import ValidatePage from './pages/ValidatePage';
import ChecksPage from './pages/ChecksPage';
import QuarantinePage from './pages/QuarantinePage';
import ReportPage from './pages/ReportPage';
import MonitorPage from './pages/MonitorPage';
import AthenaPage from './pages/AthenaPage';
import { PipelineProvider } from './context/PipelineContext';

export default function App() {
  return (
    <PipelineProvider>
      <BrowserRouter>
        <div className="app-shell">
          <Sidebar />
          <main className="main-content">
            <Routes>
              <Route path="/"           element={<Dashboard />} />
              <Route path="/validate"   element={<ValidatePage />} />
              <Route path="/checks"     element={<ChecksPage />} />
              <Route path="/quarantine" element={<QuarantinePage />} />
              <Route path="/report"     element={<ReportPage />} />
              <Route path="/monitor"    element={<MonitorPage />} />
              <Route path="/athena"     element={<AthenaPage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </PipelineProvider>
  );
}
