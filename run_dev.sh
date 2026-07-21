#!/usr/bin/env bash
# Convenience launcher for local development.
# Starts the FastAPI backend and the Vite frontend together.
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

# --- Backend ---
cd "$ROOT/backend"
if [ ! -d ".venv" ]; then
  echo "Creating backend venv..."
  python3 -m venv .venv
  ./.venv/bin/pip install -q --upgrade pip
  ./.venv/bin/pip install -q -r requirements.txt
fi
if [ ! -f ".env" ]; then
  echo "!! backend/.env missing. Copy backend/.env.example to backend/.env and add GEMINI_API_KEY."
  exit 1
fi

echo "Ingesting knowledge base (first run builds the vector store)..."
./.venv/bin/python -m scripts.ingest_kb

echo "Starting backend on http://127.0.0.1:8000 ..."
./.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# --- Frontend ---
cd "$ROOT/frontend"
if [ ! -d "node_modules" ]; then
  echo "Installing frontend deps..."
  npm install
fi
echo "Starting frontend on http://localhost:5173 ..."
npm run dev &
FRONTEND_PID=$!

trap "echo 'Stopping...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
