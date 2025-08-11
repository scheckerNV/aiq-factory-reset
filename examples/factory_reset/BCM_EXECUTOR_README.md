# BCM Command Executor with Human Approval - POC

This implements a code execution tool for BCM commands with human-in-the-loop approval, designed to work with Qwen2.5 Coder 32B from NIM for intelligent command validation.

## Overview

The BCM Command Executor provides:
- **Human-in-the-loop approval** for all command execution
- **Qwen2.5 Coder validation** (when NIM is available)
- **Dry-run mode** for safe testing
- **Remote execution** via SSH to cluster nodes
- **Integration** with existing network assessment workflow

## Quick Start - Standalone Testing

### 1. Test the Standalone POC

```bash
cd examples/factory_reset
python3 bcm_command_executor_poc.py
```

This runs a simple test with sample BCM commands in dry-run mode.

### 2. Interactive Testing

```bash
cd examples/factory_reset
python3 test_bcm_executor.py
```

This provides an interactive test suite where you can:
- Test basic BCM commands
- Test network assessment commands
- Input your own custom commands

## AIQ Workflow Integration

### 1. Simple BCM Executor Only

Test just the executor without the full network agent:

```bash
aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/bcm_executor_poc.yml --input "cmsh -c 'device status'"
```

### 2. Full Network Agent with BCM Executor

Run the complete workflow (network assessment → BCM commands → execution):

```bash
aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/network_agent_with_bcm_executor.yml --input "Analyze cluster network state and generate corrective BCM commands"
```

## Configuration

### Key Configuration Options

Edit the YAML configs to customize:

```yaml
bcm_executor:
  cluster_host: "your-cluster-hostname"  # Your cluster hostname/IP
  cluster_user: "root"                   # SSH username
  timeout: 600                          # Command timeout in seconds
  dry_run: true                         # Set to false for live execution
  coder_llm_name: qwen_coder           # Qwen2.5 for validation
```

### Safety Settings

- **dry_run: true** - Commands are validated but NOT executed (recommended for testing)
- **dry_run: false** - Commands are actually executed on the cluster (use with caution)

## Workflow Integration

The tool integrates into your existing network agent workflow:

```
1. Network Assessment → 2. BCM Command Generation → 3. Human Approval → 4. Execution
```

### Step-by-Step Flow

1. **Network Assessment**: Existing `network_assessment_tool` gathers cluster state
2. **Command Generation**: Existing `bcm_documentation_rag` generates corrective commands
3. **Command Validation**: NEW `qwen_coder` validates commands for safety/correctness
4. **Human Approval**: NEW `hitl_code_approval` prompts user for approval
5. **Command Execution**: NEW `bcm_executor` executes approved commands

## Sample Commands for Testing

### Read-Only Commands (Safe)
```bash
cmsh -c "device status"
cmsh -c "device list -f hostname,ip,status"
cmsh -c "network list"
cmsh -c "device; connectivity"
```

### Configuration Commands (Use with Caution)
```bash
cmsh -c "device use NODE01; interfaces; add eth ethernet eth1"
cmsh -c "device use NODE01; interfaces use eth1; set network internal"
cmsh -c "device use NODE01; interfaces use eth1; commit"
```

## Safety Features

1. **Dry Run Default**: All configurations default to dry-run mode
2. **Human Approval**: Every command execution requires explicit human approval
3. **Command Validation**: Qwen2.5 Coder analyzes commands for safety issues
4. **Timeout Protection**: Commands timeout if they run too long
5. **Error Handling**: Comprehensive error reporting and rollback guidance

## Troubleshooting

### If NIM is Not Working
- The tool gracefully falls back without Qwen2.5 validation
- Human approval still works
- All safety features remain active

### If SSH Access Fails
- Check cluster_host and cluster_user settings
- Verify SSH key authentication is set up
- Test manual SSH connection first

### If Commands Fail
- Review error output in the execution results
- Check BCM syntax with `cmsh --help`
- Verify cluster state and permissions
- Consider running commands manually first

## Next Steps

1. **Test in Dry-Run Mode**: Validate your commands safely
2. **Review Generated Commands**: Ensure they match your intentions
3. **Enable Live Mode**: Set `dry_run: false` when ready
4. **Integrate with Network Agent**: Use the full workflow for automated factory reset

## Files Created

- `bcm_command_executor_poc.py` - Standalone POC script
- `test_bcm_executor.py` - Interactive test suite
- `configs/bcm_executor_poc.yml` - Simple executor config
- `configs/network_agent_with_bcm_executor.yml` - Full workflow config
- `code_execution_tool.py` - AIQ integration (already existed)

## Warning

⚠️ **IMPORTANT**: BCM commands can significantly modify your cluster configuration. Always:
- Test in dry-run mode first
- Review all commands carefully before approval
- Have a rollback plan ready
- Consider backing up your cluster configuration
