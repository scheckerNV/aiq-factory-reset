# Cluster DCGM Monitoring: Setup and Usage Guide

This guide shows how to set up cluster-wide DCGM (Data Center GPU Manager) monitoring and analysis using the NeMo Agent toolkit. The tools work with BCM-managed GPU clusters (DGX, GB300, H100, etc.) and provide comprehensive GPU telemetry through Prometheus and Grafana.

## Prerequisites

### GPU Compute Nodes
Each GPU compute node requires:

- **NVIDIA drivers**: GPUs must be visible to the system
- **DCGM service running**:
  ```bash
  sudo systemctl enable --now nvidia-dcgm
  # Verify DCGM is working
  dcgmi discovery -l
  ```
- **Docker engine**: Any Docker-compatible engine (Docker CE, cm-docker, etc.)
- **Network connectivity**: Accessible via SSH from management node

### Management/Head Node
The node where you run the monitoring tools needs:

- **SSH access**: Passwordless SSH to all target GPU nodes
- **NeMo Agent toolkit**: Installed and configured
- **Network access**: Can reach GPU nodes and monitoring services
- **Optional**: BCM cluster management for auto-discovery

### Network Requirements
- **SSH connectivity**: From management node to all GPU nodes
- **Port accessibility**:
  - dcgm-exporter: 9400
  - Prometheus: 9090
  - Grafana: 3000
- **DNS/IP resolution**: Nodes accessible by hostname or IP address

## Environment Setup

Set these environment variables on your management node:

```bash
# Cluster configuration
export CLUSTER_HOST="your-headnode"     # Your management node hostname
export CLUSTER_USER="your-ssh-user"    # SSH username for GPU nodes
export MON_NODE="monitoring-node"      # Node where Prometheus/Grafana will run

# Monitoring service URLs
export PROM_URL=http://$MON_NODE:9090
export GRAFANA_URL=http://$MON_NODE:3000
export GRAFANA_ADMIN_PASSWORD='NewStrongPass!'
export GF_CREDS=admin:$GRAFANA_ADMIN_PASSWORD

# For NAT CLI
export OPENAI_API_KEY="dummy-key-for-local-nim"  # Or your actual API key
```

## Step-by-Step Setup

### 1. Prepare GPU Nodes

Ensure Docker and DCGM are running on all GPU compute nodes:

```bash
# Test SSH access and DCGM on each node
ssh <gpu-node> 'dcgmi discovery -l'

# Verify Docker is running
ssh <gpu-node> 'docker --version && systemctl is-active docker'
```

### 2. Deploy DCGM Exporters

Deploy dcgm-exporter containers on all GPU nodes. You can do this manually or use the cluster deployment tool:

#### Manual Deployment (for each GPU node):
```bash
ssh <gpu-node> '
  sudo systemctl enable --now nvidia-dcgm
  sudo docker rm -f dcgm-exporter 2>/dev/null || true
  sudo docker run -d --restart unless-stopped --name dcgm-exporter \
    --net=host --gpus all \
    nvcr.io/nvidia/k8s/dcgm-exporter:3.3.5-3.4.0-ubuntu22.04
'
```

#### Automated Deployment (using NAT tool):
```bash
nat run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/cluster_dcgm_agent.yml \
  --input "cluster_deploy_monitoring nodes=all"
```

### 3. Set Up Centralized Monitoring

Deploy Prometheus and Grafana on your designated monitoring node:

```bash
# Create directories for persistent data
ssh $MON_NODE 'sudo mkdir -p /srv/monitoring/{prom,prom-data,grafana}'

# Create Prometheus targets file (replace with your actual node hostnames/IPs)
ssh $MON_NODE 'cat >/tmp/dcgm_targets.json <<EOF
[
  { "labels": { "job": "dcgm" }, "targets": [
    "gpu-node-01:9400", "gpu-node-02:9400", "gpu-node-03:9400"
  ] }
]
EOF
sudo mv /tmp/dcgm_targets.json /srv/monitoring/prom/'

# Create Prometheus configuration
ssh $MON_NODE 'cat >/tmp/prometheus.yml <<EOF
global:
  scrape_interval: 5s
  scrape_timeout: 4s
scrape_configs:
  - job_name: "dcgm"
    file_sd_configs:
      - files: ["/etc/prometheus/dcgm_targets.json"]
EOF
sudo mv /tmp/prometheus.yml /srv/monitoring/prom/'

# Deploy Prometheus and Grafana containers
ssh $MON_NODE '
  sudo docker rm -f prometheus grafana 2>/dev/null || true

  # Fix permissions
  sudo chown -R 65534:65534 /srv/monitoring/prom-data
  sudo chown -R 472:472 /srv/monitoring/grafana

  # Start Prometheus
  sudo docker run -d --restart unless-stopped --name prometheus --net=host \
    -v /srv/monitoring/prom:/etc/prometheus:ro \
    -v /srv/monitoring/prom-data:/prometheus \
    prom/prometheus:latest \
    --config.file=/etc/prometheus/prometheus.yml \
    --storage.tsdb.retention.time=30d

  # Start Grafana
  sudo docker run -d --restart unless-stopped --name grafana --net=host \
    -e GF_SECURITY_ADMIN_PASSWORD="NewStrongPass!" \
    -v /srv/monitoring/grafana:/var/lib/grafana \
    grafana/grafana-oss:latest
'
```

