import { Routes, Route, NavLink } from 'react-router-dom'
import { alfchampsLogoUrl } from './api/client.js'
import Dashboard from './pages/Dashboard.jsx'
import NewTest from './pages/NewTest.jsx'
import WorkspacePage from './pages/Workspace.jsx'
import ReportSettings from './pages/ReportSettings.jsx'
import Memorial from './pages/Memorial.jsx'

export default function App() {
  return (
    <div className="app">
      <header className="app-header">
        <div className="app-header-inner">
          <NavLink to="/" className="brand">
            <img
              src={alfchampsLogoUrl()}
              alt="Alfchamps logo"
              style={{ height: 120, width: 120, objectFit: 'contain', display: 'inline-block' }}
            />
          </NavLink>
          <nav className="nav">
            <NavLink to="/" className="nav-link" end title="Back to project list">
              Tests
            </NavLink>
            <NavLink to="/new" className="nav-link" title="Create a new test">
              New Test
            </NavLink>
            <NavLink to="/memorial" className="nav-link" title="In memory of Alfred">
              Memorial
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="app-main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/new" element={<NewTest />} />
          <Route path="/project/:id" element={<WorkspacePage />} />
          <Route path="/project/:id/report" element={<ReportSettings />} />
          <Route path="/memorial" element={<Memorial />} />
        </Routes>
      </main>
      <footer className="app-footer">
        In memory of Alfred — our champion. Local-only tool.
      </footer>
    </div>
  )
}
