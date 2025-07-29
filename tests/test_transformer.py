"""
test_transformer.py
------------------
Tests for the CSVTransformer class in transformer.py including enhanced real-time processing.

Author: Jonathan Wardwell, Copilot, GPT-4o
License: MIT
"""

import os
import shutil
import pandas as pd
import pytest
from datetime import datetime
from services.report_generator.csv_processor import CSVTransformer

# --- Fixtures ---
@pytest.fixture
def sample_config():
    """Mock config matching the actual config.toml"""
    class DummyConfig:
        @property
        def attachment_rules(self):
            # This matches EXACTLY what's in config/config.toml
            return {
                'IB_Calls.csv': {'columns': ['Agent Name', 'Handle', 'Avg Handle']},
                'QCBs.csv': {'columns': ['Agent Name', 'Handle']},
                'Dials.csv': {'columns': ['Agent Name', 'Handle', 'Avg Handle', 'Avg Talk', 'Avg Hold']},
                'Productivity.csv': {'columns': ['Agent Name', 'Logged In', 'On Queue', 'Idle', 'Off Queue', 'Interacting']},
                'Campaign_Interactions.csv': {'columns': ['Date', 'Initial Direction', 'First Queue']},
                'ACQ.csv': {'columns': ['Agent Name', 'Handle']},
                'RESC.csv': {'columns': ['Agent Name', 'Handle']},
            }
    return DummyConfig()

@pytest.fixture
def raw_and_archive_dirs(tmp_path):
    """Create temporary raw and archive directories"""
    raw = tmp_path / 'raw'
    archive = tmp_path / 'archive'
    raw.mkdir()
    archive.mkdir()
    return str(raw), str(archive)

# --- Helper Functions ---
def write_csv(path, header, rows):
    """Write test CSV data to file"""
    df = pd.DataFrame(rows, columns=header)
    df.to_csv(path, index=False)

# --- Basic Tests ---
def test_basic_transformation(sample_config, raw_and_archive_dirs):
    """Test basic CSV transformation and archiving"""
    raw_dir, archive_dir = raw_and_archive_dirs
    
    # Create test CSV
    csv_path = os.path.join(raw_dir, 'ACQ__2025-07-27.csv')
    write_csv(csv_path, ['Agent Name', 'Handle', 'Extra'], [['John', '5', 'ignore']])
    
    # Run transformer
    transformer = CSVTransformer(sample_config, raw_dir=raw_dir, archive_dir=archive_dir)
    result = transformer.transform('2025-07-27')
    
    # Verify results
    assert 'ACQ' in result
    df = result['ACQ'][0]
    assert list(df.columns) == ['email_received_date', 'email_received_timestamp', 'Agent Name', 'Handle']
    assert df.iloc[0]['email_received_date'] == '2025-07-27'
    
    # Verify file was archived
    assert not os.path.exists(csv_path)
    assert os.path.exists(os.path.join(archive_dir, 'ACQ__2025-07-27.csv'))

# --- Enhanced Real-time Processing Tests ---
def test_hourly_transformation(sample_config, raw_and_archive_dirs):
    """Test transformation for specific hour"""
    raw_dir, archive_dir = raw_and_archive_dirs
    
    # Create test CSV files for different hours
    csv_14 = os.path.join(raw_dir, 'IB_Calls__2025-07-27_1400.csv')
    csv_15 = os.path.join(raw_dir, 'IB_Calls__2025-07-27_1500.csv')
    csv_other_day = os.path.join(raw_dir, 'IB_Calls__2025-07-26_1400.csv')
    
    test_data = [['John Doe', '123', '5.5']]
    
    write_csv(csv_14, ['Agent Name', 'Handle', 'Avg Handle'], test_data)
    write_csv(csv_15, ['Agent Name', 'Handle', 'Avg Handle'], test_data)
    write_csv(csv_other_day, ['Agent Name', 'Handle', 'Avg Handle'], test_data)
    
    # Run transformer for hour 14
    transformer = CSVTransformer(sample_config, raw_dir=raw_dir, archive_dir=archive_dir)
    result = transformer.transform_hourly('2025-07-27', 14)
    
    # Should only process hour 14 file
    assert 'IB_Calls' in result
    assert len(result['IB_Calls']) == 1  # Only one file processed
    
    # Verify correct file was processed (14:00)
    assert not os.path.exists(csv_14)  # Should be archived
    assert os.path.exists(csv_15)      # Should still exist
    assert os.path.exists(csv_other_day)  # Should still exist

