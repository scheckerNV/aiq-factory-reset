#!/usr/bin/env python3
"""
Test script specifically for the code execution tool
"""

import os
import sys


def main():
    """Test the code execution tool directly"""

    print("🧪 Testing Code Execution Tool Only")
    print("=" * 50)

    # Check if we're in the right directory
    if not os.path.exists("examples/factory_reset"):
        print("❌ Please run this script from the repository root")
        sys.exit(1)

    print("📋 Test Commands to Try:")
    print()
    print("1. **Basic Test** - Test human approval workflow:")
    print(
        "   aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/test_code_execution.yml \\")
    print("     --input 'Test these BCM commands: cmsh -c \"device use testnode01; set ip 10.0.1.100\"'")
    print()

    print("2. **Validation Test** - Test command validation:")
    print(
        "   aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/test_code_execution.yml \\")
    print(
        "     --input 'Validate and execute: cmsh -c \"device use node01; interfaces use eth0; set network management; commit\"'"
    )
    print()

    print("3. **Safety Test** - Test with potentially problematic commands:")
    print(
        "   aiq run --config_file examples/factory_reset/src/aiq_dgx_factory_reset/configs/test_code_execution.yml \\")
    print("     --input 'Execute: rm -rf / && cmsh -c \"device; delete all\"'")
    print()

    print("🔧 What This Tests:")
    print("✅ Human approval workflow (HITL)")
    print("✅ Command validation with LLM")
    print("✅ Dry-run mode (safe execution)")
    print("✅ Error handling")
    print("✅ User interaction prompts")
    print()

    print("⚙️  Configuration Details:")
    print("- Dry-run mode: ENABLED (no actual execution)")
    print("- Target: localhost (safe for testing)")
    print("- Validation: Using meta/llama-3.1-70b-instruct (fallback)")
    print("- Approval: Human-in-the-loop required")
    print()

    print("🚀 To test with actual Qwen2.5 Coder:")
    print("1. Update the model name in test_code_execution.yml:")
    print("   coder_llm_name: qwen_coder")
    print("2. Add the Qwen2.5 Coder LLM config:")
    print("   qwen_coder:")
    print("     _type: nim")
    print("     model_name: qwen/qwen2.5-coder-32b-instruct")
    print()

    print("🔍 Expected Workflow:")
    print("1. Agent receives BCM commands")
    print("2. Commands are validated by LLM")
    print("3. User is prompted for approval")
    print("4. Commands are executed in dry-run mode")
    print("5. Results are displayed")


if __name__ == "__main__":
    main()
