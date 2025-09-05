#!/usr/bin/env python3
# # Copyright (c) 2025 Aaron Sachs
# # Licensed under the MIT License.
# # See LICENSE file in the project root for full license information.

"""
Test script to verify that examples in documentation work correctly.
This script tests the basic import and initialization patterns shown in the docs.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_basic_imports():
    """Test that all documented imports work correctly."""
    print("🧪 Testing basic imports...")

    try:
        import py_superops

        print(f"✅ py_superops imported successfully (version: {py_superops.__version__})")
    except ImportError as e:
        print(f"❌ Failed to import py_superops: {e}")
        return False

    try:
        from py_superops import SuperOpsClient, SuperOpsConfig

        print("✅ Core classes imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import core classes: {e}")
        return False

    try:
        from py_superops import (
            SuperOpsAPIError,
            SuperOpsAuthenticationError,
            SuperOpsError,
            SuperOpsNetworkError,
            SuperOpsRateLimitError,
        )

        print("✅ Exception classes imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import exception classes: {e}")
        return False

    return True


def test_config_creation():
    """Test configuration creation as shown in documentation."""
    print("\n🧪 Testing configuration creation...")

    try:
        from py_superops import SuperOpsConfig

        # Test basic config
        config = SuperOpsConfig(
            api_key="sk_test_1234567890abcdef1234567890abcdef12345678",  # pragma: allowlist secret
            base_url="https://api.superops.com/v1",
        )
        print("✅ Basic configuration created successfully")

        # Test detailed config
        config = SuperOpsConfig(
            api_key="sk_test_1234567890abcdef1234567890abcdef12345678",  # pragma: allowlist secret
            base_url="https://api.superops.com/v1",
            timeout=30.0,
            max_retries=3,
            rate_limit_per_minute=60,
            enable_caching=True,
            cache_ttl=300,
            debug=False,
        )
        print("✅ Detailed configuration created successfully")

        return True
    except Exception as e:
        print(f"❌ Failed to create configuration: {e}")
        return False


def test_client_creation():
    """Test client creation as shown in documentation."""
    print("\n🧪 Testing client creation...")

    try:
        from py_superops import SuperOpsClient, SuperOpsConfig

        config = SuperOpsConfig(
            api_key="sk_test_1234567890abcdef1234567890abcdef12345678",  # pragma: allowlist secret
            base_url="https://api.superops.com/v1",
        )

        client = SuperOpsClient(config)
        print("✅ Client created successfully")

        # Test manager access
        managers_to_test = [
            "clients",
            "tickets",
            "tasks",
            "assets",
            "projects",
            "contacts",
            "sites",
            "users",
            "knowledge_base",
            "contracts",
            "time_entries",
            "attachments",
            "comments",
            "webhooks",
        ]

        for manager_name in managers_to_test:
            if hasattr(client, manager_name):
                manager = getattr(client, manager_name)
                print(f"✅ {manager_name} manager accessible: {type(manager).__name__}")
            else:
                print(f"⚠️  {manager_name} manager not found")

        return True
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return False


def test_package_info():
    """Test package info functions as shown in documentation."""
    print("\n🧪 Testing package info functions...")

    try:
        import py_superops

        version = py_superops.get_version()
        print(f"✅ Version: {version}")

        package_info = py_superops.get_package_info()
        print(f"✅ Package info retrieved: {len(package_info)} items")
        print(f"   Features: {len(package_info.get('features', []))} listed")

        return True
    except Exception as e:
        print(f"❌ Failed to get package info: {e}")
        return False


def test_convenience_functions():
    """Test convenience functions."""
    print("\n🧪 Testing convenience functions...")

    try:
        from py_superops import create_client

        # Test create_client (won't actually connect without real API key)
        client = create_client(
            api_key="sk_test_1234567890abcdef1234567890abcdef12345678"
        )  # pragma: allowlist secret
        print("✅ create_client function works")

        return True
    except Exception as e:
        print(f"❌ Failed to use convenience functions: {e}")
        return False


def main():
    """Run all documentation tests."""
    print("🚀 Testing py-superops documentation examples...\n")

    tests = [
        test_basic_imports,
        test_config_creation,
        test_client_creation,
        test_package_info,
        test_convenience_functions,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")

    print(f"\n📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All documentation examples work correctly!")
        return 0
    else:
        print("⚠️  Some documentation examples have issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())
