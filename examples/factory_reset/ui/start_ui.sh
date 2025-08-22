#!/bin/bash

# DCGM Agent Chat UI Startup Script
# This script starts both the backend and frontend services

set -e

UI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$UI_DIR/../../.." && pwd)"

echo "🚀 Starting DCGM Agent Chat UI..."
echo "Project root: $PROJECT_ROOT"
echo "UI directory: $UI_DIR"

FACTORY_ROOT="$(cd "$UI_DIR/../.." && pwd)"  # …/examples/factory_reset
CONFIG_PATH="$FACTORY_ROOT/src/aiq_dgx_factory_reset/configs/dcgm_agent.yml"
ALT_CONFIG="$PROJECT_ROOT/src/aiq_dgx_factory_reset/configs/dcgm_agent.yml"

if [[ -f "$CONFIG_PATH" ]]; then
    echo "✅ Found config at $CONFIG_PATH"
elif [[ -f "$ALT_CONFIG" ]]; then
    echo "✅ Found config at $ALT_CONFIG"
    CONFIG_PATH="$ALT_CONFIG"
else
    echo "❌ Error: dcgm_agent.yml not found."
    echo "Checked:"
    echo " - $CONFIG_PATH"
    echo " - $ALT_CONFIG"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to find an available port using ss (more reliable than lsof)
find_available_port() {
    local start_port=${1:-3100}  # Start at 3100 to skip Grafana's 3000
    local max_port=$((start_port + 100))

    for port in $(seq $start_port $max_port); do
        # Use ss to check if port is in use (more reliable than lsof)
        if ! ss -H -ltn | awk '{print $4}' | grep -q "[:.]:$port$"; then
            echo $port
            return
        fi
    done

    # If no port found in range, try high ports
    for port in $(seq 8000 8050); do
        if ! ss -H -ltn | awk '{print $4}' | grep -q "[:.]:$port$"; then
            echo $port
            return
        fi
    done

    # Last resort - use a random high port
    echo $((RANDOM % 1000 + 9000))
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

VENV_DIR="$PROJECT_ROOT/.venv"
if [[ ! -d "$VENV_DIR" ]]; then
    echo "❌ Missing venv at $VENV_DIR; create it with: python3 -m venv $VENV_DIR && source $VENV_DIR/bin/activate && pip install -e ."
    exit 1
fi
source "$VENV_DIR/bin/activate"
echo "📦 Using project virtual environment: $VENV_DIR"

# Python dependencies are already installed in the root venv
# (Commenting out to prevent version drift on every run)
# echo "📦 Installing Python dependencies..."
# cd "$UI_DIR/backend"
# pip install -q --upgrade pip
#
# # Install requirements with better error handling
# echo "📦 Installing backend requirements..."
# if ! pip install -r requirements.txt; then
#     echo "❌ Failed to install Python dependencies. Please check your internet connection and try again."
#     exit 1
# fi
#
# # Install the AIQ package in development mode with all dependencies
# echo "📦 Installing AIQ package with all dependencies..."
# cd "$PROJECT_ROOT"
# if ! pip install -e .; then
#     echo "❌ Failed to install AIQ package. Please check the project structure."
#     exit 1
# fi

# Verify critical dependencies
echo "📦 Verifying critical dependencies..."
python3 -c "
import sys

# Test basic dependencies
basic_modules = ['fastapi', 'uvicorn', 'langchain', 'langgraph']
missing = []
for module in basic_modules:
    try:
        __import__(module)
        print(f'✅ {module} - OK')
    except ImportError:
        missing.append(module)
        print(f'❌ {module} - MISSING')

# Test specific langgraph import that NAT react agent needs
try:
    from langgraph.graph.graph import CompiledGraph
    print('✅ langgraph.graph.graph.CompiledGraph - OK (NAT react agent compatible)')
except ImportError as e:
    missing.append('langgraph.graph.graph')
    print(f'❌ langgraph.graph.graph.CompiledGraph - MISSING')
    print(f'    Error: {e}')
    print('    Hint: Try pip install \"langgraph<0.2.0\"')

if missing:
    print(f'❌ Missing or incompatible dependencies: {missing}')
    print('Please check the installation logs above.')
    sys.exit(1)
else:
    print('✅ All critical dependencies verified')
"

# Verify AIQ can load the config
echo "📦 Verifying AIQ configuration..."
python3 - <<'PY'
import yaml, sys
from pathlib import Path
config_path = Path(r"""'"$CONFIG_PATH"'""")
try:
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    print(f'✅ Loaded config: {config_path}')
    print(f'✅ {len(config.get("functions", {}))} functions, {len(config.get("llms", {}))} LLM(s)')
except Exception as e:
    print(f'❌ Configuration error: {e}')
    sys.exit(1)
PY

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

# Set environment variables for the backend
export DCGM_CONFIG="dcgm_agent.yml"
export NIM_BASE_URL="http://localhost:8000/v1"

# Verify environment setup
echo "🔧 Verifying environment configuration..."
echo "✅ DCGM_CONFIG: $DCGM_CONFIG"
echo "✅ NIM_BASE_URL: $NIM_BASE_URL"

# Verify NIM service is reachable
echo "🔍 Checking NIM service connectivity..."
if curl -s --max-time 5 "$NIM_BASE_URL" > /dev/null 2>&1; then
    echo "✅ NIM service is reachable at $NIM_BASE_URL"
else
    echo "⚠️  NIM service not reachable at $NIM_BASE_URL"
    echo "   Make sure your NIM container is running on port 8000"
    echo "   You can test with: curl $NIM_BASE_URL"
fi

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

# Find available port for frontend (allow override via env var)
echo "🔍 Finding available port for frontend..."
if [[ -z "$FRONTEND_PORT" ]]; then
    # Try using Node's detect-port for ultimate reliability
    if command_exists npx; then
        FRONTEND_PORT=$(npx -y detect-port 3100 2>/dev/null || find_available_port 3100)
    else
        FRONTEND_PORT=$(find_available_port 3100)
    fi
fi
echo "✅ Using port $FRONTEND_PORT for frontend"

# Start the frontend
echo "🚀 Starting frontend server..."
cd "$UI_DIR/frontend"
HOST=0.0.0.0 PORT=$FRONTEND_PORT npm run start -- -p "$FRONTEND_PORT" -H 0.0.0.0 &
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
echo "📱 Frontend: http://localhost:$FRONTEND_PORT"
echo "🔧 Backend API: http://localhost:8080"
echo "📋 API Docs: http://localhost:8080/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user to stop the services
wait $BACKEND_PID $FRONTEND_PID
