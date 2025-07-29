"""
test_main_processor.py
---------------------
Tests for the ReportProcessor class and main.py real-time processing functionality.

Author: Jonathan Wardwell, Copilot, GPT-4o
License: MIT
"""

import os
import shutil
import pandas as pd
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Import the classes we're testing
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import ReportProcessor
from config_loader import ConfigLoader
from email_fetcher import EmailFetcher
from services.report_generator.csv_processor import CSVTransformer
from services.report_generator.excel_generator import ExcelWriter


# --- Fixtures ---
@pytest.fixture
def sample_config():
    """Mock config matching the actual config.toml"""
    class DummyConfig:
        @property
        def attachment_rules(self):
            return {
                'IB_Calls.csv': {'columns': ['Agent Name', 'Handle', 'Avg Handle']},
                'QCBs.csv': {'columns': ['Agent Name', 'Handle']},
                'Dials.csv': {'columns': ['Agent Name', 'Handle', 'Avg Handle', 'Avg Talk', 'Avg Hold']},
                'Productivity.csv': {'columns': ['Agent Name', 'Logged In', 'On Queue', 'Idle', 'Off Queue', 'Interacting']},
                'Campaign_Interactions.csv': {'columns': ['Date', 'Initial Direction', 'First Queue']},
                'ACQ.csv': {'columns': ['Agent Name', 'Handle']},
                'RESC.csv': {'columns': ['Agent Name', 'Handle']},
            }
        
        @property
        def global_filter(self):
            return {
                'sender': ['reports@example.com'],
                'subject_contains': ['Daily Report']
            }
    
    return DummyConfig()


@pytest.fixture
def temp_dirs(tmp_path):
    """Create temporary directories for testing"""
    raw_dir = tmp_path / 'raw'
    archive_dir = tmp_path / 'archive'
    output_dir = tmp_path / 'output'
    
    raw_dir.mkdir()
    archive_dir.mkdir()
    output_dir.mkdir()
    
    return {
        'raw': str(raw_dir),
        'archive': str(archive_dir),
        'output': str(output_dir)
    }


@pytest.fixture
def mock_components():
    """Create mocked components for ReportProcessor"""
    mock_email_fetcher = Mock(spec=EmailFetcher)
    mock_transformer = Mock(spec=CSVTransformer)
    mock_excel_writer = Mock(spec=ExcelWriter)
    
    return {
        'email_fetcher': mock_email_fetcher,
        'transformer': mock_transformer,
        'excel_writer': mock_excel_writer
    }


@pytest.fixture
def report_processor(sample_config, mock_components):
    """Create ReportProcessor with mocked components"""
    processor = ReportProcessor(sample_config, debug=False)
    
    # Replace components with mocks
    processor.email_fetcher = mock_components['email_fetcher']
    processor.transformer = mock_components['transformer']
    processor.excel_writer = mock_components['excel_writer']
    
    return processor


# --- Helper Functions ---
def create_test_csv(path, file_type, columns, data_rows=None):
    """Create test CSV file"""
    if data_rows is None:
        data_rows = [[f"{col}_value_{i}" for i, col in enumerate(columns)]]
    
    df = pd.DataFrame(data_rows, columns=columns)
    df.to_csv(path, index=False)
    return df


def create_sample_data():
    """Create sample transformed data for testing"""
    return {
        'IB_Calls': [pd.DataFrame({
            'email_received_date': ['2025-07-27'],
            'email_received_timestamp': ['2025-07-27 14:30'],
            'Agent Name': ['John Doe'],
            'Handle': ['123'],
            'Avg Handle': ['5.5']
        })],
        'ACQ': [pd.DataFrame({
            'email_received_date': ['2025-07-27'],
            'email_received_timestamp': ['2025-07-27 14:30'],
            'Agent Name': ['Jane Smith'],
            'Handle': ['456']
        })]
    }


# --- ReportProcessor Tests ---
def test_report_processor_initialization(sample_config):
    """Test ReportProcessor initialization"""
    processor = ReportProcessor(sample_config, debug=True)
    
    assert processor.config == sample_config
    assert processor.last_processed_time is None
    assert processor.daily_data_cache == {}
    assert hasattr(processor, 'email_fetcher')
    assert hasattr(processor, 'transformer')
    assert hasattr(processor, 'excel_writer')


