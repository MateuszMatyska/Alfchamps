import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client.js'

const CATEGORIES = [
  { key: 'web', label: 'Web Application' },
  { key: 'api', label: 'API' },
  { key: 'mobile', label: 'Mobile' },
  { key: 'genai', label: 'GenAI / LLM' },
]

export default function NewTest() {
  const [standards, setStandards] = useState([])
  const [name, setName] = useState('')
  const [selected, setSelected] = useState({})
  const [asvsLevel, setAsvsLevel] = useState(2)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    api
      .listStandards()
      .then(setStandards)
      .catch((e) => setError(e.message))
  }, [])

  const toggle = (slug) => {
    setSelected((prev) => ({ ...prev, [slug]: !prev[slug] }))
  }

  const byCategory = (cat) => standards.filter((s) => s.category === cat)

  const selectedBoth = Object.values(selected).filter(Boolean).length
  const showAsvs = (selected['owasp-asvs'] ?? false) || !standards.length

  const create = async (e) => {
    e.preventDefault()
    if (!name.trim()) {
      setError('Please give the test a name.')
      return
    }
    const slugs = Object.keys(selected).filter((s) => selected[s])
    if (slugs.length === 0) {
      setError('Please select at least one standard.')
      return
    }
    setSubmitting(true)
    setError('')
    try {
      const project = await api.createProject({
        name: name.trim(),
        standard_slugs: slugs,
        asvs_level: slugs.includes('owasp-asvs') ? asvsLevel : null,
      })
      navigate(`/project/${project.id}`)
    } catch (e) {
      setError(e.message)
      setSubmitting(false)
    }
  }

  return (
    <div>
      <h1>New Security Test</h1>
      {error && <div className="error-box">{error}</div>}

      <form onSubmit={create}>
        <div className="card">
          <label className="label">Test name</label>
          <input
            className="input"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Acme Web App Pen Test — Q3"
            maxLength={256}
          />
        </div>

        {CATEGORIES.map((cat) => (
          <div className="card" key={cat.key}>
            <h3 style={{ marginBottom: 12 }}>{cat.label}</h3>
            {byCategory(cat.key).map((s) => (
              <label key={s.slug} className={`checkbox-row ${selected[s.slug] ? 'selected' : ''}`}>
                <input type="checkbox" checked={!!selected[s.slug]} onChange={() => toggle(s.slug)} />
                <div>
                  <strong>{s.name}</strong>
                  <div className="muted" style={{ }}>
                    {s.edition} — {s.description.slice(0, 90)}
                    {s.description.length > 90 ? '…' : ''}
                  </div>
                </div>
              </label>
            ))}
            {byCategory(cat.key).length === 0 && <div className="muted">No standards available.</div>}
          </div>
        ))}

        {showAsvs && (
          <div className="card">
            <h3 style={{ marginBottom: 12 }}>ASVS Verification Level</h3>
            <p className="muted" style={{ marginTop: 0 }}>
              Choose which subset of the full ASVS checklist to include.
            </p>
            <div className="grid grid-2">
              {[
                { v: 1, t: 'Level 1', d: 'Automated / opportunistic testing' },
                { v: 2, t: 'Level 2', d: 'Most applications (recommended)' },
                { v: 3, t: 'Level 3', d: 'High-value / high-risk applications' },
              ].map((o) => (
                <label key={o.v} className={`checkbox-row ${asvsLevel === o.v ? 'selected' : ''}`}>
                  <input type="radio" checked={asvsLevel === o.v} onChange={() => setAsvsLevel(o.v)} />
                  <div>
                    <strong>{o.t}</strong>
                    <div className="muted" style={{ }}>
                      {o.d}
                    </div>
                  </div>
                </label>
              ))}
            </div>
          </div>
        )}

        <div className="action-row">
          <button type="submit" className="btn" disabled={submitting}>
            {submitting ? 'Creating…' : 'Create Test'}
          </button>
          {selectedBoth > 0 && (
            <span className="muted" style={{ alignSelf: 'center' }}>
              {selectedBoth} standard(s) selected
            </span>
          )}
        </div>
      </form>
    </div>
  )
}