def test_transform_with_hour_filter(sample_config, raw_and_archive_dirs):
    """Test transform method with hour filter"""
    raw_dir, archive_dir = raw_and_archive_dirs
    
    # Create test files
    csv_14 = os.path.join(raw_dir, 'ACQ__2025-07-27_1430.csv')
    csv_15 = os.path.join(raw_dir, 'ACQ__2025-07-27_1530.csv')
    
    test_data = [['Jane Smith', '456']]
    
    write_csv(csv_14, ['Agent Name', 'Handle'], test_data)
    write_csv(csv_15, ['Agent Name', 'Handle'], test_data)
    
    # Run transformer with hour filter
    transformer = CSVTransformer(sample_config, raw_dir=raw_dir, archive_dir=archive_dir)
    result = transformer.transform('2025-07-27', hour_filter='14')
    
    # Should only process hour 14 file
    assert 'ACQ' in result
    assert len(result['ACQ']) == 1
    
    # Verify timestamp extraction
    df = result['ACQ'][0]
    assert df.iloc[0]['email_received_timestamp'] == '2025-07-27 14:30'

def test_transform_recent(sample_config, raw_and_archive_dirs):
    """Test transform_recent method"""
    raw_dir, archive_dir = raw_and_archive_dirs
    
    # Create test files with different timestamps
    current_time = datetime.now()
    recent_time = current_time.replace(minute=0, second=0, microsecond=0)
    old_time = recent_time.replace(hour=recent_time.hour - 2)
    
    recent_str = recent_time.strftime('%Y-%m-%d_%H%M')
    old_str = old_time.strftime('%Y-%m-%d_%H%M')
    
    csv_recent = os.path.join(raw_dir, f'Productivity__{recent_str}.csv')
    csv_old = os.path.join(raw_dir, f'Productivity__{old_str}.csv')
    
    test_data = [['Agent A', '8:00', '7:30', '0:30', '0:00', '2:15']]
    columns = ['Agent Name', 'Logged In', 'On Queue', 'Idle', 'Off Queue', 'Interacting']
    
    write_csv(csv_recent, columns, test_data)
    write_csv(csv_old, columns, test_data)
    
    # Run transformer for recent files (last 1 hour)
    transformer = CSVTransformer(sample_config, raw_dir=raw_dir, archive_dir=archive_dir)
    result = transformer.transform_recent(hours_back=1)
    
    # Should only process recent file
    assert 'Productivity' in result
    assert len(result['Productivity']) == 1
    
    # Verify only recent file was archived
    assert not os.path.exists(csv_recent)  # Should be archived
    assert os.path.exists(csv_old)         # Should still exist

def test_timestamp_extraction_from_filename(sample_config, raw_and_archive_dirs):
    """Test timestamp extraction from filename"""
    raw_dir, archive_dir = raw_and_archive_dirs
    
    transformer = CSVTransformer(sample_config, raw_dir=raw_dir, archive_dir=archive_dir)
    
    # Test various filename formats
    test_cases = [
        ('IB_Calls__2025-07-27_1430.csv', '2025-07-27', '2025-07-27 14:30'),
        ('ACQ__2025-12-31_2359.csv', '2025-12-31', '2025-12-31 23:59'),
        ('Invalid_filename.csv', '2025-07-27', '2025-07-27 00:00'),  # Fallback
    ]
    
    for filename, date_str, expected_timestamp in test_cases:
        result = transformer._extract_timestamp_from_filename(filename, date_str)
        assert result == expected_timestamp

