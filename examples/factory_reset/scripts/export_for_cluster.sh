#!/bin/bash
# SPDX-FileCopyrightText: Copyright (c) 2024-2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

set -e

# Script to export factory reset container for cluster deployment
# Usage: ./scripts/export_for_cluster.sh [output-file] [image-tag]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FACTORY_RESET_DIR="$(dirname "$SCRIPT_DIR")"

# Default values
OUTPUT_FILE="${1:-factory-reset-container.tar}"
IMAGE_TAG="${2:-production}"
IMAGE_NAME="aiq-factory-reset"

echo "📦 Exporting Factory Reset Container for Cluster Deployment"
echo ""
echo "Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "Output: ${OUTPUT_FILE}"
echo ""

# Check if image exists, build if not
if ! docker image inspect "${IMAGE_NAME}:${IMAGE_TAG}" &> /dev/null; then
    echo "🔨 Image ${IMAGE_NAME}:${IMAGE_TAG} not found, building..."
    cd "$FACTORY_RESET_DIR"
    DOCKER_IMAGE_TAG="$IMAGE_TAG" ./scripts/docker_build.sh
    echo ""
fi

echo "💾 Exporting container image..."
docker save "${IMAGE_NAME}:${IMAGE_TAG}" > "${OUTPUT_FILE}"

echo "✅ Export completed!"
echo ""
echo "📁 File: ${OUTPUT_FILE}"
echo "📊 Size: $(du -h "${OUTPUT_FILE}" | cut -f1)"
echo ""
echo "🚢 To deploy on cluster:"
echo ""
echo "1. Copy to cluster node:"
echo "   scp ${OUTPUT_FILE} user@cluster-node:/tmp/"
echo ""
echo "2. Load on cluster node:"
echo "   ssh user@cluster-node"
echo "   docker load < /tmp/${OUTPUT_FILE}"
echo ""
echo "3. Run on cluster:"
echo "   docker run -d \\"
echo "     --name factory-reset \\"
echo "     -p 8000:8000 \\"
echo "     -e NVIDIA_API_KEY=your-api-key \\"
echo "     -v /data/factory-reset:/workspace/examples/factory_reset/storage \\"
echo "     ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""
echo "4. Or use with docker-compose:"
echo "   # Copy docker-compose.yml to cluster"
echo "   # Update image name in docker-compose.yml"
echo "   # docker compose up -d"
echo ""

# Create a simple deployment script
DEPLOY_SCRIPT="deploy_to_cluster.sh"
cat > "$DEPLOY_SCRIPT" << EOF
#!/bin/bash
# Auto-generated deployment script for cluster

set -e

echo "🚀 Deploying Factory Reset to cluster..."

# Load the container image
if [[ -f "${OUTPUT_FILE}" ]]; then
    echo "📦 Loading container image..."
    docker load < "${OUTPUT_FILE}"
else
    echo "❌ Container file ${OUTPUT_FILE} not found!"
    exit 1
fi

# Create data directory
sudo mkdir -p /data/factory-reset/storage
sudo chown \$USER:\$USER /data/factory-reset/storage

# Stop existing container if running
docker stop factory-reset 2>/dev/null || true
docker rm factory-reset 2>/dev/null || true

# Run the container
echo "🏃 Starting Factory Reset container..."
docker run -d \\
    --name factory-reset \\
    --restart unless-stopped \\
    -p 8000:8000 \\
    -e NVIDIA_API_KEY=\${NVIDIA_API_KEY} \\
    -v /data/factory-reset:/workspace/examples/factory_reset/storage \\
    ${IMAGE_NAME}:${IMAGE_TAG}

echo "✅ Factory Reset deployed successfully!"
echo ""
echo "🌐 Access at: http://\$(hostname -I | awk '{print \$1}'):8000"
echo "📋 Check status: docker ps"
echo "📊 View logs: docker logs -f factory-reset"

EOF

chmod +x "$DEPLOY_SCRIPT"

echo "📋 Created deployment script: $DEPLOY_SCRIPT"
echo "   Transfer this script along with the container file to your cluster"
echo ""
echo "🔐 Remember to set NVIDIA_API_KEY environment variable on the cluster:"
echo "   export NVIDIA_API_KEY=your-actual-api-key"
echo "   ./$DEPLOY_SCRIPT"
