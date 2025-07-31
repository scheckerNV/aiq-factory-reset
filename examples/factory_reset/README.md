## Quick start

run:
source .venv/bin/activate && uv pip install -e examples/factory_reset

aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/bcm_expert.yml --input "What are the cmsh steps to add a node back to the BCM management network if I have its BMC IP and login?"

## Folders and Files
### pyproject.toml
package configurations

### config
contains configurations for each agent

#### BCM_expert.yml
contains functions, llms, and workflow of the BCM expert
meant to retrieve correct information from docs/bcm_admin_manual
