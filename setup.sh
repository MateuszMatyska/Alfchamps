#!/usr/bin/env bash
set -euo pipefail

# Alfchamps - local setup (run "from commands" using a Python virtualenv + npm).
# This is a LOCAL-ONLY tool. It binds to 127.0.0.1 (localhost) only.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-python3}"

echo "==> Alfchamps local setup"

# 1. Python virtual environment + backend dependencies
if [ ! -d ".venv" ]; then
  echo "==> Creating virtual environment (.venv)"
  "$PYTHON" -m venv .venv
fi
echo "==> Installing backend dependencies"
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r backend/requirements.txt

# 2. Frontend dependencies
echo "==> Installing frontend dependencies"
cd frontend
if [ -f package-lock.json ]; then
  npm ci
else
  npm install
fi
cd "$ROOT"

# 3. Environment template if missing
if [ ! -f ".env" ]; then
  echo "==> Creating .env from .env.example"
  cp .env.example .env
fi

echo ""
echo "Done. Start the backend and frontend:"
echo "  make run-backend     # uvicorn on http://127.0.0.1:8000"
echo "  make run-frontend    # Vite on http://127.0.0.1:5173"
echo "Then open http://localhost:5173"
