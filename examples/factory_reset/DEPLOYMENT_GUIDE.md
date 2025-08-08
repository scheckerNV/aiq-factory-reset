# 🚀 DGX Factory Reset - Deployment Guide

This guide will help you deploy the DGX Factory Reset Multi-Agent System to your virtual cluster.

## 🎯 Quick Start (TL;DR)

**For Docker Compose (Easiest):**
```bash
cd examples/factory_reset
./scripts/deploy.sh --nvidia-key YOUR_NVIDIA_API_KEY
```

**For Kubernetes:**
```bash
cd examples/factory_reset
./scripts/deploy_cluster.sh --nvidia-key YOUR_NVIDIA_API_KEY --registry your-registry.com
```

## 📋 Prerequisites

### Required
- **Docker** installed and running
- **NVIDIA API Key** for NIM access (get from [NVIDIA AI](https://www.nvidia.com/en-us/ai/))

### Optional for Kubernetes
- **kubectl** configured for your cluster
- **Container registry** access (Docker Hub, Harbor, etc.)

## 🐳 Docker Compose Deployment (Recommended)

### Option 1: Automated Script (Easiest)

```bash
# Navigate to factory reset directory
cd examples/factory_reset

# Deploy with NVIDIA API key
./scripts/deploy.sh --nvidia-key nvapi-YOUR_KEY_HERE

# Or with additional options
./scripts/deploy.sh \
  --nvidia-key nvapi-YOUR_KEY_HERE \
  --openai-key sk-YOUR_OPENAI_KEY \
  --config factory_reset_orchestrator.yml \
  --port 8080
```

### Option 2: Manual Docker Compose

```bash
# 1. Navigate to directory
cd examples/factory_reset

# 2. Copy environment template
cp env.template .env

# 3. Edit .env with your API keys
nano .env  # Update NVIDIA_API_KEY and other settings

# 4. Deploy services
docker compose up -d

# 5. Check status
docker compose ps
```

### Access Your Services

After deployment, access these URLs:
- **Factory Reset API**: http://localhost:8000
- **Redis Insight**: http://localhost:5540
- **Phoenix Observability**: http://localhost:6006

### Test the Deployment

```bash
# Test the API
curl -X POST http://localhost:8000/run \
  -H 'Content-Type: application/json' \
  -d '{"input": "What are the cmsh steps to add a node back to the BCM management network?"}'

# Check service health
curl http://localhost:8000/health
```

## ☸️ Kubernetes Deployment

### Option 1: Automated Script

```bash
# For local registry (like Docker Desktop)
./scripts/deploy_cluster.sh --nvidia-key nvapi-YOUR_KEY_HERE --registry localhost:5000

# For remote registry
./scripts/deploy_cluster.sh \
  --nvidia-key nvapi-YOUR_KEY_HERE \
  --registry your-registry.com \
  --tag v1.0.0 \
  --namespace aiq-factory-reset
```

### Option 2: Manual Kubernetes

```bash
# 1. Build and push image
docker build -f Dockerfile -t your-registry.com/aiq-factory-reset:latest ../..
docker push your-registry.com/aiq-factory-reset:latest

# 2. Create namespace
kubectl create namespace aiq-factory-reset

# 3. Create API key secret
kubectl create secret generic aiq-api-keys \
  --from-literal=nvidia-api-key="nvapi-YOUR_KEY_HERE" \
  --namespace=aiq-factory-reset

# 4. Deploy using generated manifests (from script)
kubectl apply -f k8s/

# 5. Wait for deployment
kubectl wait --for=condition=available --timeout=300s deployment/factory-reset -n aiq-factory-reset
```

### Access Services in Kubernetes

```bash
# Port-forward to access services
kubectl port-forward svc/factory-reset 8000:8000 -n aiq-factory-reset &
kubectl port-forward svc/phoenix 6006:6006 -n aiq-factory-reset &

# Test API
curl -X POST http://localhost:8000/run \
  -H 'Content-Type: application/json' \
  -d '{"input": "What are the factory reset steps for a DGX node?"}'
```

## 🔧 Configuration Options

### Available Configurations

Choose your configuration file based on your use case:

| Configuration | Purpose |
|---------------|---------|
| `network_agent.yml` | Network analysis and configuration (default) |
| `factory_reset_orchestrator.yml` | Complete multi-agent orchestration |
| `networking_expert.yml` | Networking-focused operations |
| `dgx_expert.yml` | DGX hardware-focused operations |

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NVIDIA_API_KEY` | NVIDIA NIM API Key (required) | - |
| `OPENAI_API_KEY` | OpenAI API Key (optional) | - |
| `AIQ_CONFIG_FILE` | Configuration file path | `network_agent.yml` |
| `AIQ_LOG_LEVEL` | Logging level | `INFO` |
| `FACTORY_RESET_PORT` | API port | `8000` |
| `REDIS_PORT` | Redis port | `6379` |
| `PHOENIX_UI_PORT` | Phoenix UI port | `6006` |

## 🛠️ Troubleshooting

### Common Issues

**1. API Key Issues**
```bash
# Check if API key is set correctly
docker compose logs factory-reset | grep -i "api key"

# Update API key
echo "NVIDIA_API_KEY=nvapi-NEW_KEY" >> .env
docker compose restart factory-reset
```

**2. Port Conflicts**
```bash
# Check what's using the port
lsof -i :8000

# Use different port
FACTORY_RESET_PORT=8080 docker compose up -d
```

**3. Service Not Starting**
```bash
# Check logs
docker compose logs factory-reset

# Restart specific service
docker compose restart factory-reset
```

**4. Health Check Failures**
```bash
# Check service health
curl http://localhost:8000/health

# View detailed logs
docker compose logs -f factory-reset
```

### Monitoring and Debugging

```bash
# View all logs
docker compose logs -f

# Monitor resource usage
docker stats

# Check service status
docker compose ps

# Connect to Redis for debugging
docker exec -it factory-reset-redis redis-cli

# View Phoenix observability
open http://localhost:6006
```

## 🔄 Management Commands

### Docker Compose

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# Restart services
docker compose restart

# Update and restart
docker compose up --build -d

# View logs
docker compose logs -f [service-name]

# Scale services (if needed)
docker compose up -d --scale factory-reset=2
```

### Kubernetes

```bash
# Check deployment status
kubectl get pods -n aiq-factory-reset

# View logs
kubectl logs -f deployment/factory-reset -n aiq-factory-reset

# Scale deployment
kubectl scale deployment factory-reset --replicas=2 -n aiq-factory-reset

# Update image
kubectl set image deployment/factory-reset factory-reset=your-registry.com/aiq-factory-reset:v2.0.0 -n aiq-factory-reset

# Delete deployment
kubectl delete namespace aiq-factory-reset
```

## 🎉 Success! What's Next?

Once deployed, you can:

1. **Explore the API** at http://localhost:8000
2. **Monitor with Phoenix** at http://localhost:6006
3. **Manage Redis** at http://localhost:5540
4. **Integrate with your systems** using the REST API
5. **Scale up** by adjusting replica counts

For more information, see the main [README.md](README.md) and explore the configuration files in `src/aiq_dgx_factory_reset/configs/`.
