"""
Enhanced Pytest Fixtures for Comprehensive Testing
Provides reusable fixtures for all testing scenarios
"""

import pytest
import tempfile
import asyncio
from pathlib import Path
from typing import Dict, List, Any
import shutil

# Import test factories
from .test_data_factories import (
    CSVDataFactory, 
    CSVFileFactory, 
    ProcessingResultFactory,
    TestEnvironmentFactory,
    TestDataConfig
)

# Import mock services
from .mock_services import (
    MockDirectoryProcessor,
    MockCSVTransformer,
    MockExcelGenerator,
    MockFileManager,
    MockConfigManager,
    MockLogger,
    MockMetricsCollector
)

# Import business models
import sys
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from business.services.report_processor import ReportProcessingService


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def test_config():
    """Basic test configuration"""
    return TestDataConfig(
        num_records=50,  # Smaller for faster tests
        date_range_days=3,
        add_noise=False  # Deterministic for testing
    )


@pytest.fixture
def large_test_config():
    """Configuration for performance/load testing"""
    return TestDataConfig(
        num_records=1000,
        date_range_days=30,
        add_noise=True
    )


# ============================================================================
# Data Factory Fixtures
# ============================================================================

@pytest.fixture
def csv_data_factory(test_config):
    """CSV data factory with test configuration"""
    return CSVDataFactory(test_config)


@pytest.fixture
def csv_file_factory(csv_data_factory):
    """CSV file factory"""
    return CSVFileFactory(csv_data_factory)


@pytest.fixture
def result_factory():
    """Processing result factory"""
    return ProcessingResultFactory()


# ============================================================================
# Mock Service Fixtures
# ============================================================================

@pytest.fixture
def mock_directory_processor():
    """Mock directory processor"""
    processor = MockDirectoryProcessor()
    yield processor
    processor.reset()


@pytest.fixture
def mock_csv_transformer():
    """Mock CSV transformer"""
    transformer = MockCSVTransformer()
    yield transformer
    transformer.reset()


@pytest.fixture
def mock_excel_generator():
    """Mock Excel generator"""
    generator = MockExcelGenerator()
    yield generator
    generator.reset()


@pytest.fixture
def mock_file_manager():
    """Mock file manager"""
    manager = MockFileManager()
    yield manager
    manager.reset()


@pytest.fixture
def mock_config_manager():
    """Mock configuration manager"""
    manager = MockConfigManager()
    yield manager
    manager.reset()


@pytest.fixture
def mock_logger():
    """Mock logger"""
    logger = MockLogger()
    yield logger
    logger.reset()


@pytest.fixture
def mock_metrics():
    """Mock metrics collector"""
    metrics = MockMetricsCollector()
    yield metrics
    metrics.reset()


@pytest.fixture
def all_mock_services(
    mock_directory_processor,
    mock_csv_transformer,
    mock_excel_generator,
    mock_file_manager,
    mock_config_manager,
    mock_logger,
    mock_metrics
):
    """All mock services in a convenient bundle"""
    return {
        'directory_processor': mock_directory_processor,
        'csv_transformer': mock_csv_transformer,
        'excel_generator': mock_excel_generator,
        'file_manager': mock_file_manager,
        'config_manager': mock_config_manager,
        'logger': mock_logger,
        'metrics': mock_metrics
    }


# ============================================================================
# Service Fixtures
# ============================================================================

@pytest.fixture
def report_processor_with_mocks(all_mock_services):
    """Report processor with all mock dependencies"""
    return ReportProcessingService(
        directory_processor=all_mock_services['directory_processor'],
        csv_transformer=all_mock_services['csv_transformer'],
        excel_generator=all_mock_services['excel_generator'],
        file_manager=all_mock_services['file_manager'],
        config_manager=all_mock_services['config_manager'],
        logger=all_mock_services['logger'],
        metrics=all_mock_services['metrics']
    )


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def sample_csv_files(csv_file_factory):
    """Sample CSV files for testing"""
    files = []
    temp_dirs = []
    
    try:
        for file_type in ["ACQ", "Productivity"]:
            csv_file = csv_file_factory.create_csv_file(file_type=file_type)
            files.append(csv_file)
            temp_dirs.append(Path(csv_file.file_path).parent)
        
        yield files
        
    finally:
        # Cleanup
        for csv_file in files:
            try:
                Path(csv_file.file_path).unlink(missing_ok=True)
            except Exception:
                pass


@pytest.fixture
def test_directory_with_files(csv_file_factory):
    """Temporary directory with realistic test files"""
    with TestEnvironmentFactory() as env:
        temp_dir, csv_files = env.create_test_directory_with_files(
            file_types=["ACQ", "Productivity", "Campaign_Interactions"],
            num_dates=2,
            num_hours=2
        )
        yield temp_dir, csv_files


