#!/usr/bin/env python
import subprocess
import sys
import os

# Change to the project directory
os.chdir("/Users/jabbo/SHIELD-backend")

# Activate venv and run tests
cmd = [
    ".venv/bin/python",
    "-m",
    "pytest",
    "tests/unit/api/test_vulnerability_api.py",
    "-v",
]
result = subprocess.run(cmd, capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\nReturn code: {result.returncode}")
