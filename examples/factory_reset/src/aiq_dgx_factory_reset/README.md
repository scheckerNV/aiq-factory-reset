# DCGM Expert: Setup and Usage

This guide shows how to bring up DCGM metrics (dcgm-exporter → Prometheus → Grafana) and use the DCGM Expert agent tools on a DGX node.

## 1) Prerequisites (on the DGX node)

- NVIDIA driver installed; GPUs visible
- DCGM hostengine running:
```bash
sudo systemctl enable --now nvidia-dcgm
```
- Docker + NVIDIA Container Toolkit:
```bash
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
# Sanity check
docker run --rm --gpus all nvidia/cuda:12.3.2-base-ubuntu22.04 nvidia-smi
```

## 2) Environment configuration

Use localhost for API calls from the agent running on DGX, and your DGX IP for returned links:
```bash
export PROM_URL=http://<DGX_IP>:9090
export GRAFANA_URL=http://localhost:3000
export PUBLIC_HOST=<DGX_IP>
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

## 3) Start (or heal) the monitoring stack

Starts dcgm-exporter, Prometheus, and Grafana; waits for readiness.
```bash
aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/dcgm_agent.yml --input "prom_stack_start"
```
Expect:
- dcgm-exporter: metrics=200
- Prometheus: ready=200
- Grafana: health=200, login=200

Force a fresh start (only once if needed):
```bash
aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/dcgm_agent.yml --input "prom_stack_start force=true"
```

## 4) Using the DCGM Expert tools

You can use explicit tool calls (most reliable) or NL one‑shot prompts.

### Explicit tool calls (recommended)

- Create a Grafana dashboard:
```bash
aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/dcgm_agent.yml \
  --input "grafana_create_dashboard name=GPU_Overview refresh=30s overwrite=false"
```

- Query Prometheus summaries (auto-fallback on metric names):
```bash
aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/dcgm_agent.yml --input "prom_query"
```

- Run a specific PromQL:
```bash
aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/dcgm_agent.yml \
  --input "prom_query query=max by (gpu) (DCGM_FI_DEV_GPU_TEMP)"
```

- Enable DCGM health and check status:
```bash
aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/dcgm_agent.yml --input "gpu_enable_health systems=a"
sleep 65
aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/dcgm_agent.yml --input "gpu_status"
```

### NL one‑shot prompts (be explicit)

If you want NL, make it a single, explicit one‑shot and include the tool with params as plain text (no markdown/backticks). Examples:
- grafana_create_dashboard name=GPU_Overview refresh=30s overwrite=false
- prom_query
- prom_query query=avg by (gpu) (avg_over_time(DCGM_FI_DEV_GPU_UTIL[5m]))
- gpu_status

Tips:
- Avoid multi‑step plans; call one tool per request.
- The agent accepts JSON or key=value, but plain key=value is most reliable.

## 5) Grafana access

If off‑node, use the returned SSH tunnel one‑liner to open locally, or browse:
- Prometheus: http://<DGX_IP>:9090
- Grafana: http://<DGX_IP>:3000

## 6) Troubleshooting quick checks

```bash
# Health codes
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:9400/metrics
curl -s -o /dev/null -w '%{http_code}\n' $PROM_URL/-/ready
curl -s -o /dev/null -w '%{http_code}\n' $GRAFANA_URL/api/health

# Container state and logs
docker ps --format 'table {{.Names}}\t{{.Status}}'
docker logs --tail=200 grafana

# Grafana with named volume example:
# docker run -d --restart unless-stopped --name grafana --net=host \
#   -e GF_SECURITY_ADMIN_PASSWORD="$GRAFANA_ADMIN_PASSWORD" \
#   -v grafana-data:/var/lib/grafana grafana/grafana-oss:latest
```

## 7) Files of interest
- Agent config: `examples/factory_reset/src/aiq_dgx_factory_reset/configs/dcgm_agent.yml`
- Tools: `examples/factory_reset/src/aiq_dgx_factory_reset/dcgm_register.py`