@pytest.fixture
def large_test_directory(csv_file_factory, large_test_config):
    """Large test directory for performance testing"""
    factory = CSVFileFactory(CSVDataFactory(large_test_config))
    
    with TestEnvironmentFactory() as env:
        temp_dir, csv_files = env.create_test_directory_with_files(
            file_types=["ACQ", "Productivity", "Campaign_Interactions", "QCBS"],
            num_dates=5,
            num_hours=4
        )
        yield temp_dir, csv_files


# ============================================================================
# Test Environment Fixtures
# ============================================================================

@pytest.fixture
def temp_output_dir():
    """Temporary directory for test outputs"""
    temp_dir = tempfile.mkdtemp(prefix="test_output_")
    yield temp_dir
    try:
        shutil.rmtree(temp_dir)
    except Exception:
        pass


@pytest.fixture
def isolated_test_environment(test_directory_with_files, temp_output_dir):
    """Complete isolated test environment"""
    input_dir, csv_files = test_directory_with_files
    
    return {
        'input_directory': input_dir,
        'output_directory': temp_output_dir,
        'csv_files': csv_files,
        'expected_file_count': len(csv_files),
        'file_types': list(set(f.filename.split('__')[0] for f in csv_files))
    }


# ============================================================================
# Scenario-Specific Fixtures
# ============================================================================

@pytest.fixture
def success_scenario(all_mock_services, sample_csv_files):
    """Pre-configured success scenario"""
    
    # Configure mocks for success
    all_mock_services['directory_processor'].set_files_to_return([
        f.file_path for f in sample_csv_files
    ])
    
    all_mock_services['csv_transformer'].set_transform_result({
        'success': True,
        'dataframe': None,
        'message': 'Transform successful'
    })
    
    all_mock_services['excel_generator'].set_workbook_result(b'mock_excel_data')
    all_mock_services['file_manager'].set_write_success(True)
    
    return {
        'services': all_mock_services,
        'csv_files': sample_csv_files,
        'expected_result': 'success'
    }


@pytest.fixture
def failure_scenario(all_mock_services):
    """Pre-configured failure scenario"""
    
    # Configure mocks for failure
    all_mock_services['directory_processor'].set_files_to_return([])
    
    return {
        'services': all_mock_services,
        'expected_result': 'failure',
        'expected_error': 'No files found'
    }


@pytest.fixture
def error_scenario(all_mock_services, sample_csv_files):
    """Pre-configured error scenario"""
    
    # Configure mocks for errors
    all_mock_services['directory_processor'].set_files_to_return([
        f.file_path for f in sample_csv_files
    ])
    
    all_mock_services['csv_transformer'].set_transform_error(
        "CSV transformation failed"
    )
    
    return {
        'services': all_mock_services,
        'csv_files': sample_csv_files,
        'expected_result': 'error',
        'expected_error': 'CSV transformation failed'
    }


# ============================================================================
# Performance Testing Fixtures
# ============================================================================

@pytest.fixture
def performance_timer():
    """Timer for performance testing"""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            
        def start(self):
            self.start_time = time.time()
            
        def stop(self):
            self.end_time = time.time()
            return self.elapsed()
            
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()


@pytest.fixture
def performance_thresholds():
    """Performance thresholds for testing"""
    return {
        'max_processing_time': 10.0,  # seconds
        'max_file_processing_time': 2.0,  # seconds per file
        'max_memory_usage': 100 * 1024 * 1024,  # 100MB
        'max_files_per_second': 5
    }


# ============================================================================
# Async Testing Fixtures
# ============================================================================

@pytest.fixture
def event_loop():
    """Event loop for async testing"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def assert_helpers():
    """Helper functions for common assertions"""
    
    class AssertHelpers:
        @staticmethod
        def assert_processing_result_success(result):
            """Assert that processing result indicates success"""
            assert result.success is True
            assert result.files_processed > 0
            assert result.output_file is not None
            assert len(result.errors) == 0
            
        @staticmethod
        def assert_processing_result_failure(result, expected_error=None):
            """Assert that processing result indicates failure"""
            assert result.success is False
            assert len(result.errors) > 0
            if expected_error:
                assert expected_error in str(result.errors)
                
        @staticmethod
        def assert_mock_called(mock_service, method_name, times=None):
            """Assert that mock service method was called"""
            call_count = mock_service.get_call_count(method_name)
            if times is not None:
                assert call_count == times
            else:
                assert call_count > 0
                
        @staticmethod
        def assert_files_created(directory, expected_count=None, pattern="*.xlsx"):
            """Assert that files were created in directory"""
            files = list(Path(directory).glob(pattern))
            if expected_count is not None:
                assert len(files) == expected_count
            else:
                assert len(files) > 0
            return files
    
    return AssertHelpers()
