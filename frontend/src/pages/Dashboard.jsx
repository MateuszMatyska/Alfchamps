import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, alfchampsLogoUrl } from '../api/client.js'

export default function Dashboard() {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [pendingDelete, setPendingDelete] = useState(null)

  useEffect(() => {
    api
      .listProjects()
      .then(setProjects)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const remove = () => {
    if (!pendingDelete) return
    api
      .deleteProject(pendingDelete)
      .then(() => {
        setProjects(projects.filter((p) => p.id !== pendingDelete))
        setPendingDelete(null)
      })
      .catch((e) => {
        setError(e.message)
        setPendingDelete(null)
      })
  }

  if (loading) return <div className="spinner">Loading tests…</div>

  return (
    <div>
      <div className="action-row" style={{ justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ margin: 0 }}>Security Tests</h1>
        <Link to="/memorial" className="btn btn-secondary" style={{ fontSize: 28, padding: '11px 20px', fontWeight: 700, borderRadius: 10 }}>
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
              <span className="muted" style={{ }}>
                Created {p.created_at ? new Date(p.created_at).toLocaleDateString() : '—'}
              </span>
              <div className="action-row">
                <Link to={`/project/${p.id}`} className="btn">
                  Open
                </Link>
                <Link to={`/project/${p.id}/report`} className="btn btn-secondary">
                  Report
                </Link>
                <button className="btn btn-danger" onClick={() => setPendingDelete(p.id)}>
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {pendingDelete && (
        <div
          className="modal-overlay"
          onClick={() => setPendingDelete(null)}
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,.45)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
          }}
        >
          <div className="modal" style={{ background: '#fff', borderRadius: 8, padding: 24, maxWidth: 420, width: '100%' }}>
            <h3 style={{ marginTop: 0 }}>Delete this test?</h3>
            <p className="muted">
              This permanently deletes the test and all of its findings, screenshots, custom sub-checks, and memorial data.
            </p>
            <div className="action-row" style={{ justifyContent: 'flex-end' }}>
              <button className="btn btn-secondary" onClick={() => setPendingDelete(null)}>
                Cancel
              </button>
              <button className="btn btn-danger" onClick={remove}>
                Delete test
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
