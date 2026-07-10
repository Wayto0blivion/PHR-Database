#!/usr/bin/env python
"""
Test runner script for PHR Flask application.
This script runs all tests and provides a summary of results.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py -v           # Run with verbose output
    python run_tests.py -k test_name # Run specific test
"""
import sys
import subprocess


def main():
    """Run pytest with the provided arguments."""
    # Build pytest command
    cmd = [sys.executable, '-m', 'pytest', 'tests/']

    # Add any command-line arguments passed to this script
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])
    else:
        # Default arguments for standard test run
        cmd.extend(['-v', '--tb=short'])

    print("=" * 70)
    print("PHR Flask Application Test Suite")
    print("=" * 70)
    print(f"Running: {' '.join(cmd)}")
    print("=" * 70)
    print()

    # Run pytest
    result = subprocess.run(cmd)

    print()
    print("=" * 70)
    if result.returncode == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed. Please review the output above.")
    print("=" * 70)

    return result.returncode


if __name__ == '__main__':
    sys.exit(main())
