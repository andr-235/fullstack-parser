#!/usr/bin/env python3
"""
Test Runner for VK API Module

This script provides a convenient way to run the VK API test suite
with various options for coverage, parallel execution, and reporting.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --coverage         # Run with coverage report
    python run_tests.py --parallel         # Run in parallel
    python run_tests.py --verbose          # Verbose output
    python run_tests.py --fastapi          # Run only FastAPI related tests
    python run_tests.py --unit             # Run only unit tests
    python run_tests.py --integration      # Run only integration tests

Environment Variables:
    VK_API_ACCESS_TOKEN: VK API access token for integration tests
    TEST_DATABASE_URL: Database URL for repository tests
    PYTEST_XDIST_WORKER_COUNT: Number of parallel workers (default: auto)
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))


def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd or backend_dir,
            capture_output=False,
            text=True,
        )
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        return False
    except Exception as e:
        print(f"Error running command: {e}")
        return False


def get_test_command(args):
    """Build the pytest command based on arguments"""
    cmd_parts = ["python -m pytest"]

    # Test directory
    cmd_parts.append("tests/unit/vk_api/")

    # Coverage
    if args.coverage:
        cmd_parts.extend(
            [
                "--cov=src.vk_api",
                "--cov-report=html:tests/unit/vk_api/coverage_html",
                "--cov-report=term-missing",
                "--cov-fail-under=95",
            ]
        )

    # Parallel execution
    if args.parallel:
        worker_count = os.environ.get("PYTEST_XDIST_WORKER_COUNT", "auto")
        cmd_parts.append(f"-n {worker_count}")

    # Verbose output
    if args.verbose:
        cmd_parts.append("-v")
    elif not args.quiet:
        cmd_parts.append("-q")

    # Test type filtering
    if args.unit:
        cmd_parts.append("-m unit")
    elif args.integration:
        cmd_parts.append("-m integration")
    elif args.fastapi:
        cmd_parts.append("-k fastapi")
    elif args.performance:
        cmd_parts.append("-m performance")

    # Additional options
    if args.fail_fast:
        cmd_parts.append("--tb=short -x")

    if args.no_warnings:
        cmd_parts.append("--disable-warnings")

    return " ".join(cmd_parts)


def setup_environment():
    """Setup test environment variables"""
    # Set default test environment variables if not set
    env_vars = {
        "TESTING": "true",
        "PYTHONDONTWRITEBYTECODE": "1",
    }

    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value


def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        "pytest",
        "pytest-asyncio",
        "pytest-mock",
        "pytest-cov",
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing.append(package)

    if missing:
        print(f"Missing required packages: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
        return False

    return True


def main():
    parser = argparse.ArgumentParser(description="Run VK API tests")
    parser.add_argument(
        "--coverage", action="store_true", help="Generate coverage report"
    )
    parser.add_argument(
        "--parallel", action="store_true", help="Run tests in parallel"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Quiet output"
    )
    parser.add_argument(
        "--fail-fast", "-x", action="store_true", help="Stop on first failure"
    )
    parser.add_argument(
        "--no-warnings", action="store_true", help="Disable warnings"
    )

    # Test type filters
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument(
        "--unit", action="store_true", help="Run only unit tests"
    )
    test_group.add_argument(
        "--integration", action="store_true", help="Run only integration tests"
    )
    test_group.add_argument(
        "--fastapi", action="store_true", help="Run only FastAPI related tests"
    )
    test_group.add_argument(
        "--performance", action="store_true", help="Run only performance tests"
    )

    args = parser.parse_args()

    print("🚀 VK API Test Runner")
    print("=" * 50)

    # Setup
    setup_environment()

    if not check_dependencies():
        return 1

    # Build and run test command
    test_cmd = get_test_command(args)
    print(f"Running: {test_cmd}")
    print("-" * 50)

    success = run_command(test_cmd)

    if success:
        print("\n✅ All tests passed!")
        if args.coverage:
            print(
                "📊 Coverage report generated in: tests/unit/vk_api/coverage_html/"
            )
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
