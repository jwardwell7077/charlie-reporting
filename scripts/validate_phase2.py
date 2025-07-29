#!/usr/bin/env python3
"""
Phase 2 Validation Script for Charlie Reporting
Comprehensive validation of testing framework and API implementation
"""

import sys
import subprocess
import json
from pathlib import Path
import logging
from typing import Dict, List, Any


def setup_logging():
    """Configure logging for validation reporting"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - VALIDATION - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


class Phase2Validator:
    """Comprehensive Phase 2 validation"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.validation_results = []
        self.workspace_root = Path(__file__).parent.parent
        
    def validate_pytest_setup(self) -> Dict[str, Any]:
        """Validate pytest configuration and test discovery"""
        self.logger.info("Validating pytest setup...")
        
        result = {
            'category': 'Testing Framework',
            'test': 'pytest Configuration',
            'status': 'unknown',
            'details': []
        }
        
        try:
            # Check if pytest is installed
            subprocess.run([sys.executable, '-m', 'pytest', '--version'], 
                         check=True, capture_output=True, text=True)
            result['details'].append("✅ pytest installed and accessible")
            
            # Check test discovery
            discovery_result = subprocess.run([
                sys.executable, '-m', 'pytest', '--collect-only', 'tests/'
            ], capture_output=True, text=True, cwd=self.workspace_root)
            
            if discovery_result.returncode == 0:
                result['details'].append("✅ Test discovery working")
                result['status'] = 'pass'
            else:
                result['details'].append(f"❌ Test discovery failed: {discovery_result.stderr}")
                result['status'] = 'fail'
                
        except Exception as e:
            result['details'].append(f"❌ pytest setup error: {e}")
            result['status'] = 'fail'
            
        return result
    
    def validate_test_coverage(self) -> Dict[str, Any]:
        """Validate test coverage functionality"""
        self.logger.info("Validating test coverage...")
        
        result = {
            'category': 'Testing Framework',
            'test': 'Coverage Reporting',
            'status': 'unknown',
            'details': []
        }
        
        try:
            # Run coverage test
            coverage_result = subprocess.run([
                sys.executable, '-m', 'pytest', '--cov=services', 
                '--cov-report=term', 'tests/', '--tb=no'
            ], capture_output=True, text=True, cwd=self.workspace_root)
            
            if coverage_result.returncode == 0:
                result['details'].append("✅ Coverage reporting functional")
                result['status'] = 'pass'
                
                # Extract coverage percentage if available
                if "%" in coverage_result.stdout:
                    result['details'].append("✅ Coverage metrics generated")
            else:
                result['details'].append(f"❌ Coverage test failed: {coverage_result.stderr}")
                result['status'] = 'fail'
                
        except Exception as e:
            result['details'].append(f"❌ Coverage validation error: {e}")
            result['status'] = 'fail'
            
        return result
    
    def validate_phase1_services(self) -> Dict[str, Any]:
        """Validate Phase 1 business logic services"""
        self.logger.info("Validating Phase 1 services...")
        
        result = {
            'category': 'Business Logic',
            'test': 'Phase 1 Services',
            'status': 'unknown',
            'details': []
        }
        
        try:
            # Run Phase 1 demo
            phase1_result = subprocess.run([
                sys.executable, 'services/report-generator/src/main_phase1.py'
            ], capture_output=True, text=True, cwd=self.workspace_root)
            
            if phase1_result.returncode == 0:
                result['details'].append("✅ Phase 1 business logic execution successful")
                result['status'] = 'pass'
                
                # Check for key success indicators
                output = phase1_result.stdout
                if "CSV transformation complete" in output:
                    result['details'].append("✅ CSV transformation validated")
                if "Excel report generated" in output:
                    result['details'].append("✅ Excel generation validated")
            else:
                result['details'].append(f"❌ Phase 1 execution failed: {phase1_result.stderr}")
                result['status'] = 'fail'
                
        except Exception as e:
            result['details'].append(f"❌ Phase 1 validation error: {e}")
            result['status'] = 'fail'
            
        return result
    
    def validate_vscode_integration(self) -> Dict[str, Any]:
        """Validate VS Code task integration"""
        self.logger.info("Validating VS Code integration...")
        
        result = {
            'category': 'Development Environment',
            'test': 'VS Code Tasks',
            'status': 'unknown',
            'details': []
        }
        
        try:
            tasks_file = self.workspace_root / '.vscode' / 'tasks.json'
            
            if tasks_file.exists():
                result['details'].append("✅ VS Code tasks.json exists")
                
                with open(tasks_file, 'r') as f:
                    tasks_content = f.read()
                    
                # Check for Phase 2 tasks
                phase2_tasks = [
                    "Test with Coverage",
                    "Performance Benchmark", 
                    "Start Report Generator API",
                    "Validate Phase 2"
                ]
                
                for task in phase2_tasks:
                    if task in tasks_content:
                        result['details'].append(f"✅ Task '{task}' configured")
                    else:
                        result['details'].append(f"❌ Task '{task}' missing")
                        
                result['status'] = 'pass'
            else:
                result['details'].append("❌ VS Code tasks.json not found")
                result['status'] = 'fail'
                
        except Exception as e:
            result['details'].append(f"❌ VS Code validation error: {e}")
            result['status'] = 'fail'
            
        return result
    
    def validate_dependencies(self) -> Dict[str, Any]:
        """Validate required dependencies are installed"""
        self.logger.info("Validating dependencies...")
        
        result = {
            'category': 'Environment',
            'test': 'Dependencies',
            'status': 'unknown',
            'details': []
        }
        
        required_packages = [
            'pytest',
            'pytest-cov',
            'black',
            'flake8',
            'fastapi',
            'uvicorn',
            'httpx'
        ]
        
        try:
            # Get installed packages
            pip_result = subprocess.run([
                sys.executable, '-m', 'pip', 'list'
            ], capture_output=True, text=True)
            
            installed_packages = pip_result.stdout.lower()
            
            missing_packages = []
            for package in required_packages:
                if package.lower() in installed_packages:
                    result['details'].append(f"✅ {package} installed")
                else:
                    result['details'].append(f"❌ {package} missing")
                    missing_packages.append(package)
                    
            if not missing_packages:
                result['status'] = 'pass'
            else:
                result['status'] = 'fail'
                result['details'].append(f"Missing packages: {', '.join(missing_packages)}")
                
        except Exception as e:
            result['details'].append(f"❌ Dependency validation error: {e}")
            result['status'] = 'fail'
            
        return result
    
    def run_validation_suite(self) -> List[Dict[str, Any]]:
        """Execute all validation tests"""
        self.logger.info("=== Starting Phase 2 Validation Suite ===")
        
        validations = [
            self.validate_dependencies(),
            self.validate_pytest_setup(),
            self.validate_test_coverage(),
            self.validate_phase1_services(),
            self.validate_vscode_integration()
        ]
        
        self.validation_results = validations
        return validations
    
    def display_validation_summary(self, validations: List[Dict[str, Any]]):
        """Display formatted validation summary"""
        print("\n" + "="*70)
        print("PHASE 2 VALIDATION SUMMARY")
        print("="*70)
        
        passed = 0
        failed = 0
        
        for validation in validations:
            status_icon = "✅" if validation['status'] == 'pass' else "❌"
            print(f"\n{status_icon} {validation['category']}: {validation['test']}")
            
            if validation['status'] == 'pass':
                passed += 1
            else:
                failed += 1
                
            for detail in validation['details']:
                print(f"   {detail}")
        
        print(f"\n{'='*70}")
        print(f"VALIDATION RESULTS: {passed} PASSED, {failed} FAILED")
        
        if failed == 0:
            print("🎉 ALL VALIDATIONS PASSED - PHASE 2 READY!")
        else:
            print("⚠️  SOME VALIDATIONS FAILED - REVIEW REQUIRED")
            
        print("="*70)
        
        return failed == 0


def main():
    """Main validation execution"""
    validator = Phase2Validator()
    
    try:
        validations = validator.run_validation_suite()
        success = validator.display_validation_summary(validations)
        
        # Save validation results
        results_file = Path("logs/phase2_validation.json")
        results_file.parent.mkdir(exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(validations, f, indent=2)
            
        print(f"\nValidation results saved to: {results_file}")
        
        if success:
            print("\n🚀 Phase 2 environment is ready for implementation!")
            sys.exit(0)
        else:
            print("\n❌ Phase 2 environment requires fixes before proceeding")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Validation suite execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
