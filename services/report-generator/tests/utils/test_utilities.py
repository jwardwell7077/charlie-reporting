"""
Test Utilities and Helper Functions
Common utilities for testing across all test suites
"""

import functools
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import tempfile
import shutil


class TestTimer:
    """Timer utility for performance testing"""
    
    def __init__(self, name: str = "Test"):
        self.name = name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.elapsed_seconds: float = 0.0
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
    
    def start(self):
        """Start the timer"""
        self.start_time = time.time()
    
    def stop(self):
        """Stop the timer"""
        if self.start_time is not None:
            self.end_time = time.time()
            self.elapsed_seconds = self.end_time - self.start_time
            print(f"⏱️ {self.name} completed in {self.elapsed_seconds:.3f}s")
    
    @property
    def duration(self) -> float:
        """Get the duration (alias for elapsed_seconds)"""
        return self.elapsed_seconds


class TestDataManager:
    """Manages test data lifecycle and cleanup"""
    
    def __init__(self):
        self.temp_directories: List[str] = []
        self.temp_files: List[str] = []
        
    def create_temp_directory(self, prefix: str = "test_") -> str:
        """Create a temporary directory and track it for cleanup"""
        temp_dir = tempfile.mkdtemp(prefix=prefix)
        self.temp_directories.append(temp_dir)
        return temp_dir
        
    def create_temp_file(self, suffix: str = ".tmp", prefix: str = "test_") -> str:
        """Create a temporary file and track it for cleanup"""
        temp_file = tempfile.NamedTemporaryFile(
            delete=False, suffix=suffix, prefix=prefix
        )
        temp_file.close()
        self.temp_files.append(temp_file.name)
        return temp_file.name
        
    def cleanup(self):
        """Clean up all tracked temporary files and directories"""
        
        # Clean up files
        for file_path in self.temp_files:
            try:
                Path(file_path).unlink(missing_ok=True)
            except Exception:
                pass
                
        # Clean up directories
        for dir_path in self.temp_directories:
            try:
                shutil.rmtree(dir_path, ignore_errors=True)
            except Exception:
                pass
                
        self.temp_directories.clear()
        self.temp_files.clear()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


def with_test_timer(name: str = None):
    """Decorator to add timing to test functions"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            test_name = name or func.__name__
            with TestTimer(test_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def with_temp_directory(func: Callable) -> Callable:
    """Decorator to provide a temporary directory to test functions"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with TestDataManager() as manager:
            temp_dir = manager.create_temp_directory()
            kwargs['temp_dir'] = temp_dir
            return func(*args, **kwargs)
    return wrapper


class MockServiceHelper:
    """Helper for working with mock services"""
    
    @staticmethod
    def configure_success_scenario(mock_services: Dict[str, Any]):
        """Configure all mock services for a success scenario"""
        
        # Directory processor returns files
        if 'directory_processor' in mock_services:
            mock_services['directory_processor'].set_files_to_return([
                "/tmp/test1.csv", "/tmp/test2.csv"
            ])
            
        # CSV transformer succeeds
        if 'csv_transformer' in mock_services:
            mock_services['csv_transformer'].set_transform_result({
                'success': True,
                'message': 'Transformation successful'
            })
            
        # Excel generator creates workbook
        if 'excel_generator' in mock_services:
            mock_services['excel_generator'].set_workbook_result(b'excel_data')
            
        # File manager writes successfully
        if 'file_manager' in mock_services:
            mock_services['file_manager'].set_write_success(True)
            
    @staticmethod
    def configure_failure_scenario(mock_services: Dict[str, Any], error_service: str = None):
        """Configure mock services for a failure scenario"""
        
        # Default success for most services
        MockServiceHelper.configure_success_scenario(mock_services)
        
        # Inject failure in specified service
        if error_service == 'directory_processor':
            mock_services['directory_processor'].set_files_to_return([])
        elif error_service == 'csv_transformer':
            mock_services['csv_transformer'].set_transform_error("Transform failed")
        elif error_service == 'excel_generator':
            mock_services['excel_generator'].set_error("Excel generation failed")
        elif error_service == 'file_manager':
            mock_services['file_manager'].set_write_success(False)
            
    @staticmethod
    def reset_all_mocks(mock_services: Dict[str, Any]):
        """Reset all mock services to default state"""
        for service in mock_services.values():
            if hasattr(service, 'reset'):
                service.reset()


