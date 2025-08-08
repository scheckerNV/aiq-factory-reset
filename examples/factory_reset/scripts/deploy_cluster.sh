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
REGISTRY=""
IMAGE_TAG="latest"
NAMESPACE="default"

# Function to print colored output
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Function to show usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Deploy AIQ Factory Reset to your virtual cluster

OPTIONS:
    -n, --nvidia-key KEY     NVIDIA API Key (required)
    -r, --registry REGISTRY  Container registry (e.g., your-registry.com)
    -t, --tag TAG           Image tag (default: latest)
    -ns, --namespace NS     Kubernetes namespace (default: default)
    -h, --help              Show this help message

EXAMPLES:
    # Deploy to local cluster with Docker registry
    $0 --nvidia-key nvapi-xxx --registry localhost:5000

    # Deploy to remote cluster
    $0 --nvidia-key nvapi-xxx --registry your-registry.com --tag v1.0.0 --namespace aiq

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--nvidia-key)
            NVIDIA_API_KEY="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        -t|--tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        -ns|--namespace)
            NAMESPACE="$2"
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

# Build image
IMAGE_NAME="aiq-factory-reset"
if [[ -n "$REGISTRY" ]]; then
    FULL_IMAGE_NAME="$REGISTRY/$IMAGE_NAME:$IMAGE_TAG"
else
    FULL_IMAGE_NAME="$IMAGE_NAME:$IMAGE_TAG"
fi

print_info "Building Docker image: $FULL_IMAGE_NAME"
docker build -f Dockerfile -t "$FULL_IMAGE_NAME" ../..

# Push to registry if specified
if [[ -n "$REGISTRY" ]]; then
    print_info "Pushing to registry: $REGISTRY"
    docker push "$FULL_IMAGE_NAME"
fi

# Create Kubernetes manifests
print_info "Creating Kubernetes manifests..."
mkdir -p k8s

# Create namespace
cat > k8s/namespace.yaml << EOF
apiVersion: v1
kind: Namespace
metadata:
  name: $NAMESPACE
EOF

# Create secret for API keys
kubectl create secret generic aiq-api-keys \
    --from-literal=nvidia-api-key="$NVIDIA_API_KEY" \
    --namespace="$NAMESPACE" \
    --dry-run=client -o yaml > k8s/secret.yaml

# Create Redis deployment
cat > k8s/redis.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: $NAMESPACE
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:8.0
        ports:
        - containerPort: 6379
        command: ["redis-server", "--save", "60", "1", "--loglevel", "warning"]
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: $NAMESPACE
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
EOF

# Create Phoenix deployment
cat > k8s/phoenix.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: phoenix
  namespace: $NAMESPACE
spec:
  replicas: 1
  selector:
    matchLabels:
      app: phoenix
  template:
    metadata:
      labels:
        app: phoenix
    spec:
      containers:
      - name: phoenix
        image: arizephoenix/phoenix:latest
        ports:
        - containerPort: 6006
        - containerPort: 4317
        resources:
          requests:
            memory: "512Mi"
            cpu: "200m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: phoenix
  namespace: $NAMESPACE
spec:
  selector:
    app: phoenix
  ports:
  - name: ui
    port: 6006
    targetPort: 6006
  - name: grpc
    port: 4317
    targetPort: 4317
  type: ClusterIP
EOF

# Create Factory Reset deployment
cat > k8s/factory-reset.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: factory-reset
  namespace: $NAMESPACE
spec:
  replicas: 1
  selector:
    matchLabels:
      app: factory-reset
  template:
    metadata:
      labels:
        app: factory-reset
    spec:
      containers:
      - name: factory-reset
        image: $FULL_IMAGE_NAME
        ports:
        - containerPort: 8000
        env:
        - name: NVIDIA_API_KEY
          valueFrom:
            secretKeyRef:
              name: aiq-api-keys
              key: nvidia-api-key
        - name: AIQ_CONFIG_FILE
          value: "/workspace/examples/factory_reset/src/aiq_dgx_factory_reset/configs/network_agent.yml"
        - name: AIQ_LOG_LEVEL
          value: "INFO"
        - name: REDIS_HOST
          value: "redis"
        - name: REDIS_PORT
          value: "6379"
        - name: PHOENIX_COLLECTOR_ENDPOINT
          value: "http://phoenix:4317"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: factory-reset
  namespace: $NAMESPACE
spec:
  selector:
    app: factory-reset
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: factory-reset-ingress
  namespace: $NAMESPACE
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: factory-reset.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: factory-reset
            port:
              number: 8000
EOF

print_success "Kubernetes manifests created in k8s/ directory"

# Apply manifests
print_info "Deploying to Kubernetes cluster..."
kubectl apply -f k8s/

print_info "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/redis -n "$NAMESPACE"
kubectl wait --for=condition=available --timeout=300s deployment/phoenix -n "$NAMESPACE"
kubectl wait --for=condition=available --timeout=300s deployment/factory-reset -n "$NAMESPACE"

print_success "🎉 Deployment complete!"
echo
print_info "📋 Access your services:"
echo "  • Port-forward Factory Reset: kubectl port-forward svc/factory-reset 8000:8000 -n $NAMESPACE"
echo "  • Port-forward Phoenix: kubectl port-forward svc/phoenix 6006:6006 -n $NAMESPACE"
echo
print_info "📊 Monitor deployment:"
echo "  • Check pods: kubectl get pods -n $NAMESPACE"
echo "  • Check services: kubectl get svc -n $NAMESPACE"
echo "  • View logs: kubectl logs -f deployment/factory-reset -n $NAMESPACE"
echo
print_info "🧪 Test the API (after port-forwarding):"
echo "  curl -X POST http://localhost:8000/run \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"input\": \"What are the cmsh steps to add a node back to the BCM management network?\"}'"
