#!/usr/bin/env python3
"""
Test runner script for Settings module tests

This script provides convenient ways to run tests for the settings module
with different configurations and reporting options.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {cmd}")
        print(f"Return code: {e.returncode}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return e.stdout, e.stderr


def run_tests(args):
    """Run the tests with specified arguments"""
    base_cmd = "python -m pytest"

    # Add test paths
    test_paths = "tests/unit/settings/"

    # Build command with arguments
    cmd_parts = [base_cmd]

    if args.verbose:
        cmd_parts.append("-v")

    if args.quiet:
        cmd_parts.append("-q")

    if args.coverage:
        cmd_parts.extend(
            [
                "--cov=src.settings",
                "--cov-report=html:htmlcov",
                "--cov-report=term-missing",
                "--cov-fail-under=80",
            ]
        )

    if args.slow:
        cmd_parts.append("-m slow")
    else:
        cmd_parts.append("-m 'not slow'")

    if args.performance:
        cmd_parts.append("-m performance")

    if args.integration:
        cmd_parts.append("-m integration")

    if args.unit:
        # Run only unit tests (exclude integration and performance)
        cmd_parts.append("-m 'not integration and not performance'")

    if args.fail_fast:
        cmd_parts.append("--tb=short")

    if args.parallel:
        cmd_parts.extend(["-n", str(args.parallel)])

    # Add test paths
    cmd_parts.append(test_paths)

    # Add specific test files if provided
    if args.test_file:
        cmd_parts.append(args.test_file)

    # Add specific test functions if provided
    if args.test_function:
        cmd_parts.extend(["-k", args.test_function])

    cmd = " ".join(cmd_parts)
    print(f"Running command: {cmd}")

    stdout, stderr = run_command(cmd)

    if stdout:
        print("STDOUT:")
        print(stdout)

    if stderr:
        print("STDERR:")
        print(stderr)

    return stdout, stderr


def run_with_poetry(args):
    """Run tests using poetry"""
    poetry_cmd = "poetry run python -m pytest"

    # Add test paths
    test_paths = "tests/unit/settings/"

    # Build command with arguments
    cmd_parts = [poetry_cmd]

    if args.verbose:
        cmd_parts.append("-v")

    if args.coverage:
        cmd_parts.extend(
            [
                "--cov=src.settings",
                "--cov-report=html:htmlcov",
                "--cov-report=term-missing",
                "--cov-fail-under=80",
            ]
        )

    if args.slow:
        cmd_parts.append("-m slow")
    else:
        cmd_parts.append("-m 'not slow'")

    # Add test paths
    cmd_parts.append(test_paths)

    cmd = " ".join(cmd_parts)
    print(f"Running with Poetry: {cmd}")

    stdout, stderr = run_command(cmd)

    if stdout:
        print("STDOUT:")
        print(stdout)

    if stderr:
        print("STDERR:")
        print(stderr)

    return stdout, stderr


def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
        "pytest-xdist",
        "fastapi",
        "pydantic",
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall with: pip install " + " ".join(missing_packages))
        print(
            "Or with Poetry: poetry add --group dev "
            + " ".join(missing_packages)
        )
        return False

    print("All required packages are installed.")
    return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run Settings module tests")

    # Test selection options
    parser.add_argument(
        "--unit", action="store_true", help="Run only unit tests"
    )
    parser.add_argument(
        "--integration", action="store_true", help="Run only integration tests"
    )
    parser.add_argument(
        "--performance", action="store_true", help="Run only performance tests"
    )
    parser.add_argument(
        "--slow", action="store_true", help="Include slow tests"
    )

    # Output options
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose output"
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Quiet output"
    )
    parser.add_argument(
        "--fail-fast", action="store_true", help="Stop on first failure"
    )

    # Coverage options
    parser.add_argument(
        "--coverage", action="store_true", help="Generate coverage report"
    )

    # Parallel execution
    parser.add_argument(
        "-n", "--parallel", type=int, help="Number of parallel workers"
    )

    # Specific test selection
    parser.add_argument("--test-file", help="Run specific test file")
    parser.add_argument("--test-function", help="Run specific test function")

    # Poetry integration
    parser.add_argument(
        "--poetry", action="store_true", help="Run tests with Poetry"
    )

    # Utility options
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check if dependencies are installed",
    )
    parser.add_argument(
        "--clean", action="store_true", help="Clean test artifacts"
    )

    args = parser.parse_args()

    # Handle utility commands
    if args.check_deps:
        return 0 if check_dependencies() else 1

    if args.clean:
        import shutil
        import os

        # Clean coverage reports
        if os.path.exists("htmlcov"):
            shutil.rmtree("htmlcov")
            print("Removed htmlcov directory")

        if os.path.exists(".coverage"):
            os.remove(".coverage")
            print("Removed .coverage file")

        # Clean pytest cache
        if os.path.exists(".pytest_cache"):
            shutil.rmtree(".pytest_cache")
            print("Removed .pytest_cache directory")

        return 0

    # Check dependencies before running tests
    if not check_dependencies():
        print("Cannot run tests due to missing dependencies.")
        return 1

    # Run tests
    try:
        if args.poetry:
            stdout, stderr = run_with_poetry(args)
        else:
            stdout, stderr = run_tests(args)

        # Check for test failures in output
        if "FAILED" in stdout or "ERROR" in stdout:
            print("Some tests failed!")
            return 1
        elif "passed" in stdout:
            print("All tests passed!")
            return 0
        else:
            print("Test execution completed.")
            return 0

    except KeyboardInterrupt:
        print("\nTest execution interrupted by user.")
        return 130
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
