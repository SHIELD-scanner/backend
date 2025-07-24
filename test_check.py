#!/usr/bin/env python3
"""Simple test to check if our fixes work."""

import subprocess
import sys


def run_test(test_path):
    """Run a specific test and return the result."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            cwd="/Users/jabbo/SHIELD-backend",
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def main():
    """Run tests on the files we've fixed."""
    test_files = [
        "tests/unit/api/test_vulnerability_api.py",
        "tests/unit/api/test_vulnerability.py",
        "tests/unit/api/test_exposedsecret_api.py",
        "tests/unit/api/test_sbom_api.py",
        "tests/unit/api/test_application.py",
        "tests/unit/api/test_pod_api.py",
        "tests/unit/api/test_namespace_api.py",
    ]

    results = {}

    for test_file in test_files:
        print(f"Testing {test_file}...")
        success, stdout, stderr = run_test(test_file)
        results[test_file] = success

        if success:
            print(f"✅ {test_file} - PASSED")
        else:
            print(f"❌ {test_file} - FAILED")
            print(f"Error: {stderr}")

    print("\n=== SUMMARY ===")
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    print(f"Passed: {passed}/{total} test files")

    for test_file, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {test_file}")


if __name__ == "__main__":
    main()
