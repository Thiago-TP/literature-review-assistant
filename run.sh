#!/usr/bin/env bash
# Starts backend (FastAPI) and frontend (Vite) together for local use.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -d "$ROOT_DIR/backend/.venv" ]; then
  echo "Backend virtualenv not found. First-time setup:"
  echo "  cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/alembic upgrade head"
  exit 1
fi

if [ ! -d "$ROOT_DIR/frontend/node_modules" ]; then
  echo "Frontend dependencies not found. First-time setup:"
  echo "  cd frontend && npm install"
  exit 1
fi

cleanup() {
  echo "Stopping..."
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

(cd "$ROOT_DIR/backend" && .venv/bin/uvicorn app.main:app --port 8000) &
BACKEND_PID=$!

(cd "$ROOT_DIR/frontend" && npm run dev) &
FRONTEND_PID=$!

echo "Backend:  http://localhost:8000/docs"
echo "Frontend: http://localhost:5173"
wait
