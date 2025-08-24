#!/bin/bash

# DCGM Agent Chat UI Startup Script
# This script starts both the backend and frontend services

set -e

UI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$UI_DIR/../../.." && pwd)"

echo "🚀 Starting DCGM Agent Chat UI..."
echo "Project root: $PROJECT_ROOT"
echo "UI directory: $UI_DIR"

FACTORY_ROOT="$(cd "$UI_DIR/.." && pwd)"  # …/examples/factory_reset
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
echo "Config resolved to: $CONFIG_PATH"
test -f "$CONFIG_PATH" && ls -l "$CONFIG_PATH" || { echo "Config missing"; exit 1; }

python3 - "$CONFIG_PATH" <<'PY'
import yaml, sys
from pathlib import Path
config_path = Path(sys.argv[1])
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
export DCGM_CONFIG="$CONFIG_PATH"
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

# Find available port for backend (avoiding common service ports)
echo "🔍 Finding available port for backend..."
if [[ -z "$BACKEND_PORT" ]]; then
    # Avoid 3000 (Grafana), 8000 (NIM), 9090 (Prometheus), 9400 (DCGM)
    # Start from 8100 to avoid conflicts
    BACKEND_PORT=8100
    for port in {8100..8200}; do
        if ! ss -H -ltn sport = :$port 2>/dev/null | grep -q "LISTEN"; then
            BACKEND_PORT=$port
            break
        fi
    done
fi
echo "✅ Using port $BACKEND_PORT for backend"
export BACKEND_PORT

# Set the full config path for backend
export DCGM_CONFIG="$CONFIG_PATH"

# Start the backend
echo "🚀 Starting backend server..."
cd "$UI_DIR/backend"
python main.py &
BACKEND_PID=$!

# Wait a moment for the backend to start
sleep 5

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start"
    echo "Check if port $BACKEND_PORT is available:"
    ss -tlpn | grep ":$BACKEND_PORT " || echo "Port appears to be free"
    exit 1
fi

# Verify backend is responding
echo "🔍 Verifying backend is responding..."
for i in {1..10}; do
    if curl -s -f "http://localhost:$BACKEND_PORT/health" >/dev/null 2>&1; then
        echo "✅ Backend is responding on port $BACKEND_PORT"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "❌ Backend not responding after 10 seconds"
        echo "Backend logs might show the issue. Check the terminal where it's running."
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

# Find available port for frontend (avoiding common service ports)
echo "🔍 Finding available port for frontend..."
if [[ -z "$FRONTEND_PORT" ]]; then
    # Avoid 3000 (Grafana) - start from 3100
    FRONTEND_PORT=3100
    for port in {3100..3200}; do
        if ! ss -H -ltn sport = :$port 2>/dev/null | grep -q "LISTEN"; then
            FRONTEND_PORT=$port
            break
        fi
    done
fi
echo "✅ Using port $FRONTEND_PORT for frontend"

# Now build the frontend with the correct backend port
echo "🏗️  Building frontend..."
echo "Frontend will connect to backend on port $BACKEND_PORT"

# Set environment variables for frontend to connect to backend
export NEXT_PUBLIC_BACKEND_URL="http://localhost:$BACKEND_PORT"
export NEXT_PUBLIC_WS_BACKEND_URL="ws://localhost:$BACKEND_PORT"
echo "WebSocket will connect to: $NEXT_PUBLIC_WS_BACKEND_URL"

cd "$UI_DIR/frontend"
NEXT_PUBLIC_BACKEND_URL="$NEXT_PUBLIC_BACKEND_URL" \
NEXT_PUBLIC_WS_BACKEND_URL="$NEXT_PUBLIC_WS_BACKEND_URL" \
BACKEND_PORT=$BACKEND_PORT npm run build

# Start the frontend
echo "🚀 Starting frontend server..."
cd "$UI_DIR/frontend"
HOST=0.0.0.0 PORT=$FRONTEND_PORT \
NEXT_PUBLIC_BACKEND_URL="$NEXT_PUBLIC_BACKEND_URL" \
NEXT_PUBLIC_WS_BACKEND_URL="$NEXT_PUBLIC_WS_BACKEND_URL" \
BACKEND_PORT=$BACKEND_PORT npm run start -- -p "$FRONTEND_PORT" -H 0.0.0.0 &
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
echo "🔧 Backend API: http://localhost:$BACKEND_PORT"
echo "📋 API Docs: http://localhost:$BACKEND_PORT/docs"
echo "⚙️  Config: $(basename "$DCGM_CONFIG")"
echo ""
echo "Ports used (avoiding conflicts with Grafana:3000, Prometheus:9090, DCGM:9400):"
echo "  Backend: $BACKEND_PORT (range: 8100-8200)"
echo "  Frontend: $FRONTEND_PORT (range: 3100-3200)"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user to stop the services
wait $BACKEND_PID $FRONTEND_PID
