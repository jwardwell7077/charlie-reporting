import os
import sys
import shutil
import pandas as pd
import pytest

# Ensure src directory is on path
CURRENT_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..', 'src'))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from config_loader import ConfigLoader
from transformer import CSVTransformer


test_yaml = os.path.abspath(os.path.join(CURRENT_DIR, 'data', 'columns_config.yaml'))

@pytest.fixture

def transformer(tmp_path):
    # Prepare temporary raw and archive directories
    raw = tmp_path / 'raw'
    archive = tmp_path / 'archive'
    raw.mkdir()
    archive.mkdir()

    # Load config
    cfg = ConfigLoader(test_yaml)
    return CSVTransformer(cfg, raw_dir=str(raw), archive_dir=str(archive))


def create_sample_csv(dir_path, filename, data):
    path = os.path.join(dir_path, filename)
    pd.DataFrame(data).to_csv(path, index=False)
    return path


def test_transform_single_file(transformer, tmp_path):
    date_str = '2025-07-11'
    # Create a sample CSV matching 'IB Calls.csv' rule with range G:I
    # For simplicity, create 10 columns labeled A-J
    columns = [chr(c) for c in range(ord('A'), ord('K'))]
    data = {col: [1, 2] for col in columns}

    filename = f"IB Calls__{date_str}.csv"
    raw_dir = transformer.raw_dir
    create_sample_csv(raw_dir, filename, data)

    # Run transformation
    result = transformer.transform(date_str)

    # Verify sheet key exists
    assert 'IB Calls' in result
    dfs = result['IB Calls']
    assert isinstance(dfs, list) and len(dfs) == 1

    df_out = dfs[0]
    # Range G:I corresponds to columns F[6], G[7], H[8] zero-based indexes 6-8 inclusive => cols G,H,I
    expected_cols = columns[6:9]
    # plus email_received_date at front
    assert df_out.columns[0] == 'email_received_date'
    assert list(df_out.columns[1:]) == expected_cols
    # Check date column values
    assert all(df_out['email_received_date'] == date_str)

    # Check that original file was archived
    archived_files = os.listdir(transformer.archive_dir)
    assert filename in archived_files
    # Raw directory should be empty
    assert not os.listdir(raw_dir)


def test_skip_non_matching_date(transformer, tmp_path):
    # Create CSV with different date
    create_sample_csv(transformer.raw_dir, 'IB Calls__2025-07-10.csv', {'A': [1]})
    result = transformer.transform('2025-07-11')
    assert result == {}
    # File should remain in raw_dir since date didn't match
    assert 'IB Calls__2025-07-10.csv' in os.listdir(transformer.raw_dir)


def test_no_range_in_rule(transformer, tmp_path, config_loader):
    # Add a rule without 'range'
    transformer.config._cfg['attachments']['NoRange.csv'] = {}
    # Create matching file
    date_str = '2025-07-11'
    create_sample_csv(transformer.raw_dir, f'NoRange__{date_str}.csv', {'A': [1]})
    # Should skip processing but not crash
    result = transformer.transform(date_str)
    assert result == {}
    # File remains since not processed
    assert f'NoRange__{date_str}.csv' in os.listdir(transformer.raw_dir)
