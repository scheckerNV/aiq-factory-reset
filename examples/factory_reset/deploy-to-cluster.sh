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

print_info "🚀 Deploying AIQ Factory Reset to Kubernetes cluster..."

# Check if we're on the cluster
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl not found. Please run this script on your cluster node."
    exit 1
fi

print_info "📦 Checking if Docker image exists locally..."
if ! docker image inspect localhost:5000/aiq-factory-reset:latest &> /dev/null; then
    print_error "Docker image not found. Please build the image first:"
    print_error "  docker build -f examples/factory_reset/Dockerfile -t localhost:5000/aiq-factory-reset:latest ."
    exit 1
fi

print_success "✅ Docker image found locally"

print_info "☸️  Applying Kubernetes manifests..."
kubectl apply -f k8s-manifests.yml

print_info "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/aiq-factory-reset

print_success "🎉 Deployment completed!"

print_info "📊 Getting deployment status..."
kubectl get pods -l app=aiq-factory-reset
kubectl get svc aiq-factory-reset-service

# Get the node IP for access instructions
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
if [ -z "$NODE_IP" ]; then
    NODE_IP=$(hostname -I | awk '{print $1}')
fi

print_success "🌐 Your AIQ Factory Reset API is now available at:"
print_success "   http://${NODE_IP}:30800"
print_success "   API docs: http://${NODE_IP}:30800/docs"

print_info "🧪 Test the API with:"
echo "curl -X POST http://${NODE_IP}:30800/generate -H 'Content-Type: application/json' -d '{\"input_message\": \"What are the cmsh steps to add a node to the BCM network?\"}'"

print_info "📋 Useful commands:"
echo "  kubectl logs -l app=aiq-factory-reset -f    # View logs"
echo "  kubectl get pods -l app=aiq-factory-reset    # Check pod status"
echo "  kubectl delete -f k8s-manifests.yml         # Remove deployment"
