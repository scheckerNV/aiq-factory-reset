#!/usr/bin/env python3
"""
Test script for BCM Command Executor POC
This demonstrates how to use the BCM command executor with sample commands.
"""

import asyncio
import os
import sys

# Add the project to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bcm_command_executor_poc import BCMCommandExecutor


async def test_basic_commands():
    """Test basic BCM commands"""
    print("🧪 Testing Basic BCM Commands")
    print("=" * 50)

    # Sample commands that are safe to run
    basic_commands = """# Basic cluster information commands (read-only)
echo "=== BCM Cluster Status Check ==="
cmsh -c "device status" || echo "device status failed"
cmsh -c "device list -f hostname,ip,status" || echo "device list failed"
cmsh -c "network list" || echo "network list failed"
echo "=== BCM Basic Check Complete ==="
"""

    executor = BCMCommandExecutor(
        cluster_host="localhost",
        cluster_user=os.getenv("USER", "root"),
        timeout=60,
        dry_run=True  # Safe mode
    )

    result = await executor.execute_commands(basic_commands)
    print(result)


async def test_network_assessment_commands():
    """Test network assessment style commands"""
    print("\n🌐 Testing Network Assessment Commands")
    print("=" * 50)

    # Commands similar to what the network agent generates
    network_commands = """# Network assessment commands (read-only)
echo "=== Network State Assessment ==="
cmsh -c "device; connectivity" || echo "connectivity check failed"
cmsh -c "device; routes" || echo "routes check failed"
cmsh -c "device; interfaces; list" || echo "interfaces list failed"
cmsh -c "network list" || echo "network list failed"
echo "=== Network Assessment Complete ==="
"""

    executor = BCMCommandExecutor(
        cluster_host="localhost",
        cluster_user=os.getenv("USER", "root"),
        timeout=90,
        dry_run=True  # Safe mode
    )

    result = await executor.execute_commands(network_commands)
    print(result)


async def test_custom_commands():
    """Test with custom user-provided commands"""
    print("\n✏️  Testing Custom Commands")
    print("=" * 50)

    print("Enter your BCM commands (end with Ctrl+D or empty line on some systems):")
    print("Example: cmsh -c \"device status\"")
    print("-" * 40)

    lines = []
    try:
        while True:
            line = input()
            if not line.strip():  # Empty line ends input on some systems
                break
            lines.append(line)
    except EOFError:
        pass  # Ctrl+D pressed

    if not lines:
        print("No commands entered, skipping custom test.")
        return

    custom_commands = "\n".join(lines)

    executor = BCMCommandExecutor(
        cluster_host="localhost",
        cluster_user=os.getenv("USER", "root"),
        timeout=120,
        dry_run=True  # Safe mode - change to False for live execution
    )

    result = await executor.execute_commands(custom_commands)
    print(result)


async def main():
    """Main test function"""
    print("🚀 BCM Command Executor Test Suite")
    print("=" * 60)
    print("This test demonstrates BCM command execution with human approval.")
    print("All tests run in DRY RUN mode by default for safety.")
    print("=" * 60)

    # Test 1: Basic commands
    await test_basic_commands()

    # Test 2: Network assessment commands
    await test_network_assessment_commands()

    # Test 3: Custom commands (interactive)
    try:
        await test_custom_commands()
    except KeyboardInterrupt:
        print("\n\nCustom command test skipped.")

    print("\n" + "=" * 60)
    print("✅ Test Suite Complete!")
    print("=" * 60)
    print("\n📝 Next Steps:")
    print("1. Review the execution results above")
    print("2. To enable live execution, set dry_run=False in the executor")
    print("3. Integrate with the network agent workflow when ready")
    print("4. Test with real BCM commands from your network assessment")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted by user. Goodbye!")
        sys.exit(0)