def test_datetime_extraction_from_filename(sample_config, raw_and_archive_dirs):
    """Test datetime extraction from filename"""
    raw_dir, archive_dir = raw_and_archive_dirs
    
    transformer = CSVTransformer(sample_config, raw_dir=raw_dir, archive_dir=archive_dir)
    
    # Test valid filename
    filename = 'Dials__2025-07-27_1445.csv'
    result = transformer._extract_datetime_from_filename(filename)
    
    expected = datetime(2025, 7, 27, 14, 45)
    assert result == expected
    
    # Test invalid filename
    invalid_filename = 'invalid_format.csv'
    result = transformer._extract_datetime_from_filename(invalid_filename)
    assert result is None

def test_timestamp_columns_added(sample_config, raw_and_archive_dirs):
    """Test that timestamp columns are properly added"""
    raw_dir, archive_dir = raw_and_archive_dirs
    
    # Create test CSV with timestamp in filename
    csv_path = os.path.join(raw_dir, 'Campaign_Interactions__2025-07-27_0900.csv')
    test_data = [['2025-07-27', 'Inbound', 'Support']]
    write_csv(csv_path, ['Date', 'Initial Direction', 'First Queue'], test_data)
    
    # Run transformer
    transformer = CSVTransformer(sample_config, raw_dir=raw_dir, archive_dir=archive_dir)
    result = transformer.transform('2025-07-27')
    
    # Verify timestamp columns were added
    df = result['Campaign_Interactions'][0]
    assert 'email_received_date' in df.columns
    assert 'email_received_timestamp' in df.columns
    assert df.iloc[0]['email_received_date'] == '2025-07-27'
    assert df.iloc[0]['email_received_timestamp'] == '2025-07-27 09:00'

# --- Comprehensive Tests for All Config.toml File Types ---
@pytest.mark.parametrize("file_type,columns", [
    ("IB_Calls", ["Agent Name", "Handle", "Avg Handle"]),
    ("QCBs", ["Agent Name", "Handle"]),
    ("Dials", ["Agent Name", "Handle", "Avg Handle", "Avg Talk", "Avg Hold"]),
    ("Productivity", ["Agent Name", "Logged In", "On Queue", "Idle", "Off Queue", "Interacting"]),
    ("Campaign_Interactions", ["Date", "Initial Direction", "First Queue"]),
    ("ACQ", ["Agent Name", "Handle"]),
    ("RESC", ["Agent Name", "Handle"]),
])
def test_all_config_file_types(sample_config, raw_and_archive_dirs, file_type, columns):
    """Test transformation for all file types defined in config.toml"""
    raw_dir, archive_dir = raw_and_archive_dirs
    
    # Create test data with all required columns plus extras
    test_data = {col: [f"test_{i}"] for i, col in enumerate(columns)}
    test_data["Extra_Column"] = ["should_be_removed"]
    
    # Create test CSV
    csv_path = os.path.join(raw_dir, f'{file_type}__2025-07-27.csv')
    write_csv(csv_path, list(test_data.keys()), [list(test_data.values())])
    
    # Run transformer
    transformer = CSVTransformer(sample_config, raw_dir=raw_dir, archive_dir=archive_dir)
    result = transformer.transform('2025-07-27')
    
    # Verify results
    assert file_type in result, f"Missing sheet for {file_type}"
    df = result[file_type][0]
    expected_cols = ['email_received_date', 'email_received_timestamp'] + columns
    assert list(df.columns) == expected_cols, f"Column mismatch for {file_type}"
    assert df.iloc[0]['email_received_date'] == '2025-07-27'
    
    # Verify file was archived
    assert not os.path.exists(csv_path)
    assert os.path.exists(os.path.join(archive_dir, f'{file_type}__2025-07-27.csv'))

