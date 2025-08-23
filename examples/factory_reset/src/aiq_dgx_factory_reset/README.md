# DCGM Expert: Setup and Usage

This guide shows how to set up DCGM monitoring and analysis tools that work with both single nodes and BCM-managed clusters (DGX, GB300, H100, etc.).

## 1) Prerequisites

### On Compute Nodes (GPU nodes)
Each compute node with GPUs needs:
- **NVIDIA driver installed**: GPUs must be visible to the system
- **DCGM hostengine running**:
```bash
sudo systemctl enable --now nvidia-dcgm
# Verify DCGM is working
dcgmi discovery -l
```
- **Docker + NVIDIA Container Toolkit** (for monitoring stack):
```bash
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
# Sanity check
docker run --rm --gpus all nvidia/cuda:12.3.2-base-ubuntu22.04 nvidia-smi
```

### On Management/Head Node (where you run the tools)
- **SSH access to compute nodes**: Passwordless SSH must work to all target nodes
```bash
# Test SSH access to your compute nodes
ssh <compute_node_ip> 'dcgmi discovery -l'
```
- **BCM cluster management**: For auto-discovery via `cmsh -c "device list"`
- **Python environment**: AIQ toolkit installed and configured

### Network Requirements
- **Compute nodes reachable**: SSH connectivity from management node to compute nodes
- **Port accessibility**: For distributed monitoring (dcgm-exporter: 9400, Prometheus: 9090, Grafana: 3000)
- **DNS/IP resolution**: Nodes must be accessible by hostname or IP

## 2) Usage Modes

### Single Node Mode (Original dcgm_register.py)
Run tools directly on a GPU compute node with local DCGM and Docker.

### Cluster Mode (New cluster DCGM tools)
Run tools from a management/head node to analyze multiple GPU compute nodes via SSH.

## 3) Environment Configuration

### For Single Node Mode
Use localhost for API calls from the agent running on GPU node:
```bash
export PROM_URL=http://localhost:9090
export GRAFANA_URL=http://localhost:3000
export GRAFANA_ADMIN_PASSWORD='NewStrongPass!'
export GF_CREDS=admin:$GRAFANA_ADMIN_PASSWORD
```

### For Cluster Mode
Configure for distributed monitoring across multiple nodes:
```bash
# Central monitoring node (usually headnode)
export CLUSTER_HOST="bcm11-headnode"  # Your headnode hostname
export CLUSTER_USER="hpcuser1"        # SSH user for compute nodes
export PROM_URL=http://<HEADNODE_IP>:9090
export GRAFANA_URL=http://<HEADNODE_IP>:3000
export PUBLIC_HOST=<HEADNODE_IP>
export GRAFANA_ADMIN_PASSWORD='NewStrongPass!'
export GF_CREDS=admin:$GRAFANA_ADMIN_PASSWORD
```

Optional persistence for Grafana:
```bash
# Preferred: named volume
docker volume create grafana-data
# Or host dir (ensure uid 472 owns it)
# sudo mkdir -p /var/lib/grafana && sudo chown -R 472:472 /var/lib/grafana
```

## 4) DCGM Analysis Tools

### Cluster-wide Analysis (Recommended for BCM clusters)

#### Quick Cluster GPU Status
Get GPU status across all compute nodes:
```bash
aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/cluster_dcgm_agent.yml \
  --input "cluster_gpu_status"
```

#### Target Specific Nodes
Analyze specific nodes or IP ranges:
```bash
# Specific nodes by hostname pattern
aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/cluster_dcgm_agent.yml \
  --input "cluster_gpu_status nodes=r1-p1-gb300-n01,r1-p1-gb300-n02"

# IP range
aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/cluster_dcgm_agent.yml \
  --input "cluster_gpu_status nodes=10.102.112.15-20"
```

#### Cluster Health Checks
Enable DCGM health monitoring across the cluster:
```bash
aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/cluster_dcgm_agent.yml \
  --input "cluster_gpu_enable_health systems=all"

# Wait for health data to collect (~60s), then check
aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/cluster_dcgm_agent.yml \
  --input "cluster_gpu_health_check"
```