### 4. Create Prometheus Datasource

Create the Prometheus datasource in Grafana:

```bash
curl -s -u admin:$GRAFANA_ADMIN_PASSWORD -H 'Content-Type: application/json' \
  -X POST http://$MON_NODE:3000/api/datasources \
  -d '{"name":"ClusterPrometheus","type":"prometheus","access":"proxy","url":"http://'"$MON_NODE"':9090","isDefault":true}'
```

### 5. Create Cluster Dashboard

Use the NAT tool to create a comprehensive cluster monitoring dashboard:

```bash
nat run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/cluster_dcgm_agent.yml \
  --input '{"name":"GPU Cluster Overview","refresh":"30s","grafana_host":"'"$MON_NODE"'","grafana_port":"3000","overwrite":"true"}'
```

The tool will output the dashboard URL and access instructions.

## Using the Monitoring Tools

### Cluster-Wide GPU Status
Get real-time GPU status across all nodes:

```bash
nat run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/cluster_dcgm_agent.yml \
  --input "cluster_gpu_status"
```

### Target Specific Nodes
Analyze specific nodes or IP ranges:

```bash
# Specific nodes
nat run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/cluster_dcgm_agent.yml \
  --input "cluster_gpu_status nodes=gpu-node-01,gpu-node-02"

# IP range
nat run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/cluster_dcgm_agent.yml \
  --input "cluster_gpu_status nodes=10.0.1.10-20"
```

### Enable Health Monitoring
Enable DCGM health checks across the cluster:

```bash
nat run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/cluster_dcgm_agent.yml \
  --input "cluster_gpu_enable_health systems=all"
```

Wait about 60 seconds for data collection, then check health status:

```bash
nat run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/cluster_dcgm_agent.yml \
  --input "cluster_gpu_health_check"
```

### Run Diagnostics
Execute DCGM diagnostics across multiple nodes:

```bash
nat run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/cluster_dcgm_agent.yml \
  --input "cluster_gpu_diagnostics level=r2 nodes=all"
```

## Accessing the Dashboard

### From Local Network
If you're on the same network as the monitoring node:
- **Prometheus**: http://your-monitoring-node:9090
- **Grafana**: http://your-monitoring-node:3000
- **Login**: admin / NewStrongPass!

### Remote Access via SSH Tunnel
If accessing from outside the cluster network:

```bash
# Create SSH tunnel (replace with your actual hostnames/IPs)
ssh -fN -L 3002:monitoring-node:3000 user@headnode-ip

# Then open in your browser
open http://localhost:3002
```

For jump host setups:
```bash
ssh -fN -J user@jump-host -L 3002:localhost:3000 user@monitoring-node
```

## Verification and Troubleshooting

### Check Service Status
```bash
# Verify containers are running
ssh $MON_NODE 'docker ps --format "table {{.Names}}\t{{.Status}}"'

# Check Prometheus targets
curl -s http://$MON_NODE:9090/api/v1/targets | jq '.data.activeTargets[].health'

# Test dcgm-exporter on any GPU node
ssh <gpu-node> 'curl -s http://localhost:9400/metrics | head -5'
```

### Common Issues and Solutions

**SSH Connection Failures**
- Verify passwordless SSH is configured
- Check SSH key authentication
- Ensure correct usernames for each node

**DCGM Not Found**
- Confirm `nvidia-dcgm` service is running: `systemctl status nvidia-dcgm`
- Check GPU driver installation: `nvidia-smi`
- Verify GPUs are visible: `dcgmi discovery -l`

**Container Issues**
- Check Docker daemon status: `systemctl status docker`
- Verify GPU runtime: `docker run --gpus all nvidia/cuda:latest nvidia-smi`
- Review container logs: `docker logs dcgm-exporter`

**Networking Problems**
- Test port connectivity: `nc -zv monitoring-node 9090`
- Check firewall rules
- Verify DNS resolution or use IP addresses

## Configuration Files

- **Cluster configuration**: `configs/cluster_dcgm_agent.yml`
- **Single node configuration**: `configs/dcgm_agent.yml`
- **Tool implementations**: `cluster_dcgm_register.py`, `dcgm_register.py`

## Advanced Usage

### Custom Dashboard Creation
Create dashboards with specific parameters:

```bash
nat run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/cluster_dcgm_agent.yml \
  --input '{"name":"Custom Dashboard","refresh":"10s","grafana_host":"monitoring-node","overwrite":false}'
```

### Monitoring Specific GPU Metrics
The dashboards automatically include:
- GPU temperatures across all nodes
- GPU utilization and power consumption
- Memory usage and errors
- NVLink status and bandwidth
- Cluster summary statistics

### Data Retention
Adjust Prometheus retention in the container startup:
```bash
--storage.tsdb.retention.time=30d  # Keep 30 days of data
```

This setup provides comprehensive, cluster-wide GPU monitoring with minimal overhead and maximum visibility into your GPU infrastructure health and performance.
