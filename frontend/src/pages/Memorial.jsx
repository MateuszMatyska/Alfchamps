import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, memorialPhotoUrl } from '../api/client.js'

export default function Memorial() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api
      .getMemorial()
      .then(setData)
      .catch((e) => setError(e.message))
  }, [])

  return (
    <div>
      <div className="card" style={{ textAlign: 'center', maxWidth: 640, margin: '0 auto', padding: 40 }}>
        <h1 style={{ marginBottom: 4 }}>🏆</h1>
        <h2 style={{ marginTop: 0 }}>{data ? data.tagline : 'Alfchamps'}</h2>
        {data && data.has_photo && (
          <img
            src={memorialPhotoUrl()}
            alt="Alfred"
            style={{ maxWidth: '100%', maxHeight: 420, borderRadius: 12, marginTop: 8 }}
          />
        )}
        {error ? (
          <div className="error-box">{error}</div>
        ) : data ? (
          <p
            className="muted"
            style={{ whiteSpace: 'pre-line', fontStyle: 'italic', fontSize: 18, lineHeight: 1.7 }}
          >
            {data.text}
          </p>
        ) : (
          <p className="muted">Loading…</p>
        )}
        <div className="action-row" style={{ justifyContent: 'center' }}>
          <Link to="/" className="btn">
            ← Back to tests
          </Link>
        </div>
      </div>
    </div>
  )
}