def test_missing_columns_error(sample_config, raw_and_archive_dirs, caplog):
    """Test handling of files with missing required columns"""
    raw_dir, archive_dir = raw_and_archive_dirs
    
    # Create CSV missing required columns (Dials needs 5 columns, only provide 2)
    csv_path = os.path.join(raw_dir, 'Dials__2025-07-27.csv')
    write_csv(csv_path, ['Agent Name', 'Handle'], [['John', '5']])
    
    transformer = CSVTransformer(sample_config, raw_dir=raw_dir, archive_dir=archive_dir)
    
    with caplog.at_level('ERROR'):
        result = transformer.transform('2025-07-27')
    
    # Should skip the file and log error
    assert result == {}
    assert 'Missing columns' in caplog.text
    assert os.path.exists(csv_path)  # File not archived due to error

def test_no_matching_rule(sample_config, raw_and_archive_dirs, caplog):
    """Test handling of files with no matching rules"""
    raw_dir, archive_dir = raw_and_archive_dirs
    
    csv_path = os.path.join(raw_dir, 'Unknown_File__2025-07-27.csv')
    write_csv(csv_path, ['Col1', 'Col2'], [['data1', 'data2']])
    
    transformer = CSVTransformer(sample_config, raw_dir=raw_dir, archive_dir=archive_dir)
    
    with caplog.at_level('WARNING'):
        result = transformer.transform('2025-07-27')
    
    assert result == {}
    assert 'No matching rule' in caplog.text
    assert os.path.exists(csv_path)  # File not processed

def test_date_filtering(sample_config, raw_and_archive_dirs):
    """Test that files with wrong dates are skipped"""
    raw_dir, archive_dir = raw_and_archive_dirs
    
    # Create files with different dates
    csv_today = os.path.join(raw_dir, 'ACQ__2025-07-27.csv')
    csv_yesterday = os.path.join(raw_dir, 'ACQ__2025-07-26.csv')
    
    write_csv(csv_today, ['Agent Name', 'Handle'], [['John', '5']])
    write_csv(csv_yesterday, ['Agent Name', 'Handle'], [['Jane', '3']])
    
    transformer = CSVTransformer(sample_config, raw_dir=raw_dir, archive_dir=archive_dir)
    result = transformer.transform('2025-07-27')
    
    # Only today's file should be processed
    assert 'ACQ' in result
    assert len(result['ACQ']) == 1
    
    # Only today's file should be archived
    assert not os.path.exists(csv_today)
    assert os.path.exists(csv_yesterday)  # Yesterday's file remains

def test_multiple_files_same_type(sample_config, raw_and_archive_dirs):
    """Test processing multiple files of the same type"""
    raw_dir, archive_dir = raw_and_archive_dirs
    
    # Create multiple ACQ files
    csv1 = os.path.join(raw_dir, 'ACQ_batch1__2025-07-27.csv')
    csv2 = os.path.join(raw_dir, 'ACQ_batch2__2025-07-27.csv')
    
    write_csv(csv1, ['Agent Name', 'Handle'], [['John', '5']])
    write_csv(csv2, ['Agent Name', 'Handle'], [['Jane', '3']])
    
    transformer = CSVTransformer(sample_config, raw_dir=raw_dir, archive_dir=archive_dir)
    result = transformer.transform('2025-07-27')
    
    # Should have one sheet with multiple DataFrames
    assert 'ACQ' in result
    assert len(result['ACQ']) == 2
    
    # Both files should be archived
    assert not os.path.exists(csv1)
    assert not os.path.exists(csv2)

def test_corrupt_csv_handling(sample_config, raw_and_archive_dirs, caplog):
    """Test handling of corrupt/malformed CSV files"""
    raw_dir, archive_dir = raw_and_archive_dirs
    
    csv_path = os.path.join(raw_dir, 'ACQ__2025-07-27.csv')
    
    # Write corrupt data
    with open(csv_path, 'w') as f:
        f.write('Agent Name,Handle\n"Unclosed quote,5\nBad,data\x00\x01')
    
    transformer = CSVTransformer(sample_config, raw_dir=raw_dir, archive_dir=archive_dir)
    
    with caplog.at_level('ERROR'):
        result = transformer.transform('2025-07-27')
    
    # Should handle gracefully
    assert result == {}
    assert 'Error processing' in caplog.text
    assert os.path.exists(csv_path)  # File not archived due to error
