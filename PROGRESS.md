# Alfchamps — Build Progress Log

Project: Security reporting tool for pen testers / security engineers (tribute to Alfred, our champion).
Stack: FastAPI + SQLite/SQLAlchemy + ReportLab (PDF) / React + Vite. Dual deployment (local venv + podman/docker).

Last updated: 2026-09-17

## Status Legend
- [x] Done and verified
- [~] Done but verification aborted / needs re-run
- [ ] Not started

---

## 1. Done — Project structure
- Created dirs: `backend/app/{routers,seed,data}`, `backend/tests`, `frontend/src/{components/{Wizard,Workspace,ReportSettings},api,pages,styles}`, `assets/`, `docs/`, `data/uploads`, `data/reports`

## 2. Done — Backend core
- `backend/app/config.py` — pydantic-settings, env vars, CORS list, upload limits, dir properties
- `backend/app/database.py` — SQLAlchemy engine/session (SQLite)
- `backend/app/models.py` — Standard, ChecklistItem, Project, ProjectItem, Screenshot, ReportConfig
- `backend/app/schemas.py` — Pydantic request/response models
- `backend/app/memorial.py` — **hardcoded Alfred tribute** (change only via PR)

## 3. Done — Seed data (verified)
Seeders in `backend/app/seed/` (idempotent, helpers in `helpers.py`):
- `top10_web.py` — OWASP Top 10 Web 2021 (10 items)
- `api_top10.py` — OWASP API Security Top 10 2023 (10 items)
- `asvs.py` — **ASVS 4.0.3, parsed from bundled official CSV** in `seed/data/asvs-4.0.3.csv` (278 items, level-tagged L1/L2/L3)
- `wstg.py` — **WSTG, parsed from bundled official checklist** in `seed/data/wstg-checklist.md` (109 items, all 12 categories)
- `masvs.py` — mobile MASVS (11 items)
- `genai.py` — GenAI LLM Top 10 2026 (10 items)
- Verified counts: ASVS=278, WSTG=109, others 10/10/11/10
- Verified ASVS level filter: L1=128, L2=259, L3=278

## 4. Done — Backend routers & PDF
- `routers/standards.py` — list standards
- `routers/projects.py` — create (wizard, level filtering), get, list, delete
- `routers/checklists.py` — update item (status/notes/repro steps), add custom item, delete
- `routers/assets.py` — screenshot upload/serve, shared `_save_image`
- `routers/reports.py` — report config get/put, company logo upload, **PDF generation** (verified OK, ~117KB, valid %PDF/%%EOF)
- `backend/app/main.py` — FastAPI app, CORS, security headers middleware, lifespan seeding, /health
- `.env.example`, `backend/requirements.txt` (includes pytest/httpx/ruff for dev)