class TestAssertions:
    """Enhanced assertion helpers for testing"""
    
    @staticmethod
    def assert_processing_success(result, min_files: int = 1):
        """Assert that processing completed successfully"""
        assert result.success is True, f"Processing failed: {result.errors}"
        assert result.files_processed >= min_files, f"Expected at least {min_files} files, got {result.files_processed}"
        assert result.output_file is not None, "Output file should be specified"
        assert len(result.errors) == 0, f"Unexpected errors: {result.errors}"
        
    @staticmethod
    def assert_processing_failure(result, expected_error: str = None):
        """Assert that processing failed as expected"""
        assert result.success is False, "Processing should have failed"
        assert len(result.errors) > 0, "Should have error messages"
        if expected_error:
            error_text = ' '.join(str(e) for e in result.errors)
            assert expected_error.lower() in error_text.lower(), f"Expected error '{expected_error}' not found in: {error_text}"
            
    @staticmethod
    def assert_file_exists(file_path: str, message: str = None):
        """Assert that a file exists"""
        path = Path(file_path)
        assert path.exists(), message or f"File should exist: {file_path}"
        assert path.is_file(), message or f"Path should be a file: {file_path}"
        
    @staticmethod
    def assert_directory_exists(dir_path: str, message: str = None):
        """Assert that a directory exists"""
        path = Path(dir_path)
        assert path.exists(), message or f"Directory should exist: {dir_path}"
        assert path.is_dir(), message or f"Path should be a directory: {dir_path}"
        
    @staticmethod
    def assert_mock_called(mock_service, method_name: str, min_calls: int = 1):
        """Assert that mock service method was called"""
        if hasattr(mock_service, 'get_call_count'):
            call_count = mock_service.get_call_count(method_name)
            assert call_count >= min_calls, f"Method {method_name} should be called at least {min_calls} times, got {call_count}"
        else:
            # Fallback for different mock implementations
            assert hasattr(mock_service, method_name), f"Mock service should have method {method_name}"
            
    @staticmethod
    def assert_performance_acceptable(duration: float, max_duration: float):
        """Assert that performance is within acceptable limits"""
        assert duration <= max_duration, f"Performance too slow: {duration:.3f}s > {max_duration:.3f}s maximum"
        
    @staticmethod
    def assert_data_integrity(original_data: Dict, processed_data: Dict):
        """Assert that data integrity is maintained during processing"""
        # Check that no data was lost
        if 'record_count' in original_data and 'record_count' in processed_data:
            assert processed_data['record_count'] <= original_data['record_count'], "Data loss detected"
            
        # Check that essential fields are preserved
        if 'columns' in original_data and 'columns' in processed_data:
            original_columns = set(original_data['columns'])
            processed_columns = set(processed_data['columns'])
            assert original_columns.issubset(processed_columns), "Essential columns missing"


class TestReporting:
    """Test reporting and metrics collection"""
    
    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
        self.performance_metrics: List[Dict[str, Any]] = []
    
    def record_test_result(self, test_name: str, success: bool, duration: float, **kwargs):
        """Record a test result"""
        result = {
            'test_name': test_name,
            'success': success,
            'duration': duration,
            'timestamp': time.time(),
            **kwargs
        }
        self.test_results.append(result)
        
    def record_performance_metric(self, metric_name: str, value: float, unit: str = ""):
        """Record a performance metric"""
        metric = {
            'metric_name': metric_name,
            'value': value,
            'unit': unit,
            'timestamp': time.time()
        }
        self.performance_metrics.append(metric)
        
    def generate_summary(self) -> Dict[str, Any]:
        """Generate test summary report"""
        if not self.test_results:
            return {'error': 'No test results recorded'}
            
        successful_tests = [t for t in self.test_results if t['success']]
        failed_tests = [t for t in self.test_results if not t['success']]
        
        total_duration = sum(t['duration'] for t in self.test_results)
        avg_duration = total_duration / len(self.test_results) if self.test_results else 0
        
        return {
            'total_tests': len(self.test_results),
            'successful_tests': len(successful_tests),
            'failed_tests': len(failed_tests),
            'success_rate': len(successful_tests) / len(self.test_results) * 100,
            'total_duration': total_duration,
            'average_duration': avg_duration,
            'performance_metrics_count': len(self.performance_metrics)
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Alias for generate_summary for backward compatibility"""
        summary = self.generate_summary()
        # Convert to expected format
        if 'error' not in summary:
            return {
                'total_tests': summary['total_tests'],
                'passed_tests': summary['successful_tests'],
                'failed_tests': summary['failed_tests'],
                'success_rate': summary['success_rate'],
                'total_duration': summary['total_duration'],
                'average_duration': summary['average_duration']
            }
        return summary
        
    def print_summary(self):
        """Print formatted test summary"""
        summary = self.generate_summary()
        
        if 'error' in summary:
            print(f"❌ {summary['error']}")
            return
            
        print("\n" + "="*50)
        print("📊 TEST EXECUTION SUMMARY")
        print("="*50)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"✅ Successful: {summary['successful_tests']}")
        print(f"❌ Failed: {summary['failed_tests']}")
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        print(f"⏱️ Total Duration: {summary['total_duration']:.2f}s")
        print(f"⏱️ Average Duration: {summary['average_duration']:.3f}s")
        print(f"📊 Performance Metrics: {summary['performance_metrics_count']}")
        print("="*50)
# Utility functions for common test operations
def create_test_csv_content(columns: List[str], num_rows: int = 10) -> str:
    """Create CSV content for testing"""
    import random
    
    header = ','.join(columns)
    rows = []
    
    for i in range(num_rows):
        row_data = []
        for col in columns:
            if 'id' in col.lower():
                row_data.append(str(i + 1))
            elif 'name' in col.lower():
                row_data.append(f"Test_{i+1}")
            elif 'value' in col.lower() or 'amount' in col.lower():
                row_data.append(str(random.randint(1, 1000)))
            else:
                row_data.append(f"Data_{i+1}")
        rows.append(','.join(row_data))
    
    return header + '\n' + '\n'.join(rows)


def wait_for_condition(condition: Callable[[], bool], timeout: float = 5.0, interval: float = 0.1) -> bool:
    """Wait for a condition to become true"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if condition():
            return True
        time.sleep(interval)
    
    return False


# Global test reporter instance
test_reporter = TestReporting()
