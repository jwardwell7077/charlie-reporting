#!/usr / bin / env python3
"""Phase 2 Validation Script
Comprehensive validation of Phase 2 implementation requirements

This script validates all Phase 2 deliverables:
- Testing framework configuration
- Test coverage requirements
- API implementation status
- Integration testing framework
- Performance benchmarks
- Documentation completeness
"""

import json
import os
import subprocess
import sys
from pathlib import Path


class Phase2Validator:
    """Comprehensive Phase 2 implementation validator"""

    def __init__(self, workspace_root: str = None):
        self.workspaceroot = Path(workspace_root or os.getcwd())
        self.results = []
        self.errors = []

    def validate_all(self) -> dict[str, Any]:
        """Run all Phase 2 validation checks"""
        print("🎯 Phase 2 Implementation Validation")
        print("=" * 50)

        validationresults = {
            "testing_framework": self.validate_testing_framework(),
            "test_coverage": self.validate_test_coverage(),
            "api_implementation": self.validate_api_implementation(),
            "integration_tests": self.validate_integration_tests(),
            "performance_benchmarks": self.validate_performance_benchmarks(),
            "documentation": self.validate_documentation(),
            "vscode_integration": self.validate_vscode_integration()
        }

        # Calculate overall score
        totalchecks = sum(len(checks) for checks in validation_results.values())
        passedchecks = sum(
            sum(1 for check in checks if check["status"] == "✅")
            for checks in validation_results.values()
        )

        overallscore = (passed_checks / total_checks) * 100 if total_checks > 0 else 0

        print("\n🎊 Phase 2 Validation Complete")
        print(f"📊 Overall Score: {overall_score:.1f}% ({passed_checks}/{total_checks} checks passed)")

        if overall_score >= 85:
            print("✅ Phase 2 implementation meets requirements!")
        else:
            print("⚠️ Phase 2 implementation needs improvement")

        return {
            "score": overall_score,
            "passed": passed_checks,
            "total": total_checks,
            "results": validation_results
        }

    def validate_testing_framework(self) -> list[dict[str, str]]:
        """Validate testing framework configuration"""
        print("\n🧪 Testing Framework Configuration")
        checks = []

        # Check pytest.ini
        pytestini = self.workspace_root / "pytest.ini"
        checks.append({
            "name": "pytest.ini configuration",
            "status": "✅" if pytest_ini.exists() else "❌",
            "details": f"Found at {pytest_ini}" if pytest_ini.exists() else "Missing pytest.ini"
        })

        # Check conftest.py
        conftest = self.workspace_root / "tests" / "conftest.py"
        checks.append({
            "name": "conftest.py with shared fixtures",
            "status": "✅" if conftest.exists() else "❌",
            "details": f"Found at {conftest}" if conftest.exists() else "Missing conftest.py"
        })

        # Check test directory structure
        testservices_dir = self.workspace_root / "tests" / "services"
        checks.append({
            "name": "Service - specific test directory",
            "status": "✅" if test_services_dir.exists() else "❌",
            "details": f"Found at {test_services_dir}" if test_services_dir.exists() else "Missing tests / services/"
        })

        # Check integration test directory
        integrationdir = self.workspace_root / "tests" / "integration"
        checks.append({
            "name": "Integration test directory",
            "status": "✅" if integration_dir.exists() else "❌",
            "details": f"Found at {integration_dir}" if integration_dir.exists() else "Missing tests / integration/"
        })

        for check in checks:
            print(f"  {check['status']} {check['name']}: {check['details']}")

        return checks

    def validate_test_coverage(self) -> list[dict[str, str]]:
        """Validate test coverage requirements"""
        print("\n📊 Test Coverage Analysis")
        checks = []

        try:
            # Run coverage analysis
            result = subprocess.run([
                sys.executable, "-m", "pytest",
                "--cov=services",
                "--cov - report=term - missing",
                "--tb=no", "-q"
            ], check=False, capture_output=True, text=True, cwd=self.workspace_root)

            if result.returncode == 0:
                coverageoutput = result.stdout
                # Parse coverage percentage (simplified)
                if "TOTAL" in coverage_output:
                    lines = coverage_output.split('\n')
                    totalline = [line for line in lines if "TOTAL" in line]
                    if total_line:
                        # Extract percentage (this is a simplified parser)
                        try:
                            percentage = float(total_line[0].split()[-1].rstrip('%'))
                            status = "✅" if percentage >= 85 else "⚠️"
                            checks.append({
                                "name": f"Test coverage {percentage}%",
                                "status": status,
                                "details": f"Target: 85%, Actual: {percentage}%"
                            })
                        except (ValueError, IndexError):
                            checks.append({
                                "name": "Test coverage parsing",
                                "status": "❌",
                                "details": "Could not parse coverage percentage"
                            })
                else:
                    checks.append({
                        "name": "Test coverage",
                        "status": "⚠️",
                        "details": "Coverage report generated but no TOTAL line found"
                    })
            else:
                checks.append({
                    "name": "Test coverage",
                    "status": "❌",
                    "details": f"Coverage test failed: {result.stderr}"
                })

        except Exception as e:
            checks.append({
                "name": "Test coverage",
                "status": "❌",
                "details": f"Coverage analysis failed: {str(e)}"
            })

        # Check for HTML coverage report
        htmlcovdir = self.workspace_root / "htmlcov"
        checks.append({
            "name": "HTML coverage report",
            "status": "✅" if htmlcov_dir.exists() else "❌",
            "details": f"Found at {htmlcov_dir}" if htmlcov_dir.exists() else "Missing HTML coverage report"
        })

        for check in checks:
            print(f"  {check['status']} {check['name']}: {check['details']}")

        return checks

    def validate_api_implementation(self) -> list[dict[str, str]]:
        """Validate API implementation status"""
        print("\n🌐 API Implementation Status")
        checks = []

        # Check FastAPI main files
        apifiles = [
            "services / report - generator / src / main.py",
            "services / report - generator / src / api / __init__.py",
            "services / report - generator / src / api / routes / health.py"
        ]

        for api_file in api_files:
            filepath = self.workspace_root / api_file
            checks.append({
                "name": f"API file: {api_file}",
                "status": "✅" if file_path.exists() else "❌",
                "details": f"Found at {file_path}" if file_path.exists() else f"Missing {api_file}"
            })

        # Check for API route implementations
        routesdir = self.workspace_root / "services" / "report - generator" / "src" / "api" / "routes"
        if routes_dir.exists():
            routefiles = list(routes_dir.glob("*.py"))
            checks.append({
                "name": f"API routes ({len(route_files)} files)",
                "status": "✅" if len(route_files) >= 2 else "⚠️",
                "details": f"Found {len(route_files)} route files: {[f.name for f in route_files]}"
            })
        else:
            checks.append({
                "name": "API routes directory",
                "status": "❌",
                "details": "Missing API routes directory"
            })

        for check in checks:
            print(f"  {check['status']} {check['name']}: {check['details']}")

        return checks

    def validate_integration_tests(self) -> list[dict[str, str]]:
        """Validate integration testing framework"""
        print("\n🔗 Integration Testing Framework")
        checks = []

        # Check for integration test files
        integrationdir = self.workspace_root / "tests" / "integration"
        if integration_dir.exists():
            integrationfiles = list(integration_dir.glob("test_*.py"))
            checks.append({
                "name": f"Integration test files ({len(integration_files)})",
                "status": "✅" if len(integration_files) >= 1 else "❌",
                "details": f"Found {len(integration_files)} files: {[f.name for f in integration_files]}"
            })
        else:
            checks.append({
                "name": "Integration test files",
                "status": "❌",
                "details": "Missing integration tests directory"
            })

        # Check for cross - service test scenarios
        expectedintegration_tests = [
            "test_phase1_workflow.py",
            "test_service_health.py",
            "test_data_flow.py"
        ]

        for test_file in expected_integration_tests:
            filepath = integration_dir / test_file if integration_dir.exists() else None
            checks.append({
                "name": f"Integration test: {test_file}",
                "status": "✅" if file_path and file_path.exists() else "❌",
                "details": f"Found at {file_path}" if file_path and file_path.exists() else f"Missing {test_file}"
            })

        for check in checks:
            print(f"  {check['status']} {check['name']}: {check['details']}")

        return checks

    def validate_performance_benchmarks(self) -> list[dict[str, str]]:
        """Validate performance benchmarking implementation"""
        print("\n📊 Performance Benchmarks")
        checks = []

        # Check for performance benchmark script
        benchmarkscript = self.workspace_root / "scripts" / "performance_benchmark.py"
        checks.append({
            "name": "Performance benchmark script",
            "status": "✅" if benchmark_script.exists() else "❌",
            "details": f"Found at {benchmark_script}" if benchmark_script.exists() else "Missing performance_benchmark.py"
        })

        # Check for benchmark results directory
        benchmarkresults = self.workspace_root / "benchmark_results"
        checks.append({
            "name": "Benchmark results directory",
            "status": "✅" if benchmark_results.exists() else "⚠️",
            "details": f"Found at {benchmark_results}" if benchmark_results.exists() else "No benchmark results yet"
        })

        # Check for performance test in test suite
        perftest = self.workspace_root / "tests" / "performance"
        checks.append({
            "name": "Performance test directory",
            "status": "✅" if perf_test.exists() else "⚠️",
            "details": f"Found at {perf_test}" if perf_test.exists() else "No dedicated performance tests"
        })

        for check in checks:
            print(f"  {check['status']} {check['name']}: {check['details']}")

        return checks

    def validate_documentation(self) -> list[dict[str, str]]:
        """Validate documentation completeness"""
        print("\n📖 Documentation Completeness")
        checks = []

        # Check for API documentation
        apidocs = self.workspace_root / "services" / "report - generator" / "docs"
        checks.append({
            "name": "API documentation directory",
            "status": "✅" if api_docs.exists() else "❌",
            "details": f"Found at {api_docs}" if api_docs.exists() else "Missing API documentation"
        })

        # Check for OpenAPI specification
        openapispec = api_docs / "openapi.yaml" if api_docs.exists() else None
        checks.append({
            "name": "OpenAPI specification",
            "status": "✅" if openapi_spec and openapi_spec.exists() else "❌",
            "details": f"Found at {openapi_spec}" if openapi_spec and openapi_spec.exists() else "Missing OpenAPI spec"
        })

        # Check for Phase 2 plan documentation
        phase2plan = self.workspace_root / "docs" / "sprint - reviews" / "2025 - 07 - 28 - phase2 - detailed - plan.md"
        checks.append({
            "name": "Phase 2 detailed plan",
            "status": "✅" if phase2_plan.exists() else "❌",
            "details": f"Found at {phase2_plan}" if phase2_plan.exists() else "Missing Phase 2 plan"
        })

        # Check for test documentation
        testreadme = self.workspace_root / "tests" / "README.md"
        checks.append({
            "name": "Test documentation",
            "status": "✅" if test_readme.exists() else "⚠️",
            "details": f"Found at {test_readme}" if test_readme.exists() else "Missing test documentation"
        })

        for check in checks:
            print(f"  {check['status']} {check['name']}: {check['details']}")

        return checks

    def validate_vscode_integration(self) -> list[dict[str, str]]:
        """Validate VS Code integration"""
        print("\n⚙️ VS Code Integration")
        checks = []

        # Check tasks.json
        tasksjson = self.workspace_root / ".vscode" / "tasks.json"
        if tasks_json.exists():
            try:
                with open(tasks_json) as f:
                    tasks_data = json.load(f)
                    task_labels = [task.get("label", "") for task in tasks_data.get("tasks", [])]

                    expectedtasks = [
                        "Test with Coverage",
                        "Performance Benchmark",
                        "Run Unit Tests (pytest)"
                    ]

                    for expected_task in expected_tasks:
                        found = any(expected_task in label for label in task_labels)
                        checks.append({
                            "name": f"VS Code task: {expected_task}",
                            "status": "✅" if found else "❌",
                            "details": "Task configured" if found else "Task missing"
                        })

            except Exception as e:
                checks.append({
                    "name": "tasks.json parsing",
                    "status": "❌",
                    "details": f"Failed to parse tasks.json: {str(e)}"
                })
        else:
            checks.append({
                "name": "tasks.json file",
                "status": "❌",
                "details": "Missing .vscode / tasks.json"
            })

        # Check launch.json
        launchjson = self.workspace_root / ".vscode" / "launch.json"
        checks.append({
            "name": "launch.json debug configuration",
            "status": "✅" if launch_json.exists() else "❌",
            "details": f"Found at {launch_json}" if launch_json.exists() else "Missing debug configuration"
        })

        for check in checks:
            print(f"  {check['status']} {check['name']}: {check['details']}")

        return checks


def main():
    """Main validation execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Phase 2 Implementation Validator")
    parser.add_argument("--workspace", help="Workspace root directory", default=None)
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    validator = Phase2Validator(args.workspace)
    results = validator.validate_all()

    if args.json:
        print(json.dumps(results, indent=2))

    # Exit with appropriate code
    sys.exit(0 if results["score"] >= 85 else 1)


if __name__ == "__main__":
    main()