def test_process_hourly_with_data(report_processor, mock_components):
    """Test hourly processing with data available"""
    # Setup mock returns
    sample_data = create_sample_data()
    mock_components['transformer'].transform.return_value = sample_data
    mock_components['excel_writer'].write_incremental.return_value = '/path/to/report.xlsx'
    
    target_time = datetime(2025, 7, 27, 14, 0, 0)
    result = report_processor.process_hourly(target_time)
    
    # Verify calls
    mock_components['email_fetcher'].fetch.assert_called_once_with('2025-07-27')
    mock_components['transformer'].transform.assert_called_once_with('2025-07-27')
    mock_components['excel_writer'].write_incremental.assert_called_once_with(
        sample_data, '2025-07-27', '2025-07-27_14'
    )
    
    # Verify results
    assert result == sample_data
    assert report_processor.last_processed_time == target_time
    assert '2025-07-27' in report_processor.daily_data_cache


def test_process_hourly_no_data(report_processor, mock_components):
    """Test hourly processing with no data"""
    mock_components['transformer'].transform.return_value = {}
    
    result = report_processor.process_hourly()
    
    # Verify calls
    mock_components['email_fetcher'].fetch.assert_called_once()
    mock_components['transformer'].transform.assert_called_once()
    mock_components['excel_writer'].write_incremental.assert_not_called()
    
    assert result == {}


def test_generate_on_demand_report(report_processor, mock_components):
    """Test on-demand report generation"""
    # Setup cache with data
    sample_data = create_sample_data()
    report_processor.daily_data_cache['2025-07-27'] = sample_data
    
    mock_components['excel_writer'].write_custom.return_value = '/path/to/ondemand.xlsx'
    
    result = report_processor.generate_on_demand_report('2025-07-27')
    
    # Verify call
    mock_components['excel_writer'].write_custom.assert_called_once()
    args = mock_components['excel_writer'].write_custom.call_args
    assert args[0][0] == sample_data  # First argument should be the data
    assert 'ondemand_2025-07-27_' in args[0][1]  # Second argument should be filename
    
    assert result == '/path/to/ondemand.xlsx'


def test_generate_on_demand_report_filtered(report_processor, mock_components):
    """Test on-demand report with specific report types"""
    sample_data = create_sample_data()
    report_processor.daily_data_cache['2025-07-27'] = sample_data
    
    mock_components['excel_writer'].write_custom.return_value = '/path/to/filtered.xlsx'
    
    result = report_processor.generate_on_demand_report('2025-07-27', ['IB_Calls'])
    
    # Verify filtered data was passed
    mock_components['excel_writer'].write_custom.assert_called_once()
    args = mock_components['excel_writer'].write_custom.call_args
    filtered_data = args[0][0]
    assert 'IB_Calls' in filtered_data
    assert 'ACQ' not in filtered_data


def test_generate_end_of_day_summary(report_processor, mock_components):
    """Test end-of-day summary generation"""
    sample_data = create_sample_data()
    report_processor.daily_data_cache['2025-07-27'] = sample_data
    
    mock_components['excel_writer'].write_summary.return_value = '/path/to/summary.xlsx'
    
    result = report_processor.generate_end_of_day_summary('2025-07-27')
    
    # Verify call
    mock_components['excel_writer'].write_summary.assert_called_once()
    args = mock_components['excel_writer'].write_summary.call_args
    enhanced_data = args[0][0]
    
    # Check that metadata was added
    assert 'Report_Metadata' in enhanced_data
    assert 'IB_Calls' in enhanced_data
    assert 'ACQ' in enhanced_data
    
    # Verify cache was cleared
    assert '2025-07-27' not in report_processor.daily_data_cache
    
    assert result == '/path/to/summary.xlsx'


def test_update_daily_cache(report_processor):
    """Test daily cache update functionality"""
    sample_data = create_sample_data()
    
    # First update
    report_processor._update_daily_cache('2025-07-27', sample_data)
    assert '2025-07-27' in report_processor.daily_data_cache
    assert len(report_processor.daily_data_cache['2025-07-27']['IB_Calls']) == 1
    
    # Second update (should append)
    report_processor._update_daily_cache('2025-07-27', sample_data)
    assert len(report_processor.daily_data_cache['2025-07-27']['IB_Calls']) == 2


