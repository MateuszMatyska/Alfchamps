import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api, screenshotUrl } from '../api/client.js'

const STATUSES = ['not_tested', 'in_progress', 'passed', 'failed', 'na']

const STATUS_LABEL = {
  not_tested: 'Not tested',
  in_progress: 'In progress',
  passed: 'Passed',
  failed: 'Failed',
  na: 'N/A',
}

const EMPTY_CUSTOM = { title: '', description: '', reproduce_steps: '' }

// Only http(s) links are rendered as documentation links.
const safeUrl = (url) => (/^https?:\/\//i.test(url || '') ? url : '')

// Next auto sub-point code, mirroring the backend: A01 -> A01-01, A01-02, ...
const nextSubCode = (item) => {
  const base = item?.code || 'CUSTOM'
  const highest = (item?.children || []).reduce((max, child) => {
    const m = /-(\d+)$/.exec(child.code || '')
    return m ? Math.max(max, Number(m[1])) : max
  }, 0)
  return `${base}-${String(highest + 1).padStart(2, '0')}`
}

export default function WorkspacePage() {
  const { id } = useParams()
  const [project, setProject] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [active, setActive] = useState(null)
  const [draft, setDraft] = useState({ status: '', notes: '', reproduce_steps: '' })
  const [saving, setSaving] = useState(false)
  const [custom, setCustom] = useState(EMPTY_CUSTOM)
  const [customFiles, setCustomFiles] = useState([])

  const load = useCallback(
    (init = false) => {
      api
        .getProject(id)
        .then((p) => {
          setProject(p)
          if (init && p.items.length) {
            const first = p.items[0]
            setActive(first.id)
            setDraft({
              status: first.status,
              notes: first.notes,
              reproduce_steps: first.reproduce_steps,
            })
          }
          setLoading(false)
        })
        .catch((e) => {
          setError(e.message)
          setLoading(false)
        })
    },
    [id],
  )

  useEffect(() => load(true), [load])

  const findItem = useCallback((items, itemId) => {
    for (const it of items || []) {
      if (it.id === itemId) return it
      const found = findItem(it.children || [], itemId)
      if (found) return found
    }
    return null
  }, [])

  const activeItem = useMemo(() => findItem(project?.items || [], active), [project, active, findItem])
  const activeIsSub = activeItem?.parent_id != null

  const groupName = (code) => {
    if (code.startsWith('API')) return 'OWASP API Top 10'
    if (code.startsWith('A')) return 'OWASP Top 10 Web'
    if (code.startsWith('WSTG')) return 'WSTG'
    if (code.startsWith('MSTG')) return 'MASVS'
    if (code.startsWith('V')) return 'ASVS'
    if (code.startsWith('LLM')) return 'GenAI Top 10'
    return 'Other'
  }

  const groups = useMemo(() => {
    if (!project) return []
    const map = {}
    project.items.forEach((item) => {
      const key = groupName(item.code)
      const g = (map[key] = map[key] || { name: key, items: [] })
      g.items.push(item)
    })
    return Object.values(map)
  }, [project])

  const selectItem = (itemId) => {
    const it = findItem(project.items, itemId)
    setActive(itemId)
    setDraft({
      status: it.status,
      notes: it.notes,
      reproduce_steps: it.reproduce_steps,
    })
    setError('')
  }

  const save = async () => {
    setSaving(true)
    setError('')
    try {
      await api.updateItem(id, activeItem.id, {
        status: draft.status,
        notes: draft.notes,
        reproduce_steps: draft.reproduce_steps,
      })
      await load()
      setSaving(false)
    } catch (e) {
      setError(e.message)
      setSaving(false)
    }
  }

  const onUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    try {
      await api.uploadScreenshot(id, activeItem.id, file, '')
      load()
    } catch (err) {
      setError(err.message)
    }
    e.target.value = ''
  }

  const onAddFiles = (e) => {
    setCustomFiles(Array.from(e.target.files || []))
  }

  const addSub = async () => {
    if (!custom.title.trim()) {
      setError('Sub-check needs a title.')
      return
    }
    if (!activeItem || activeIsSub) {
      setError('Select a main point to add the sub-check under.')
      return
    }
    setSaving(true)
    setError('')
    try {
      const created = await api.addCustomItem(id, {
        title: custom.title.trim(),
        description: custom.description,
        reproduce_steps: custom.reproduce_steps,
        parent_id: activeItem.id,
      })
      for (const file of customFiles) {
        await api.uploadScreenshot(id, created.id, file, '')
      }
      setCustom(EMPTY_CUSTOM)
      setCustomFiles([])
      await load()
      setActive(created.id)
      setDraft({
        status: 'not_tested',
        notes: '',
        reproduce_steps: created.reproduce_steps || custom.reproduce_steps,
      })
      setSaving(false)
    } catch (e) {
      setError(e.message)
      setSaving(false)
    }
  }

  const removeSub = async () => {
    if (!activeItem || !activeIsSub) return
    if (!window.confirm(`Remove sub-check ${activeItem.code}? This cannot be undone.`)) return
    setSaving(true)
    setError('')
    try {
      await api.deleteItem(id, activeItem.id)
      const parentId = project.items.find((it) => (it.children || []).some((c) => c.id === activeItem.id))?.id
      await load()
      setActive(parentId || null)
      setSaving(false)
    } catch (e) {
      setError(e.message)
      setSaving(false)
    }
  }

  if (loading) return <div className="spinner">Loading workspace…</div>
  if (!project) return <div className="error-box">{error || 'Project not found'}</div>

  const docUrl = safeUrl(activeItem?.reference_url)

  return (
    <div>
      <div className="action-row page-head">
        <h1 style={{ margin: 0 }}>{project.name}</h1>
        <Link to={`/project/${id}/report`} className="btn">
          Report Settings
        </Link>
      </div>
      {error && <div className="error-box">{error}</div>}

      <p className="muted">{project.items.length} checklist items</p>

      <div className="items-layout">
        <div className="group-list">
          {groups.map((g) => (
            <div key={g.name}>
              <div className="group-header">
                {g.name} ({g.items.length})
              </div>
              {g.items.map((item) => (
                <div key={item.id}>
                  <div
                    className={`group-item ${item.id === active ? 'active' : ''}`}
                    onClick={() => selectItem(item.id)}
                  >
                    <div>
                      <div className="group-item-code">{item.code}</div>
                      <div className="group-item-title">{item.title}</div>
                    </div>
                    <span className={`tag`} style={{ background: statusColor(item.status) }}>
                      {STATUS_LABEL[item.status]}
                    </span>
                  </div>
                  {(item.children || []).map((child) => (
                    <div
                      key={child.id}
                      className={`group-item sub-item ${child.id === active ? 'active' : ''}`}
                      onClick={() => selectItem(child.id)}
                    >
                      <div>
                        <div className="group-item-code">{child.code}</div>
                        <div className="group-item-title">{child.title}</div>
                      </div>
                      <span className={`tag`} style={{ background: statusColor(child.status) }}>
                        {STATUS_LABEL[child.status]}
                      </span>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          ))}
        </div>

        <div className="detail-pane">
          {activeItem ? (
            <>
              <h2>
                {activeItem.code} — {activeItem.title}
              </h2>
              {activeItem.description && (
                <p>
                  <strong>What / Why:</strong> {activeItem.description}
                </p>
              )}
              {activeItem.how_to_test && (
                <p>
                  <strong>How to test:</strong> {activeItem.how_to_test}
                </p>
              )}
              {activeItem.test_examples && (
                <p>
                  <strong>Test examples:</strong> {activeItem.test_examples}
                </p>
              )}
              {docUrl && (
                <p>
                  <strong>Documentation:</strong>{' '}
                  <a href={docUrl} target="_blank" rel="noopener noreferrer">
                    {docUrl}
                  </a>
                </p>
              )}

              <div className="grid grid-2" style={{ marginTop: 16 }}>
                <div>
                  <label className="label">Status</label>
                  <select
                    className="select"
                    value={draft.status}
                    onChange={(e) => setDraft({ ...draft, status: e.target.value })}
                  >
                    {STATUSES.map((s) => (
                      <option key={s} value={s}>
                        {STATUS_LABEL[s]}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div style={{ marginTop: 16 }}>
                <label className="label">Notes</label>
                <textarea
                  className="textarea"
                  value={draft.notes}
                  onChange={(e) => setDraft({ ...draft, notes: e.target.value })}
                  placeholder="Evidence, observations, impact…"
                />
              </div>

              {activeIsSub && (
                <>
                  <div style={{ marginTop: 16 }}>
                    <label className="label">Reproduction steps</label>
                    <textarea
                      className="textarea"
                      value={draft.reproduce_steps}
                      onChange={(e) => setDraft({ ...draft, reproduce_steps: e.target.value })}
                      placeholder={'1. Navigate to…\n2. Send request…'}
                    />
                  </div>

                  <div className="action-row">
                    <button className="btn" onClick={save} disabled={saving}>
                      {saving ? 'Saving…' : 'Save'}
                    </button>
                    <label className="btn btn-secondary" style={{ cursor: 'pointer' }}>
                      Upload screenshot
                      <input type="file" accept="image/*" style={{ display: 'none' }} onChange={onUpload} />
                    </label>
                    <button className="btn btn-danger" onClick={removeSub} disabled={saving}>
                      Remove sub-check
                    </button>
                  </div>

                  {(activeItem.screenshots || []).length > 0 && (
                    <div className="grid" style={{ marginTop: 16 }}>
                      {activeItem.screenshots.map((shot) => (
                        <img
                          key={shot.id}
                          className="screenshot"
                          src={screenshotUrl(id, activeItem.id, shot.id)}
                          alt={shot.alt_text || 'screenshot'}
                        />
                      ))}
                    </div>
                  )}
                </>
              )}
              {!activeIsSub && (
                <div className="action-row">
                  <button className="btn" onClick={save} disabled={saving}>
                    {saving ? 'Saving…' : 'Save'}
                  </button>
                </div>
              )}

              {!activeIsSub && (
                <div style={{ marginTop: 24, borderTop: '1px solid var(--border)', paddingTop: 16 }}>
                  <h3>Add sub-check to this item</h3>
                  <p className="muted" style={{ marginTop: 0 }}>
                    Sub-check code is generated automatically as{' '}
                    <strong>{nextSubCode(activeItem)}</strong>.
                  </p>
                  <div style={{ marginTop: 12 }}>
                    <label className="label">Title</label>
                    <input
                      className="input"
                      value={custom.title}
                      onChange={(e) => setCustom({ ...custom, title: e.target.value })}
                      placeholder="Custom security check"
                    />
                  </div>
                  <div style={{ marginTop: 12 }}>
                    <label className="label">Description</label>
                    <textarea
                      className="textarea"
                      value={custom.description}
                      onChange={(e) => setCustom({ ...custom, description: e.target.value })}
                      placeholder="What to test and how…"
                    />
                  </div>
                  <div style={{ marginTop: 12 }}>
                    <label className="label">Reproduction steps</label>
                    <textarea
                      className="textarea"
                      value={custom.reproduce_steps}
                      onChange={(e) => setCustom({ ...custom, reproduce_steps: e.target.value })}
                      placeholder={'1. Navigate to…\n2. Send request…'}
                    />
                  </div>
                  <div style={{ marginTop: 12 }}>
                    <label className="label">Screenshots (optional)</label>
                    <label className="btn btn-secondary" style={{ cursor: 'pointer' }}>
                      {customFiles.length ? `Choose screenshots (${customFiles.length} selected)` : 'Choose screenshots'}
                      <input type="file" accept="image/*" multiple style={{ display: 'none' }} onChange={onAddFiles} />
                    </label>
                  </div>
                  <div className="action-row" style={{ marginTop: 12 }}>
                    <button className="btn btn-secondary" onClick={addSub} disabled={saving}>
                      {saving ? 'Adding…' : 'Add sub-check'}
                    </button>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="empty-state">
              <p>Select a checklist item to begin.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

const statusColor = (s) => {
  switch (s) {
    case 'passed':
      return '#27ae60'
    case 'failed':
      return '#e74c3c'
    case 'in_progress':
      return '#f39c12'
    case 'na':
      return '#3498db'
    default:
      return '#9e9e9e'
  }
}
