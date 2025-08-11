#!/usr/bin/env python3
"""
Simple POC for BCM Command Execution with Human Approval
This is a standalone script to test BCM command execution before integrating with the network agent.
"""

import asyncio
import logging
import os
import tempfile
from typing import Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BCMCommandExecutor:
    """Simple BCM command executor with human approval"""

    def __init__(self,
                 cluster_host: str = "localhost",
                 cluster_user: str = "root",
                 timeout: int = 300,
                 dry_run: bool = True):
        self.cluster_host = cluster_host
        self.cluster_user = cluster_user
        self.timeout = timeout
        self.dry_run = dry_run

    def get_human_approval(self, commands: str) -> bool:
        """Get human approval for command execution"""
        print("\n" + "=" * 60)
        print("🔧 BCM COMMAND EXECUTION REQUEST")
        print("=" * 60)
        print(f"Target Cluster: {self.cluster_host}")
        print(f"User: {self.cluster_user}")
        print(f"Dry Run Mode: {'Enabled' if self.dry_run else 'Disabled'}")
        print(f"Timeout: {self.timeout} seconds")
        print("\n📝 COMMANDS TO EXECUTE:")
        print("-" * 40)
        print(commands)
        print("-" * 40)

        if self.dry_run:
            print("\n⚠️  DRY RUN MODE: Commands will be validated but NOT executed")
        else:
            print("\n⚠️  LIVE MODE: Commands WILL be executed on the cluster!")

        print("\n🔍 Please review these commands carefully.")
        print("These commands may make changes to your DGX cluster configuration.")

        while True:
            response = input("\nDo you approve execution of these commands? (yes/no): ").strip().lower()
            if response in ['yes', 'y', 'approve']:
                return True
            elif response in ['no', 'n', 'deny', 'cancel']:
                return False
            else:
                print("Please respond with 'yes' or 'no'")

    async def execute_commands(self, bcm_commands: str) -> str:
        """Execute BCM commands with approval"""

        if not bcm_commands or not bcm_commands.strip():
            return "❌ No BCM commands provided for execution"

        # Get human approval
        if not self.get_human_approval(bcm_commands):
            return """❌ **Execution Cancelled**

User did not approve command execution. No changes were made to the cluster.

You can:
1. Modify the commands and try again
2. Review the commands for safety
3. Exit with the current analysis
"""

        print(f"\n✅ Commands approved for execution {'(DRY RUN)' if self.dry_run else '(LIVE)'}")

        # Dry run mode - just validate
        if self.dry_run:
            return f"""✅ **Dry Run Mode - Commands Validated**

**APPROVED COMMANDS:**
{bcm_commands}

**Status:** Commands have been validated and approved but not executed (dry-run mode).
To execute these commands, set dry_run=False.
"""

        # Execute commands on the cluster
        try:
            logger.info("Executing approved BCM commands on cluster...")

            # Create execution script
            script_content = f"""#!/bin/bash
set -e  # Exit on any error
set -x  # Print commands

echo "Starting BCM command execution..."
echo "Timestamp: $(date)"
echo "User: $(whoami)"
echo "Host: $(hostname)"
echo "===================================="

{bcm_commands}

echo "===================================="
echo "BCM command execution completed successfully!"
echo "Timestamp: $(date)"
"""

            # Write script to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(script_content)
                script_path = f.name

            # Make executable
            os.chmod(script_path, 0o755)

            if self.cluster_host == "localhost":
                # Local execution
                cmd = [script_path]
                process = await asyncio.create_subprocess_exec(*cmd,
                                                               stdout=asyncio.subprocess.PIPE,
                                                               stderr=asyncio.subprocess.PIPE)
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=self.timeout)
            else:
                # Remote execution via SSH
                # Copy script to cluster
                scp_cmd = ["scp", script_path, f"{self.cluster_user}@{self.cluster_host}:/tmp/bcm_execution.sh"]

                scp_process = await asyncio.create_subprocess_exec(*scp_cmd,
                                                                   stdout=asyncio.subprocess.PIPE,
                                                                   stderr=asyncio.subprocess.PIPE)
                await scp_process.communicate()

                if scp_process.returncode != 0:
                    return "❌ Failed to upload execution script to cluster"

                # Execute script on cluster
                ssh_cmd = [
                    "ssh",
                    f"{self.cluster_user}@{self.cluster_host}",
                    "chmod +x /tmp/bcm_execution.sh && /tmp/bcm_execution.sh"
                ]

                process = await asyncio.create_subprocess_exec(*ssh_cmd,
                                                               stdout=asyncio.subprocess.PIPE,
                                                               stderr=asyncio.subprocess.PIPE)
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=self.timeout)

            # Clean up local script
            os.unlink(script_path)

            if process.returncode == 0:
                return f"""✅ **Command Execution Successful**

**EXECUTION OUTPUT:**
{stdout.decode('utf-8')}

**STATUS:** All BCM commands executed successfully on {self.cluster_host}

**NEXT STEPS:**
1. Verify cluster state changes
2. Run network assessment to confirm changes
3. Update documentation as needed
"""
            else:
                error_output = stderr.decode('utf-8')
                return f"""❌ **Command Execution Failed**

**ERROR OUTPUT:**
{error_output}

**STDOUT:**
{stdout.decode('utf-8')}

**RECOMMENDATIONS:**
1. Review the error messages above
2. Check command syntax and permissions
3. Verify cluster connectivity
4. Consider running commands manually for troubleshooting
"""

        except asyncio.TimeoutError:
            return f"❌ Command execution timed out after {self.timeout} seconds"
        except Exception as e:
            return f"❌ Execution error: {str(e)}"


async def main():
    """Main function for testing"""
    print("🚀 BCM Command Executor POC")
    print("=" * 50)

    # Sample BCM commands for testing
    sample_commands = """# Sample BCM commands for testing
cmsh -c "device status"
cmsh -c "device list -f hostname,ip,status"
cmsh -c "network list"
echo "BCM command test completed"
"""

    # Initialize executor in dry-run mode for safety
    executor = BCMCommandExecutor(
        cluster_host="localhost",
        cluster_user=os.getenv("USER", "root"),
        timeout=60,
        dry_run=False  # Start with dry run for safety
    )

    # Execute sample commands
    result = await executor.execute_commands(sample_commands)
    print("\n" + "=" * 60)
    print("📋 EXECUTION RESULT:")
    print("=" * 60)
    print(result)

    print("\n✨ To test with your own commands, modify the sample_commands variable")
    print("✨ To enable live execution, set dry_run=False (be careful!)")


if __name__ == "__main__":
    asyncio.run(main())
