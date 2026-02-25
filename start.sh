#!/bin/bash
# J.A.R.V.I.S. 3.0 — Startup Script
# Starts both backend and frontend servers

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "================================================="
echo "  J.A.R.V.I.S. 3.0 — Initializing Systems"
echo "================================================="

# Check for .env file
if [ ! -f "$SCRIPT_DIR/backend/.env" ]; then
    echo ""
    echo "[WARNING] No .env file found in backend/"
    echo "Copy .env.example to backend/.env and add your GEMINI_API_KEY"
    echo ""
fi

# Start Backend
echo ""
echo "[1/2] Starting Backend Server..."
cd "$SCRIPT_DIR/backend"
python main.py &
BACKEND_PID=$!
echo "  Backend PID: $BACKEND_PID"

# Wait for backend to initialize
sleep 3

# Start Frontend
echo ""
echo "[2/2] Starting Frontend Dev Server..."
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!
echo "  Frontend PID: $FRONTEND_PID"

echo ""
echo "================================================="
echo "  J.A.R.V.I.S. 3.0 — All Systems Online"
echo "================================================="
echo ""
echo "  Backend:  http://127.0.0.1:8000"
echo "  Frontend: http://localhost:5173"
echo ""
echo "  Press Ctrl+C to shutdown all services"
echo ""

# Cleanup on exit
cleanup() {
    echo ""
    echo "[Shutdown] Stopping all services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "[Shutdown] Goodbye, sir."
}

trap cleanup EXIT INT TERM

# Wait for both processes
wait
