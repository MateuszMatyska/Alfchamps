// Thin fetch wrapper around the Alfchamps backend.
// In dev, requests hit the Vite dev server and are proxied to the backend.
// In production (served by nginx), requests are proxied by nginx to the backend.

const BASE = ''

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body.detail || detail
    } catch {
      /* ignore non-json */
    }
    throw new Error(detail || `Request failed (${res.status})`)
  }
  if (res.status === 204) return null
  const ct = res.headers.get('content-type') || ''
  if (ct.includes('application/json')) return res.json()
  return res
}

export const api = {
  // Standards
  listStandards: () => request('/standards'),

  // Memorial
  getMemorial: () => request('/memorial'),

  // Projects
  listProjects: () => request('/projects'),
  getProject: (id) => request(`/projects/${id}`),
  createProject: (payload) =>
    request('/projects', { method: 'POST', body: JSON.stringify(payload) }),
  deleteProject: (id) => request(`/projects/${id}`, { method: 'DELETE' }),

  // Items
  updateItem: (projectId, itemId, payload) =>
    request(`/projects/${projectId}/items/${itemId}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),
  addCustomItem: (projectId, payload) =>
    request(`/projects/${projectId}/items`, { method: 'POST', body: JSON.stringify(payload) }),
  deleteItem: (projectId, itemId) =>
    request(`/projects/${projectId}/items/${itemId}`, { method: 'DELETE' }),

  // Screenshots
  uploadScreenshot: (projectId, itemId, file, altText) => {
    const form = new FormData()
    form.append('file', file)
    if (altText) form.append('alt_text', altText)
    return request(`/projects/${projectId}/items/${itemId}/screenshots`, {
      method: 'POST',
      body: form,
    })
  },

  // Report
  getReportConfig: (projectId) => request(`/projects/${projectId}/report/config`),
  updateReportConfig: (projectId, payload) =>
    request(`/projects/${projectId}/report/config`, { method: 'PUT', body: JSON.stringify(payload) }),
  uploadCompanyLogo: (projectId, file) => {
    const form = new FormData()
    form.append('file', file)
    return request(`/projects/${projectId}/report/config/logo`, { method: 'POST', body: form })
  },
  reportPdfUrl: (projectId) => `${BASE}/projects/${projectId}/report/pdf`,
}

export const screenshotUrl = (projectId, itemId, screenshotId) =>
  `/projects/${projectId}/items/${itemId}/screenshots/${screenshotId}/file`

export const memorialPhotoUrl = () => '/memorial/photo'

export const alfchampsLogoUrl = () => '/assets/alfchamps_logo.png'
