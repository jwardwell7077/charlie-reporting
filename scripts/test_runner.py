#!/usr/bin/env python3
"""
Service-Based Test Runner
Runs tests across all services with proper organization
"""
import subprocess
import sys
from pathlib import Path
import argparse

def run_service_tests(service_name=None, test_type=None, verbose=False):
    """Run tests for a specific service or all services."""
    
    base_cmd = ["python3", "-m", "pytest"]
    
    if verbose:
        base_cmd.extend(["-v", "--tb=long"])
    
    services_dir = Path("services")
    
    if service_name:
        # Run tests for specific service
        service_path = services_dir / service_name / "tests"
        if not service_path.exists():
            print(f"❌ No tests found for service: {service_name}")
            return 1
        
        cmd = base_cmd + [str(service_path)]
        if test_type:
            cmd.extend(["-m", test_type])
        
        print(f"🧪 Running tests for {service_name} service...")
        return subprocess.run(cmd).returncode
    
    else:
        # Run tests for all services
        exit_codes = []
        
        # Get all services with tests
        services_with_tests = []
        for service_dir in services_dir.iterdir():
            if service_dir.is_dir() and (service_dir / "tests").exists():
                services_with_tests.append(service_dir.name)
        
        if not services_with_tests:
            print("❌ No services with tests found")
            return 1
        
        print(f"🧪 Running tests for {len(services_with_tests)} services...")
        
        for service in services_with_tests:
            print(f"\n🔍 Testing {service}...")
            cmd = base_cmd + [str(services_dir / service / "tests")]
            if test_type:
                cmd.extend(["-m", test_type])
            
            result = subprocess.run(cmd)
            exit_codes.append(result.returncode)
            
            if result.returncode == 0:
                print(f"✅ {service} tests passed")
            else:
                print(f"❌ {service} tests failed")
        
        # Also run shared tests
        shared_tests = Path("shared/tests")
        if shared_tests.exists():
            print(f"\n🔍 Testing shared utilities...")
            cmd = base_cmd + [str(shared_tests)]
            if test_type:
                cmd.extend(["-m", test_type])
            
            result = subprocess.run(cmd)
            exit_codes.append(result.returncode)
            
            if result.returncode == 0:
                print(f"✅ Shared tests passed")
            else:
                print(f"❌ Shared tests failed")
        
        # Return overall result
        if all(code == 0 for code in exit_codes):
            print(f"\n🎉 All tests passed!")
            return 0
        else:
            failed_count = sum(1 for code in exit_codes if code != 0)
            print(f"\n💥 {failed_count} test suite(s) failed")
            return 1

def list_services():
    """List all services with tests."""
    services_dir = Path("services")
    services_with_tests = []
    
    for service_dir in services_dir.iterdir():
        if service_dir.is_dir() and (service_dir / "tests").exists():
            test_count = len(list((service_dir / "tests").glob("**/test_*.py")))
            services_with_tests.append((service_dir.name, test_count))
    
    if services_with_tests:
        print("📋 Services with tests:")
        for service, count in services_with_tests:
            print(f"  - {service}: {count} test files")
    else:
        print("❌ No services with tests found")
    
    # Also check shared tests
    shared_tests = Path("shared/tests")
    if shared_tests.exists():
        shared_count = len(list(shared_tests.glob("**/test_*.py")))
        print(f"  - shared: {shared_count} test files")

def run_coverage_report():
    """Generate coverage report for all services."""
    cmd = [
        "python3", "-m", "pytest", 
        "--cov=services", 
        "--cov=shared",
        "--cov-report=html:coverage_html",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "services/*/tests",
        "shared/tests"
    ]
    
    print("📊 Generating coverage report...")
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("✅ Coverage report generated in coverage_html/")
    else:
        print("❌ Coverage report generation failed")
    
    return result.returncode

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Service-based test runner")
    
    parser.add_argument(
        "--service", "-s",
        help="Run tests for specific service",
        choices=["report_generator", "email-service", "outlook-relay", "database-service", "scheduler-service"]
    )
    
    parser.add_argument(
        "--type", "-t",
        help="Run specific type of tests",
        choices=["unit", "integration", "api", "performance", "legacy"]
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all services with tests"
    )
    
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_services()
        return 0
    
    if args.coverage:
        return run_coverage_report()
    
    return run_service_tests(
        service_name=args.service,
        test_type=args.type,
        verbose=args.verbose
    )

if __name__ == "__main__":
    exit(main())
