# DGX Factory Reset Multi-Agent System

A comprehensive multi-agent system for DGX SuperPOD factory reset operations, featuring specialized agents for networking, DGX hardware management, and orchestrated workflows.

## Quick Start

### Local Development Setup

Run locally with virtual environment:
```bash
source .venv/bin/activate && uv pip install -e examples/factory_reset

aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/factory_reset_orchestrator.yml --input "What are the cmsh steps to add a node back to the BCM management network if I have its BMC IP and login?"
```

### Docker Deployment

cd examples/factory_reset
./scripts/deploy.sh --nvidia-key YOUR_NVIDIA_API_KEY

#### test api:
curl -X POST http://localhost:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{"input_message": "How do I add a node to BCM?"}'

#### View logs
docker compose logs -f factory-reset

#### Stop
docker compose down

#### Restart
docker compose restart

## Folders and Files
### pyproject.toml
package configurations

### config
contains configurations for each agent

#### BCM_expert.yml
contains functions, llms, and workflow of the BCM expert
meant to retrieve correct information from docs/bcm_admin_manual
