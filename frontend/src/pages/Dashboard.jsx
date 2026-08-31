import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client.js'

export default function Dashboard() {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api
      .listProjects()
      .then(setProjects)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const remove = async (id) => {
    if (!window.confirm('Delete this test and all its data?')) return
    try {
      await api.deleteProject(id)
      setProjects(projects.filter((p) => p.id !== id))
    } catch (e) {
      setError(e.message)
    }
  }

  if (loading) return <div className="spinner">Loading tests…</div>

  return (
    <div>
      <div className="action-row" style={{ justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ margin: 0 }}>Security Tests</h1>
        <Link to="/memorial" className="btn btn-secondary">
          🏆 Memorial
        </Link>
      </div>
      {error && <div className="error-box">{error}</div>}
      {projects.length === 0 ? (
        <div className="empty-state">
          <p>No tests yet.</p>
          <Link to="/new" className="btn">
            Create your first test
          </Link>
        </div>
      ) : (
        <div className="projects-grid">
          {projects.map((p) => (
            <div key={p.id} className="project-card">
              <h3 className="muted" style={{ marginBottom: 0 }}>
                {p.name}
              </h3>
              <span className="muted" style={{ fontSize: 13 }}>
                Created {p.created_at ? new Date(p.created_at).toLocaleDateString() : '—'}
              </span>
              <div className="action-row">
                <Link to={`/project/${p.id}`} className="btn">
                  Open
                </Link>
                <Link to={`/project/${p.id}/report`} className="btn btn-secondary">
                  Report
                </Link>
                <button className="btn btn-danger" onClick={() => remove(p.id)}>
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
