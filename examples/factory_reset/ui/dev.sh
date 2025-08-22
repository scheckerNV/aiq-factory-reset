#!/bin/bash

# DCGM Agent Chat UI Development Script
# This script starts both backend and frontend in development mode

set -e

UI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$UI_DIR/.." && pwd)"

echo "🔧 Starting DCGM Agent Chat UI in development mode..."

# Function to cleanup background processes
cleanup() {
    echo "🛑 Shutting down development servers..."
    if [[ -n $BACKEND_PID ]]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [[ -n $FRONTEND_PID ]]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if virtual environment exists
VENV_DIR="$UI_DIR/.venv"
if [[ ! -d "$VENV_DIR" ]]; then
    echo "❌ Virtual environment not found. Please run ./start_ui.sh first to set up the environment."
    exit 1
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Start the backend in development mode
echo "🚀 Starting backend server (development mode)..."
cd "$UI_DIR/backend"
PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH" uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a moment for the backend to start
sleep 3

# Start the frontend in development mode
echo "🚀 Starting frontend server (development mode)..."
cd "$UI_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

# Wait a moment for the frontend to start
sleep 3

echo ""
echo "🎉 DCGM Agent Chat UI is running in development mode!"
echo ""
echo "📱 Frontend (dev): http://localhost:3000"
echo "🔧 Backend API (dev): http://localhost:8000"
echo "📋 API Docs: http://localhost:8000/docs"
echo ""
echo "Both servers will auto-reload on file changes"
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user to stop the services
wait $BACKEND_PID $FRONTEND_PID
