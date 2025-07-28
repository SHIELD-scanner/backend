#!/usr/bin/env python3

import subprocess
import sys


def run_tests():
    """Run pytest and capture output."""
    try:
        # Run vulnerability client tests
        print("Running vulnerability client tests...")
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/unit/core/test_vulnerabilityClient.py",
                "-v",
            ],
            capture_output=True,
            text=True,
            cwd="/Users/jabbo/SHIELD-backend",
        )

        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)
        print(f"Return code: {result.returncode}")

        # Run user tests
        print("\nRunning user API tests...")
        result2 = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/unit/api/test_user.py::TestUserAPI::test_get_roles",
                "-v",
            ],
            capture_output=True,
            text=True,
            cwd="/Users/jabbo/SHIELD-backend",
        )

        print("STDOUT:")
        print(result2.stdout)
        print("STDERR:")
        print(result2.stderr)
        print(f"Return code: {result2.returncode}")

    except Exception as e:
        print(f"Error running tests: {e}")


if __name__ == "__main__":
    run_tests()
