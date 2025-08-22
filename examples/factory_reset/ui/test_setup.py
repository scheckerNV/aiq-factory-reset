#!/usr/bin/env python3
"""
DCGM Agent Chat UI - Setup Test Script
This script verifies that the UI setup is correct and all components can be imported.
"""

import os
import sys
from pathlib import Path


def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing Python imports...")

    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False

    try:
        import uvicorn
        print("✅ Uvicorn imported successfully")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False

    try:
        import websockets
        print("✅ WebSockets imported successfully")
    except ImportError as e:
        print(f"❌ WebSockets import failed: {e}")
        return False

    try:
        import yaml
        print("✅ YAML imported successfully")
    except ImportError as e:
        print(f"❌ YAML import failed: {e}")
        return False

    return True


def test_aiq_imports():
    """Test that AIQ modules can be imported"""
    print("\n🧪 Testing AIQ imports...")

    # Add the source directory to Python path
    ui_dir = Path(__file__).parent
    src_dir = ui_dir.parent / "src"

    if src_dir.exists():
        sys.path.insert(0, str(src_dir))
        print(f"✅ Added {src_dir} to Python path")
    else:
        print(f"❌ Source directory not found: {src_dir}")
        return False

    try:
        from aiq.builder.builder import Builder
        print("✅ AIQ Builder imported successfully")
    except ImportError as e:
        print(f"❌ AIQ Builder import failed: {e}")
        return False

    try:
        from aiq.builder.function_info import FunctionInfo
        print("✅ AIQ FunctionInfo imported successfully")
    except ImportError as e:
        print(f"❌ AIQ FunctionInfo import failed: {e}")
        return False

    return True


def test_config_file():
    """Test that the DCGM agent configuration file exists"""
    print("\n🧪 Testing configuration file...")

    ui_dir = Path(__file__).parent
    config_path = ui_dir.parent / "src" / "aiq_dgx_factory_reset" / "configs" / "dcgm_agent.yml"

    if config_path.exists():
        print(f"✅ Configuration file found: {config_path}")

        try:
            import yaml
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            # Check for required sections
            required_sections = ['functions', 'workflow']
            for section in required_sections:
                if section in config:
                    print(f"✅ Configuration section '{section}' found")
                else:
                    print(f"❌ Configuration section '{section}' missing")
                    return False

            # Check for functions
            functions = config.get('functions', {})
            print(f"✅ Found {len(functions)} configured functions:")
            for func_name in functions:
                print(f"   - {func_name}")

            return True

        except Exception as e:
            print(f"❌ Failed to load configuration: {e}")
            return False
    else:
        print(f"❌ Configuration file not found: {config_path}")
        return False


def test_node_dependencies():
    """Test that Node.js and npm are available"""
    print("\n🧪 Testing Node.js dependencies...")

    try:
        import subprocess

        # Check Node.js
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js version: {result.stdout.strip()}")
        else:
            print("❌ Node.js not found")
            return False

        # Check npm
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm version: {result.stdout.strip()}")
        else:
            print("❌ npm not found")
            return False

        return True

    except FileNotFoundError:
        print("❌ Node.js or npm not found in PATH")
        return False


def main():
    """Main test function"""
    print("🚀 DCGM Agent Chat UI - Setup Test")
    print("=" * 50)

    tests = [
        ("Python Dependencies", test_imports),
        ("AIQ Dependencies", test_aiq_imports),
        ("Configuration File", test_config_file),
        ("Node.js Dependencies", test_node_dependencies),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        success = test_func()
        results.append((test_name, success))

    print("\n" + "=" * 50)
    print("📊 Test Results:")

    all_passed = True
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} {test_name}")
        if not success:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Your setup is ready.")
        print("Run './start_ui.sh' to start the UI.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("Refer to README.md for setup instructions.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