## 5. Done — Verification (backend)
- Venv `.venv` created; backend deps installed
- `pytest backend/tests -q` → **11 passed** (health, seeded standards, ASVS level filtering, ASVS-doesn't-exclude-other-standards, CRUD, custom item, screenshot upload/serve, non-image rejected, logo upload, report config, PDF generation)
- `ruff check backend/app backend/tests` → **clean**
- Full end-to-end via real HTTP server: create project with all 6 standards (ASVS L3 = 428 items), patch item, upload screenshot (PNG), set config, **generate valid PDF (~163KB, %PDF/%%EOF)** — all 200 OK
- `backend/tests/conftest.py` isolates the test DB via `DATABASE_URL` env; `test_api.py` uses a zlib-built valid 1x1 PNG

## 6. Done — Frontend (React + Vite)
- `frontend/package.json`, `vite.config.js` (SPA build; dev proxy `/standards`, `/projects`, `/health` → `127.0.0.1:8000`; `reportPdfUrl`/`screenshotUrl` helpers)
- `index.html`, `src/main.jsx`, `src/App.jsx` (routes: Dashboard, NewTest, Workspace, ReportSettings)
- `src/api/client.js` — fetch wrapper (relative base)
- `src/pages/Dashboard.jsx` (project list), `src/pages/NewTest.jsx` (wizard: name, standards, ASVS level), `src/pages/Workspace.jsx` (grouped checklist, notes, repro steps, status, screenshot upload), `src/pages/ReportSettings.jsx` (accent color, company, logo, PDF download, memorial)
- `styles/index.css`, `eslint.config.js` (incl. `eslint-plugin-react`)
- Verified: ESLint clean, `npm run build` succeeds (36 modules)

## 7. Done — Deployment
- `Containerfile.backend` (multi-stage, non-root, `DATABASE_URL=sqlite:////data/alfchamps.db`, `ALFCHAMPS_DATA_DIR=/data`, healthcheck)
- `Containerfile.frontend` (Vite build + `nginx-unprivileged:1.27-alpine`, non-root)
- `container/nginx.conf` (proxies `/standards`, `/projects`, `/health` → `backend:8000`)
- `container-compose.yaml` (backend + frontend, volume, healthchecks, resource limits; backend not published to host)
- `setup.sh` (executable), `Makefile` (setup, run-backend, run-frontend, build, test, lint, container up/down for podman & docker)
- Podman/docker **not installed locally** → container paths authored but not built/verified

## 8. Done — Docs & Assets
- `README.md` (overview, quickstart, container usage, config table, security/local-only note, memorial)
- `docs/MEMORIAL.md` (hardcoded tribute, PR-only)
- `assets/alfred_logo.png` + `assets/README.md` (where to drop Alfred's photo)
- `AGENTS.md` updated with **LOCAL-ONLY (no auth)** deployment note
- `.gitignore` created (`.venv`, `node_modules`, `dist`, `.env`, `data/`, `*.db`, caches)

## 9. Done — Custom sub-checks, cover redesign, exec summary (2026-09-17)
- **Custom checks are now sub-points** nested under the checklist item they were created on:
  - `ProjectItem.parent_id` self-FK + `children` relationship (cascade delete-orphan)
  - Startup migration in `database.py` adds `parent_id` + `exec_summary` columns to existing SQLite DBs (verified against dev DB)
  - `get_project` returns nested `children`; sub-points can't be nested further and must belong to the project (400/404 enforced)
  - Add form in Workspace now: code/title/description/**reproduction steps**/**multi-screenshot upload**, creates item under the active item
  - Left list renders sub-points as indented child rows; clicking opens their editable detail pane
  - PDF renders sub-points indented under the parent with notes/repro/screenshots
- **Cover redesign** (per user decisions):
  - Top is **ALFCHAMPS logo** from `assets/alfchamps_logo.png` (user-provided; drawn only if file exists — no placeholder square)
  - Company logo moved **below the company name**; deleted the old solid-blue `assets/alfred_logo.png`
  - Alfred's photo moves to the **Memorial page only** (`assets/alfred_photo.png`) via new `GET /memorial/photo` + `has_photo` flag
- **Executive summary custom text**:
  - `ReportConfig.exec_summary` + config GET/PUT + schema
  - Textarea in Report Settings; rendered **above** the status-count table (table unchanged)
- **Verified:** 16 pytest tests pass, ruff clean, ESLint clean, Vite build OK, full E2E via TestClient AND through the running Podman stack (migration on the persisted volume DB, sub-point + screenshots + exec summary + PDF, logo on cover, memorial photo served)

---

## Remaining / follow-ups
- [x] Podman container deployment verified end-to-end (`make podman-up` / `podman-compose up -d --build`)
- [ ] Optional: end-to-end browser check of the new sub-check flow + cover + exec summary in the UI
- [x] Real Alfchamps logo at `assets/alfchamps_logo.png` and Alfred's photo at `assets/alfred_photo.png` provided
- [ ] Optional: switch backend build image format to `docker` so `HEALTHCHECK` shows in `podman ps` (cosmetic)

---

## Commands for picking up
```bash
# Backend tests
cd /home/mateuszm/Projects/Alfchamps && .venv/bin/pip install -q pytest httpx ruff
.venv/bin/python -m pytest backend/tests -q

# Run backend (local)
.venv/bin/uvicorn backend.app.main:app --host 127.0.0.1 --port 8000

# Frontend
cd frontend && npm install && npm run dev    # Vite on :5173, proxied or CORS to :8000
```

## Notes / gotchas
- Config uses `settings.upload_dir` / `settings.reports_dir` properties (NOT `UPLOAD_DIR` attr) — already fixed.
- Seed submodules import helpers from `.helpers` (avoids circular import).
- App is LOCAL-ONLY (no auth) — document this clearly.
- Memorial lines are hardcoded in `backend/app/memorial.py`; report uses `config.memorial_text or ALFRED_TRIBUTE`.
- Data dirs: `data/uploads` (screenshots/logos), `data/reports` (PDFs), `data/alfchamps.db`.
