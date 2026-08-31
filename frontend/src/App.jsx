import { Routes, Route, NavLink } from 'react-router-dom'
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
            <span className="brand-emoji" aria-hidden="true">
              🏆
            </span>
            <span className="brand-name">Alfchamps</span>
          </NavLink>
          <nav className="nav">
            <NavLink to="/" className="nav-link" end>
              Tests
            </NavLink>
            <NavLink to="/new" className="nav-link">
              New Test
            </NavLink>
            <NavLink to="/memorial" className="nav-link">
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