def test_get_daily_data_from_cache(report_processor):
    """Test getting daily data from cache"""
    sample_data = create_sample_data()
    report_processor.daily_data_cache['2025-07-27'] = sample_data
    
    result = report_processor._get_daily_data('2025-07-27')
    assert result == sample_data


def test_get_daily_data_reprocess(report_processor, mock_components):
    """Test getting daily data when not in cache (reprocessing)"""
    sample_data = create_sample_data()
    mock_components['transformer'].transform.return_value = sample_data
    
    result = report_processor._get_daily_data('2025-07-27')
    
    mock_components['transformer'].transform.assert_called_once_with('2025-07-27')
    assert result == sample_data


def test_add_summary_statistics(report_processor):
    """Test adding summary statistics to data"""
    sample_data = create_sample_data()
    
    enhanced = report_processor._add_summary_statistics(sample_data, '2025-07-27')
    
    assert 'Report_Metadata' in enhanced
    assert 'IB_Calls' in enhanced
    assert 'ACQ' in enhanced
    
    metadata_df = enhanced['Report_Metadata'][0]
    assert 'Metric' in metadata_df.columns
    assert 'Value' in metadata_df.columns
    assert len(metadata_df) == 4  # Should have 4 metadata rows


# --- Integration Tests ---
@pytest.mark.integration
def test_hourly_processing_integration(sample_config, temp_dirs):
    """Integration test for hourly processing"""
    # Create test CSV files with timestamp format
    raw_dir = temp_dirs['raw']
    
    # Create files for different hours
    csv_files = [
        'IB_Calls__2025-07-27_1400.csv',
        'ACQ__2025-07-27_1400.csv',
        'IB_Calls__2025-07-27_1500.csv'
    ]
    
    for csv_file in csv_files:
        file_type = csv_file.split('__')[0]
        columns = sample_config.attachment_rules[f'{file_type}.csv']['columns']
        path = os.path.join(raw_dir, csv_file)
        create_test_csv(path, file_type, columns)
    
    # Create processor with real components
    processor = ReportProcessor(sample_config, debug=True)
    processor.transformer.raw_dir = raw_dir
    processor.transformer.archive_dir = temp_dirs['archive']
    processor.excel_writer.output_dir = temp_dirs['output']
    
    # Mock the email fetcher (we're testing transformation and writing)
    processor.email_fetcher = Mock()
    
    # Process hour 14 (should get 2 files)
    result = processor.process_hourly(datetime(2025, 7, 27, 14, 0))
    
    # Should have processed IB_Calls and ACQ for hour 14
    assert 'IB_Calls' in result
    assert 'ACQ' in result
    assert len(result) == 2


# --- Error Handling Tests ---
def test_process_hourly_error_handling(report_processor, mock_components):
    """Test error handling in hourly processing"""
    mock_components['transformer'].transform.side_effect = Exception("Test error")
    
    result = report_processor.process_hourly()
    
    # Should return empty dict on error
    assert result == {}


def test_on_demand_report_no_data(report_processor, mock_components):
    """Test on-demand report when no data available"""
    mock_components['transformer'].transform.return_value = {}
    
    result = report_processor.generate_on_demand_report('2025-07-27')
    
    assert result is None


# --- Edge Cases ---
def test_process_hourly_specific_datetime(report_processor, mock_components):
    """Test processing for specific datetime"""
    sample_data = create_sample_data()
    mock_components['transformer'].transform.return_value = sample_data
    
    specific_time = datetime(2025, 7, 27, 15, 30, 45)  # Specific time with minutes/seconds
    result = report_processor.process_hourly(specific_time)
    
    # Should normalize to hour boundary
    expected_time = datetime(2025, 7, 27, 15, 0, 0)
    assert report_processor.last_processed_time == expected_time


def test_continuous_processing_interrupt(report_processor):
    """Test continuous processing with keyboard interrupt"""
    with patch('time.sleep') as mock_sleep:
        mock_sleep.side_effect = KeyboardInterrupt()
        
        # Should exit gracefully
        report_processor.run_continuous_processing(check_interval=1)
        
        mock_sleep.assert_called_once_with(1)


if __name__ == '__main__':
    pytest.main([__file__])
