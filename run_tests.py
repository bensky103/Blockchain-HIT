#!/usr/bin/env python3
"""
Test runner script.
"""

import subprocess
import sys

def main():
    """Run the tests."""
    print("Running tests...")
    result = subprocess.run(["pytest", "-q"], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)
    
    if result.returncode == 0:
        print("All tests passed!")
        return 0
    else:
        print(f"Tests failed with return code {result.returncode}")
        return result.returncode

if __name__ == "__main__":
    sys.exit(main())
