#!/usr/bin/env python3
"""Test runner script for SHIELD backend."""

import subprocess
import sys
import os


def run_tests():
    """Run all tests with coverage reporting."""
    print("🧪 Running SHIELD Backend Tests")
    print("=" * 50)
    
    # Set test environment
    os.environ["MONGODB_DB"] = "shield_test"
    os.environ["SENTRY_DSN"] = ""
    
    # Install test dependencies if not already installed
    print("📦 Installing test dependencies...")
    subprocess.run([
        sys.executable, "-m", "pip", "install", 
        "pytest", "pytest-asyncio", "httpx", "pytest-mock", "mongomock", "pytest-cov"
    ], check=False)
    
    # Run unit tests
    print("\n🔬 Running Unit Tests...")
    unit_result = subprocess.run([
        sys.executable, "-m", "pytest", "tests/unit/", 
        "-v", "--tb=short", "--cov=app", "--cov-report=term-missing"
    ], capture_output=False)
    
    # Run integration tests
    print("\n🔗 Running Integration Tests...")
    integration_result = subprocess.run([
        sys.executable, "-m", "pytest", "tests/integration/", 
        "-v", "--tb=short"
    ], capture_output=False)
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    
    if unit_result.returncode == 0:
        print("✅ Unit Tests: PASSED")
    else:
        print("❌ Unit Tests: FAILED")
    
    if integration_result.returncode == 0:
        print("✅ Integration Tests: PASSED")
    else:
        print("❌ Integration Tests: FAILED")
    
    # Overall result
    if unit_result.returncode == 0 and integration_result.returncode == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n💥 Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