#### Run Cluster Diagnostics
Execute DCGM diagnostics across multiple nodes:
```bash
aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/cluster_dcgm_agent.yml \
  --input "cluster_gpu_diagnostics level=r2 nodes=all"
```

### Single Node Analysis (Original tools)

#### Start monitoring stack on current node
```bash
aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/dcgm_agent.yml --input "prom_stack_start"
```

#### Single node GPU status and diagnostics
```bash
# Check GPU health on current node
aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/dcgm_agent.yml --input "gpu_status"

# Run diagnostics on current node
aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/dcgm_agent.yml --input "gpu_run_diagnostics level=r2"
```

## 5) Distributed Monitoring Setup

### Deploy dcgm-exporter across cluster nodes
Deploy monitoring stack across multiple nodes:
```bash
# Deploy to all compute nodes
aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/cluster_dcgm_agent.yml \
  --input "cluster_deploy_monitoring nodes=all"

# Deploy to specific nodes
aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/cluster_dcgm_agent.yml \
  --input "cluster_deploy_monitoring nodes=10.102.112.15-20"
```

### Create cluster-wide dashboards
```bash
# Create comprehensive cluster dashboard
aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/cluster_dcgm_agent.yml \
  --input "cluster_create_dashboard name=GB300_Cluster_Overview"
```

## 6) Accessing Monitoring Services

### Local Access (same network)
- **Prometheus**: http://\<HEADNODE_IP\>:9090
- **Grafana**: http://\<HEADNODE_IP\>:3000

### Remote Access (SSH tunnel)
```bash
# Create SSH tunnel for Grafana
ssh -L 3001:localhost:3000 <username>@<headnode_ip>
# Then access: http://localhost:3001
```

## 7) Troubleshooting

### Verify Prerequisites
```bash
# Test SSH access to compute nodes
ssh <compute_node_ip> 'dcgmi discovery -l'

# Check BCM node discovery
cmsh -c "device list -f ip,hostname,category"

# Verify DCGM on specific node
ssh <compute_node_ip> 'systemctl status nvidia-dcgm'
```

### Check Service Health
```bash
# Health codes for single-node monitoring
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:9400/metrics
curl -s -o /dev/null -w '%{http_code}\n' $PROM_URL/-/ready
curl -s -o /dev/null -w '%{http_code}\n' $GRAFANA_URL/api/health

# Container state and logs
docker ps --format 'table {{.Names}}\t{{.Status}}'
docker logs --tail=200 grafana

# Check cluster-wide DCGM health
aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/cluster_dcgm_agent.yml \
  --input "cluster_health_check"
```

### Common Issues
- **SSH failures**: Verify passwordless SSH and correct usernames
- **DCGM not found**: Ensure `nvidia-dcgm` service is running on compute nodes
- **No GPU discovery**: Check NVIDIA drivers and GPU visibility
- **Permission denied**: May need sudo access for Docker operations
- **Port conflicts**: Check if monitoring ports (9090, 3000, 9400) are available

## 8) Files of Interest

### Configuration Files
- **Single node config**: `examples/factory_reset/src/aiq_dgx_factory_reset/configs/dcgm_agent.yml`
- **Cluster config**: `examples/factory_reset/src/aiq_dgx_factory_reset/configs/cluster_dcgm_agent.yml`

### Tool Implementation Files
- **Single node tools**: `examples/factory_reset/src/aiq_dgx_factory_reset/dcgm_register.py`
- **Cluster tools**: `examples/factory_reset/src/aiq_dgx_factory_reset/cluster_dcgm_register.py`
- **Node assessment**: `examples/factory_reset/scripts/node_assessment.sh`

### Example Usage for Your GB300 System
Based on your setup, here are specific commands:
```bash
# Get status of all 18 GB300 nodes
aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/cluster_dcgm_agent.yml \
  --input "cluster_gpu_status nodes=10.102.112.15-32"

# Enable health monitoring on your GB300 cluster
aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/cluster_dcgm_agent.yml \
  --input "cluster_gpu_enable_health systems=all nodes=r1-p1-gb300-n01-18"
```
