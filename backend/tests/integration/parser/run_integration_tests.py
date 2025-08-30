#!/usr/bin/env python3
"""
Integration Test Runner for Parser Module

This script provides convenient ways to run integration tests with various options.

Usage:
    python run_integration_tests.py                    # Run all tests
    python run_integration_tests.py --category workflow # Run workflow tests
    python run_integration_tests.py --performance      # Run performance tests
    python run_integration_tests.py --load            # Run load tests
    python run_integration_tests.py --coverage        # Run with coverage
    python run_integration_tests.py --profile         # Run with profiling
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path

# Test categories and their corresponding files
TEST_CATEGORIES = {
    "workflow": "test_parser_workflow.py",
    "api": "test_parser_api.py",
    "performance": "test_parser_performance.py",
    "error_recovery": "test_parser_error_recovery.py",
    "load": "test_parser_load.py",
    "all": "*",  # All test files
}

def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd or Path(__file__).parent.parent.parent.parent,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def run_integration_tests(
    category="all",
    coverage=False,
    profile=False,
    verbose=False,
    fail_fast=False,
    benchmark=False
):
    """Run integration tests with specified options"""

    # Base command
    base_cmd = "cd /opt/app/backend && poetry run pytest"

    # Test path
    if category == "all":
        test_path = "tests/integration/parser/"
    else:
        test_file = TEST_CATEGORIES.get(category)
        if not test_file:
            print(f"Unknown category: {category}")
            print(f"Available categories: {', '.join(TEST_CATEGORIES.keys())}")
            return False
        test_path = f"tests/integration/parser/{test_file}"

    cmd_parts = [base_cmd, test_path]

    # Add options
    if verbose:
        cmd_parts.append("-v -s")
    else:
        cmd_parts.append("-v")

    if fail_fast:
        cmd_parts.append("--tb=short -x")

    if coverage:
        cmd_parts.extend([
            "--cov=src.parser",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])

    if benchmark:
        cmd_parts.append("--benchmark-enable")

    if profile:
        cmd_parts.append("--profile")

    # Execute command
    cmd = " ".join(cmd_parts)
    print(f"Running: {cmd}")
    print("-" * 50)

    success, stdout, stderr = run_command(cmd)

    if stdout:
        print(stdout)

    if stderr and not success:
        print("STDERR:", stderr)

    if success:
        print("-" * 50)
        print("✅ Integration tests completed successfully!")
    else:
        print("-" * 50)
        print("❌ Integration tests failed!")

    return success

def run_performance_analysis():
    """Run performance analysis on integration tests"""
    print("🚀 Running Performance Analysis...")
    print("-" * 50)

    # Run performance tests with benchmarking
    success = run_integration_tests(
        category="performance",
        benchmark=True,
        verbose=True
    )

    if success:
        print("📊 Performance analysis completed!")
        print("Check benchmark results above.")

    return success

def run_load_test():
    """Run load testing"""
    print("🔥 Running Load Tests...")
    print("-" * 50)

    success = run_integration_tests(
        category="load",
        verbose=True,
        fail_fast=False
    )

    if success:
        print("📈 Load testing completed!")
        print("Check load test results above.")

    return success

def run_full_suite():
    """Run the complete integration test suite"""
    print("🎯 Running Complete Integration Test Suite...")
    print("=" * 60)

    results = {}

    # Run each category
    for category in ["workflow", "api", "performance", "error_recovery", "load"]:
        print(f"\n📋 Running {category} tests...")
        success = run_integration_tests(category=category, verbose=False)
        results[category] = success

    # Summary
    print("\n" + "=" * 60)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 60)

    total_passed = 0
    total_categories = len(results)

    for category, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print("25")
        if success:
            total_passed += 1

    print("-" * 60)
    print("20")
    print(".1f"
    overall_success = total_passed == total_categories

    if overall_success:
        print("🎉 All integration tests passed!")
    else:
        print("⚠️  Some integration tests failed. Check output above.")

    return overall_success

def main():
    parser = argparse.ArgumentParser(
        description="Run Parser Integration Tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_integration_tests.py                    # Run all tests
  python run_integration_tests.py --category workflow # Run workflow tests
  python run_integration_tests.py --performance      # Run performance tests
  python run_integration_tests.py --load            # Run load tests
  python run_integration_tests.py --coverage        # Run with coverage
  python run_integration_tests.py --full-suite      # Run complete suite
        """
    )

    parser.add_argument(
        "--category",
        choices=list(TEST_CATEGORIES.keys()),
        default="all",
        help="Test category to run"
    )

    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage analysis"
    )

    parser.add_argument(
        "--profile",
        action="store_true",
        help="Run with performance profiling"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    parser.add_argument(
        "--fail-fast", "-x",
        action="store_true",
        help="Stop on first failure"
    )

    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Enable benchmarking"
    )

    parser.add_argument(
        "--performance",
        action="store_true",
        help="Run performance analysis"
    )

    parser.add_argument(
        "--load",
        action="store_true",
        help="Run load testing"
    )

    parser.add_argument(
        "--full-suite",
        action="store_true",
        help="Run complete integration test suite"
    )

    args = parser.parse_args()

    # Handle special modes
    if args.performance:
        success = run_performance_analysis()
    elif args.load:
        success = run_load_test()
    elif args.full_suite:
        success = run_full_suite()
    else:
        # Normal test run
        success = run_integration_tests(
            category=args.category,
            coverage=args.coverage,
            profile=args.profile,
            verbose=args.verbose,
            fail_fast=args.fail_fast,
            benchmark=args.benchmark
        )

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
