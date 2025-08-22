#!/bin/bash

# DCGM Agent Chat UI Startup Script
# This script starts both the backend and frontend services

set -e

UI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$UI_DIR/.." && pwd)"

echo "🚀 Starting DCGM Agent Chat UI..."
echo "Project root: $PROJECT_ROOT"
echo "UI directory: $UI_DIR"

# Check if we're in the right directory
if [[ ! -f "$PROJECT_ROOT/src/aiq_dgx_factory_reset/configs/dcgm_agent.yml" ]]; then
    echo "❌ Error: dcgm_agent.yml not found. Please run this script from the correct directory."
    echo "Expected: $PROJECT_ROOT/src/aiq_dgx_factory_reset/configs/dcgm_agent.yml"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check dependencies
echo "🔍 Checking dependencies..."

if ! command_exists python3; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is required but not installed."
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is required but not installed."
    exit 1
fi

echo "✅ Dependencies check passed"

# Create Python virtual environment if it doesn't exist
VENV_DIR="$UI_DIR/.venv"
if [[ ! -d "$VENV_DIR" ]]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo "🔧 Activating Python virtual environment..."
source "$VENV_DIR/bin/activate"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd "$UI_DIR/backend"
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Install the AIQ package in development mode
echo "📦 Installing AIQ package..."
cd "$PROJECT_ROOT"
pip install -q -e .

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd "$UI_DIR/frontend"
if [[ ! -d "node_modules" ]] || [[ "package.json" -nt "node_modules/.package-lock.json" ]]; then
    npm install
fi

# Build the frontend
echo "🏗️  Building frontend..."
npm run build

# Function to cleanup background processes
cleanup() {
    echo "🛑 Shutting down services..."
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

# Start the backend
echo "🚀 Starting backend server..."
cd "$UI_DIR/backend"
python main.py &
BACKEND_PID=$!

# Wait a moment for the backend to start
sleep 3

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start"
    exit 1
fi

# Start the frontend
echo "🚀 Starting frontend server..."
cd "$UI_DIR/frontend"
npm run start &
FRONTEND_PID=$!

# Wait a moment for the frontend to start
sleep 3

# Check if frontend is running
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "❌ Frontend failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo "🎉 DCGM Agent Chat UI is running!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📋 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user to stop the services
wait $BACKEND_PID $FRONTEND_PID
