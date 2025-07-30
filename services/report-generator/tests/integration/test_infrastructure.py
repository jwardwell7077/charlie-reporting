"""
Integration Test Infrastructure
End-to-end testing capabilities for complete workflows
"""

import pytest
import asyncio
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd

# Test utilities
from .enhanced_fixtures import *
from .test_data_factories import TestEnvironmentFactory


class IntegrationTestRunner:
    """Orchestrates complex integration testing scenarios"""
    
    def __init__(self):
        self.test_results = []
        self.performance_metrics = {}
        
    async def run_complete_workflow_test(
        self,
        report_processor,
        test_environment: Dict[str, Any],
        expected_outcomes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run a complete end-to-end workflow test"""
        
        start_time = time.time()
        
        try:
            # Execute the main workflow
            result = await report_processor.process_directory(
                directory_path=test_environment['input_directory'],
                output_directory=test_environment['output_directory']
            )
            
            end_time = time.time()
            
            # Validate results
            validation_results = self._validate_workflow_results(
                result, test_environment, expected_outcomes
            )
            
            # Collect performance metrics
            performance_metrics = {
                'total_time': end_time - start_time,
                'files_per_second': (
                    result.files_processed / (end_time - start_time)
                    if result.files_processed > 0 else 0
                ),
                'records_per_second': (
                    result.total_records / (end_time - start_time)
                    if result.total_records > 0 else 0
                )
            }
            
            return {
                'success': True,
                'result': result,
                'validation': validation_results,
                'performance': performance_metrics,
                'execution_time': end_time - start_time
            }
            
        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'error': str(e),
                'execution_time': end_time - start_time
            }
    
    def _validate_workflow_results(
        self,
        result,
        test_environment: Dict[str, Any],
        expected_outcomes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate workflow results against expectations"""
        
        validation_results = {
            'success_match': result.success == expected_outcomes.get('success', True),
            'file_count_match': result.files_processed == expected_outcomes.get('files_processed'),
            'output_file_exists': False,
            'output_file_valid': False,
            'errors': [],
            'warnings': []
        }
        
        # Check output file
        if result.output_file:
            output_path = Path(result.output_file)
            validation_results['output_file_exists'] = output_path.exists()
            
            if output_path.exists():
                try:
                    # Attempt to read Excel file to validate format
                    pd.read_excel(output_path, sheet_name=None)
                    validation_results['output_file_valid'] = True
                except Exception as e:
                    validation_results['errors'].append(f"Invalid output file: {e}")
        
        # Check expected error conditions
        if expected_outcomes.get('should_fail', False):
            if result.success:
                validation_results['errors'].append("Expected failure but got success")
        
        # Check expected file processing counts
        expected_files = expected_outcomes.get('files_processed')
        if expected_files is not None and result.files_processed != expected_files:
            validation_results['warnings'].append(
                f"Expected {expected_files} files, processed {result.files_processed}"
            )
        
        return validation_results


class PerformanceTestSuite:
    """Performance and load testing infrastructure"""
    
    def __init__(self):
        self.metrics = {}
        
    async def run_load_test(
        self,
        report_processor,
        file_counts: List[int],
        record_counts: List[int],
        iterations: int = 3
    ) -> Dict[str, Any]:
        """Run load testing with varying data sizes"""
        
        results = []
        
        for file_count in file_counts:
            for record_count in record_counts:
                iteration_results = []
                
                for i in range(iterations):
                    # Create test environment with specified parameters
                    with TestEnvironmentFactory() as env:
                        temp_dir, csv_files = env.create_test_directory_with_files(
                            file_types=["ACQ"] * file_count,
                            num_dates=1,
                            num_hours=1
                        )
                        
                        # Measure performance
                        start_time = time.time()
                        start_memory = self._get_memory_usage()
                        
                        try:
                            result = await report_processor.process_directory(
                                directory_path=temp_dir,
                                output_directory=temp_dir
                            )
                            
                            end_time = time.time()
                            end_memory = self._get_memory_usage()
                            
                            iteration_results.append({
                                'success': result.success,
                                'files_processed': result.files_processed,
                                'total_records': result.total_records,
                                'execution_time': end_time - start_time,
                                'memory_delta': end_memory - start_memory,
                                'throughput_files_per_sec': result.files_processed / (end_time - start_time),
                                'throughput_records_per_sec': result.total_records / (end_time - start_time)
                            })
                            
                        except Exception as e:
                            iteration_results.append({
                                'success': False,
                                'error': str(e),
                                'execution_time': time.time() - start_time
                            })
                
                # Calculate averages for this configuration
                successful_runs = [r for r in iteration_results if r.get('success', False)]
                
                if successful_runs:
                    avg_metrics = {
                        'file_count': file_count,
                        'record_count': record_count,
                        'iterations': len(successful_runs),
                        'avg_execution_time': sum(r['execution_time'] for r in successful_runs) / len(successful_runs),
                        'avg_memory_delta': sum(r.get('memory_delta', 0) for r in successful_runs) / len(successful_runs),
                        'avg_throughput_files': sum(r['throughput_files_per_sec'] for r in successful_runs) / len(successful_runs),
                        'avg_throughput_records': sum(r['throughput_records_per_sec'] for r in successful_runs) / len(successful_runs),
                        'success_rate': len(successful_runs) / len(iteration_results) * 100
                    }
                    results.append(avg_metrics)
                else:
                    results.append({
                        'file_count': file_count,
                        'record_count': record_count,
                        'success_rate': 0,
                        'error': 'All iterations failed'
                    })
        
        return {
            'load_test_results': results,
            'summary': self._generate_performance_summary(results)
        }
    
    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss
        except ImportError:
            # Fallback if psutil not available
            return 0
    
    def _generate_performance_summary(self, results: List[Dict]) -> Dict[str, Any]:
        """Generate performance summary from results"""
        
        successful_results = [r for r in results if r.get('success_rate', 0) > 0]
        
        if not successful_results:
            return {'error': 'No successful test runs'}
        
        return {
            'total_configurations_tested': len(results),
            'successful_configurations': len(successful_results),
            'fastest_execution_time': min(r['avg_execution_time'] for r in successful_results),
            'slowest_execution_time': max(r['avg_execution_time'] for r in successful_results),
            'highest_throughput_files': max(r['avg_throughput_files'] for r in successful_results),
            'highest_throughput_records': max(r['avg_throughput_records'] for r in successful_results),
            'average_success_rate': sum(r['success_rate'] for r in successful_results) / len(successful_results)
        }


class ErrorInjectionTestSuite:
    """Test suite for error handling and resilience"""
    
    def __init__(self):
        self.error_scenarios = []
        
    async def test_file_system_errors(self, report_processor, test_environment):
        """Test various file system error conditions"""
        
        scenarios = [
            {
                'name': 'permission_denied',
                'setup': lambda: self._make_directory_readonly(test_environment['input_directory']),
                'expected_error': 'Permission denied'
            },
            {
                'name': 'disk_full',
                'setup': lambda: self._simulate_disk_full(test_environment['output_directory']),
                'expected_error': 'No space left'
            },
            {
                'name': 'corrupt_files',
                'setup': lambda: self._create_corrupt_csv_files(test_environment['input_directory']),
                'expected_error': 'Invalid CSV'
            }
        ]
        
        results = []
        
        for scenario in scenarios:
            try:
                # Setup error condition
                scenario['setup']()
                
                # Attempt processing
                result = await report_processor.process_directory(
                    directory_path=test_environment['input_directory'],
                    output_directory=test_environment['output_directory']
                )
                
                # Validate error handling
                results.append({
                    'scenario': scenario['name'],
                    'success': not result.success,  # Should fail
                    'error_handled_correctly': scenario['expected_error'] in str(result.errors),
                    'result': result
                })
                
            except Exception as e:
                results.append({
                    'scenario': scenario['name'],
                    'success': True,  # Exception is expected
                    'error_handled_correctly': scenario['expected_error'] in str(e),
                    'exception': str(e)
                })
        
        return results
    
    def _make_directory_readonly(self, directory: str):
        """Make directory read-only to simulate permission errors"""
        # This would implement actual permission changes
        # For testing purposes, we might mock this
        pass
    
    def _simulate_disk_full(self, directory: str):
        """Simulate disk full condition"""
        # This would implement disk space simulation
        # For testing purposes, we might mock this
        pass
    
    def _create_corrupt_csv_files(self, directory: str):
        """Create corrupt CSV files for testing"""
        corrupt_file = Path(directory) / "corrupt__2025-07-29__0900.csv"
        with open(corrupt_file, 'w') as f:
            f.write("This is not a valid CSV file content\n")
            f.write("Random binary data: \x00\x01\x02\x03")


# Integration Test Markers for pytest
pytest_integration_markers = {
    'integration': pytest.mark.integration,
    'slow': pytest.mark.slow,
    'performance': pytest.mark.performance,
    'load': pytest.mark.load,
    'error_injection': pytest.mark.error_injection,
    'end_to_end': pytest.mark.end_to_end
}
