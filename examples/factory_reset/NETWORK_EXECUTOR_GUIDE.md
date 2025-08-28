# Network Agent with Automatic BCM Command Execution

This guide shows how to use the enhanced network agent that automatically executes BCM commands after generating them.

## Workflow Overview

```
Input Request → Network Assessment → BCM Command Generation → Human Approval → Command Execution → Results
```

## Quick Start

### Option 1: Enhanced Network Agent (Recommended)
This extends your existing workflow with execution capabilities:

```bash
aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/network_agent_with_executor.yml --input "Correct cmsh bcm commands to comprehensively revert schecker-testcluster cluster's network state to known state"
```

### Option 2: Streamlined Auto-Execute Workflow
This is a focused workflow that prioritizes execution:

```bash
aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/network_agent_auto_execute.yml --input "Execute complete network factory reset on schecker-testcluster"
```

## What Happens Automatically

1. **Network Assessment**: The agent runs your existing network assessment tools
2. **Analysis**: Reviews current state vs desired state using documentation
3. **Command Generation**: BCM expert generates appropriate `cmsh` commands
4. **Validation**: Qwen2.5 Coder validates commands for safety and correctness
5. **Human Approval**: You review and approve the commands before execution
6. **Execution**: Approved commands are executed on schecker-testcluster
7. **Results**: Detailed execution results and next steps are provided

## Key Differences from Original Workflow

### Before (network_agent.yml):
- ✅ Network assessment
- ✅ BCM command generation
- ❌ Manual copy/paste of commands
- ❌ Manual execution

### After (network_agent_with_executor.yml):
- ✅ Network assessment
- ✅ BCM command generation
- ✅ Automatic command validation
- ✅ Human-approved execution
- ✅ Execution results and verification

## Configuration Details

Both configurations use:
- **cluster_host**: `schecker-testcluster` (your test cluster)
- **cluster_user**: `root`
- **dry_run**: `false` (live execution enabled since POC worked)
- **timeout**: `600` seconds (longer for network operations)

## Sample Inputs

### Complete Factory Reset
```bash
--input "Execute complete network factory reset to restore schecker-testcluster to known good state"
```

### Specific Network Issues
```bash
--input "Fix network connectivity issues on schecker-testcluster nodes"
```

### Interface Configuration
```bash
--input "Reset and reconfigure network interfaces on schecker-testcluster according to documentation"
```

## Safety Features

1. **Command Validation**: Qwen2.5 Coder analyzes commands before execution
2. **Human Approval**: Every execution requires your explicit approval
3. **Comprehensive Logging**: All operations are logged with timestamps
4. **Error Handling**: Detailed error reporting and rollback guidance
5. **Timeout Protection**: Commands timeout if they run too long

## Expected Flow

1. **You run the command**
2. **Agent assesses network** (existing tools)
3. **Agent generates BCM commands** (existing tools)
4. **Qwen2.5 validates commands** (new)
5. **System prompts you for approval** (new)
   ```
   NETWORK FACTORY RESET COMMANDS
   Target Cluster: schecker-testcluster

   The following commands will be executed:
   cmsh -c "device use node01; interfaces; reset"
   cmsh -c "device use node01; interfaces; commit"
   ...

   Do you approve execution? (yes/no):
   ```
6. **Commands execute if approved** (new)
7. **Results displayed** (new)

## Troubleshooting

### If NIM/Qwen2.5 is Down
- Command validation will be skipped gracefully
- Human approval still required
- All other safety features remain active

### If SSH Access Fails
- Check that `cluster_user: root` is correct for your setup
- Verify SSH key authentication is configured
- Test manual SSH: `ssh root@schecker-testcluster`

### If Commands Fail
- Review the detailed error output
- Check the execution logs
- Consider running commands manually for debugging
- Adjust commands based on error messages

## Files Overview

- `network_agent_with_executor.yml` - Enhanced version of your existing workflow
- `network_agent_auto_execute.yml` - Streamlined execution-focused workflow
- `bcm_executor_poc.yml` - Simple executor testing (from earlier)

Choose the configuration that best fits your needs!
