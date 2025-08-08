#!/bin/bash
# SPDX-FileCopyrightText: Copyright (c) 2024-2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
NVIDIA_API_KEY=""
OPENAI_API_KEY=""
CONFIG_FILE="network_agent.yml"
PORT=8000

# Function to print colored output
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Function to show usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Deploy AIQ Factory Reset to Docker containers

OPTIONS:
    -n, --nvidia-key KEY     NVIDIA API Key (required)
    -o, --openai-key KEY     OpenAI API Key (optional)
    -c, --config CONFIG      Configuration file (default: network_agent.yml)
    -p, --port PORT          Port to expose (default: 8000)
    -h, --help               Show this help message

EXAMPLES:
    # Basic deployment with NVIDIA API key
    $0 --nvidia-key nvapi-xxx

    # Full deployment with both API keys
    $0 --nvidia-key nvapi-xxx --openai-key sk-xxx

    # Custom configuration and port
    $0 --nvidia-key nvapi-xxx --config factory_reset_orchestrator.yml --port 8080

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--nvidia-key)
            NVIDIA_API_KEY="$2"
            shift 2
            ;;
        -o|--openai-key)
            OPENAI_API_KEY="$2"
            shift 2
            ;;
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate required parameters
if [[ -z "$NVIDIA_API_KEY" ]]; then
    print_error "NVIDIA API Key is required"
    usage
    exit 1
fi

# Change to factory_reset directory
cd "$(dirname "$0")/.."
print_info "Working directory: $(pwd)"

# Check if Docker is installed and running
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! docker info &> /dev/null; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_success "Docker is installed and running"

# Create .env file
print_info "Creating .env file..."
cat > .env << EOF
# Auto-generated environment file
NVIDIA_API_KEY=$NVIDIA_API_KEY
OPENAI_API_KEY=$OPENAI_API_KEY
AIQ_CONFIG_FILE=/workspace/examples/factory_reset/src/aiq_dgx_factory_reset/configs/$CONFIG_FILE
FACTORY_RESET_PORT=$PORT
REDIS_PORT=6379
REDISINSIGHT_PORT=5540
PHOENIX_UI_PORT=6006
PHOENIX_GRPC_PORT=4317
AIQ_LOG_LEVEL=INFO
EOF

print_success "Environment file created"

# Create storage directory if it doesn't exist
mkdir -p storage
print_info "Storage directory ready"

# Stop any existing services
print_info "Stopping existing services..."
docker compose down 2>/dev/null || true

# Build and start services
print_info "Building and starting services..."
docker compose up --build -d

# Wait for services to be healthy
print_info "Waiting for services to be healthy..."
sleep 10

# Check service status
print_info "Checking service status..."
if docker compose ps | grep -q "Up"; then
    print_success "Services started successfully!"

    echo
    print_info "🎉 Deployment complete! Access your services:"
    echo "  • Factory Reset API: http://localhost:$PORT"
    echo "  • Redis Insight: http://localhost:5540"
    echo "  • Phoenix Observability: http://localhost:6006"
    echo
    print_info "📋 Useful commands:"
    echo "  • View logs: docker compose logs -f factory-reset"
    echo "  • Stop services: docker compose down"
    echo "  • Restart: docker compose restart"
    echo
    print_info "🧪 Test the API:"
    echo "  curl -X POST http://localhost:$PORT/run \\"
    echo "    -H 'Content-Type: application/json' \\"
    echo "    -d '{\"input\": \"What are the cmsh steps to add a node back to the BCM management network?\"}'"

else
    print_error "Some services failed to start. Check logs:"
    docker compose logs
    exit 1
fi
