import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client.js'

const PRESETS = ['#1a56db', '#7c3aed', '#0f766e', '#b91c1c', '#ea580c', '#15803d', '#111827', '#be185d']

export default function ReportSettings() {
  const { id } = useParams()
  const [color, setColor] = useState('#1a56db')
  const [companyName, setCompanyName] = useState('')
  const [reportTitle, setReportTitle] = useState('')
  const [error, setError] = useState('')
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    api
      .getReportConfig(id)
      .then((c) => {
        setColor(c.accent_color)
        setCompanyName(c.company_name || '')
        setReportTitle(c.report_title || '')
      })
      .catch((e) => setError(e.message))
  }, [id])

  const saveConfig = async () => {
    setError('')
    setSaved(false)
    try {
      await api.updateReportConfig(id, {
        accent_color: color,
        company_name: companyName,
        report_title: reportTitle,
      })
      setSaved(true)
    } catch (e) {
      setError(e.message)
    }
  }

  const onLogo = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    try {
      await api.uploadCompanyLogo(id, file)
      setSaved(true)
    } catch (err) {
      setError(err.message)
    }
    e.target.value = ''
  }

  const downloadPdf = () => {
    window.open(api.reportPdfUrl(id), '_blank')
  }

  return (
    <div>
      <div className="action-row" style={{ justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ margin: 0 }}>Report Settings</h1>
        <Link to={`/project/${id}`} className="btn btn-secondary">
          ← Back to workspace
        </Link>
      </div>
      {error && <div className="error-box">{error}</div>}
      {saved && (
        <div className="error-box" style={{ background: '#e9f9ef', borderColor: '#c3ecd2', color: '#1a7f44' }}>
          Saved.
        </div>
      )}

      <div className="card">
        <h3>Report Colors</h3>
        <div className="color-row">
          {PRESETS.map((c) => (
            <button
              key={c}
              className="color-swatch"
              style={{ background: c, borderColor: color === c ? 'var(--accent)' : 'var(--border)' }}
              onClick={() => setColor(c)}
              title={c}
            />
          ))}
          <input type="color" value={color} onChange={(e) => setColor(e.target.value)} title="Custom color" />
        </div>
      </div>

      <div className="card">
        <h3>Company & Report Details</h3>
        <div className="grid grid-2">
          <div>
            <label className="label">Company name (for report)</label>
            <input
              className="input"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              placeholder="ACME Security"
            />
          </div>
          <div>
            <label className="label">Report title</label>
            <input
              className="input"
              value={reportTitle}
              onChange={(e) => setReportTitle(e.target.value)}
              placeholder="Security Assessment Report"
            />
          </div>
        </div>
        <div style={{ marginTop: 16 }}>
          <label className="label">Company logo</label>
          <label className="btn btn-secondary" style={{ cursor: 'pointer' }}>
            Upload logo
            <input type="file" accept="image/*" style={{ display: 'none' }} onChange={onLogo} />
          </label>
        </div>
      </div>

      <div className="action-row">
        <button className="btn" onClick={saveConfig}>
          Save settings
        </button>
        <button className="btn btn-secondary" onClick={downloadPdf}>
          Download PDF report
        </button>
      </div>
    </div>
  )
}
