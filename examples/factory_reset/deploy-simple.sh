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

# Function to print colored output
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

print_info "🚀 Deploying AIQ Factory Reset to your cluster..."

# Check if Docker image exists
print_info "📦 Checking if Docker image exists locally..."
if ! docker image inspect localhost:5000/aiq-factory-reset:latest &> /dev/null; then
    print_error "Docker image not found. Please build the image first:"
    print_error "  docker build -f examples/factory_reset/Dockerfile -t localhost:5000/aiq-factory-reset:latest ."
    exit 1
fi

print_success "✅ Docker image found locally"

# Create docker-compose file for cluster deployment
print_info "📝 Creating Docker Compose configuration..."
cat > docker-compose-cluster.yml << 'EOF'
version: '3.8'

services:
  factory-reset:
    image: localhost:5000/aiq-factory-reset:latest
    container_name: aiq-factory-reset
    ports:
      - "8000:8000"
    environment:
      - NVIDIA_API_KEY=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
      - AIQ_CONFIG_FILE=/workspace/examples/factory_reset/src/aiq_dgx_factory_reset/configs/simple_network.yml
      - AIQ_LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/docs"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

EOF

# Stop any existing deployment
print_info "🛑 Stopping any existing deployment..."
docker compose -f docker-compose-cluster.yml down 2>/dev/null || true

# Deploy the service
print_info "🚀 Starting AIQ Factory Reset service..."
docker compose -f docker-compose-cluster.yml up -d

# Wait for service to be ready
print_info "⏳ Waiting for service to be ready..."
sleep 15

# Check status
print_info "📊 Checking deployment status..."
docker compose -f docker-compose-cluster.yml ps

# Get the server IP
SERVER_IP=$(hostname -I | awk '{print $1}')
if [ -z "$SERVER_IP" ]; then
    SERVER_IP="localhost"
fi

# Test the API
print_info "🧪 Testing API endpoint..."
if curl -s -f http://localhost:8000/docs > /dev/null; then
    print_success "🎉 Deployment successful!"
    print_success "🌐 Your AIQ Factory Reset API is now available at:"
    print_success "   http://${SERVER_IP}:8000"
    print_success "   API docs: http://${SERVER_IP}:8000/docs"

    print_info "🧪 Test the API with:"
    echo "curl -X POST http://${SERVER_IP}:8000/generate -H 'Content-Type: application/json' -d '{\"input_message\": \"What are the cmsh steps to add a node to the BCM network?\"}'"

    print_info "📋 Useful commands:"
    echo "  docker compose -f docker-compose-cluster.yml logs -f    # View logs"
    echo "  docker compose -f docker-compose-cluster.yml ps        # Check status"
    echo "  docker compose -f docker-compose-cluster.yml down      # Stop service"
else
    print_error "❌ Service not responding. Check logs:"
    docker compose -f docker-compose-cluster.yml logs
fi
