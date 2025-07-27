# Directory structure for pytest-based unit tests
# 
# daily_report_automation/
# ├── src/
# ├── config/
# └── tests/
#     ├── data/                        # sample CSVs and YAMLs for test fixtures
#     │   ├── example_IB_Calls__2025-07-11.csv
#     │   └── columns_config.yaml       # copy or minimal stub from config/
#     ├── conftest.py                  # pytest fixtures
#     ├── test_utils.py                # tests for utils.py
#     ├── test_config_loader.py        # tests for config_loader.py
#     ├── test_email_fetcher.py        # tests for email_fetcher.py (mocked Outlook)
#     ├── test_transformer.py          # tests for transformer.py
#     ├── test_excel_writer.py         # tests for excel_writer.py
#     └── test_archiver.py             # tests for archiver.py


# conftest.py
# Pytest fixtures for the reporting pipeline tests.

"""
conftest.py
-----------
Pytest fixtures for the reporting pipeline tests.

Author: Jonathan Wardwell, Copilot, GPT-4o
License: MIT
"""

import os
import pytest
from config_loader import ConfigLoader
from transformer import CSVTransformer

@pytest.fixture(scope='session')
def config_loader():
    """
    Fixture for loading the TOML config for tests.
    Returns:
        ConfigLoader: Loaded config object.
    """
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.toml')
    return ConfigLoader(config_path)

@pytest.fixture
def transformer(tmp_path, config_loader):
    """
    Fixture for creating a CSVTransformer with loaded config.
    Args:
        config_loader (ConfigLoader): Loaded config fixture.
    Returns:
        CSVTransformer: Transformer instance.
    """
    raw = tmp_path / 'raw'
    archive = tmp_path / 'archive'
    raw.mkdir()
    archive.mkdir()
    return CSVTransformer(config_loader, raw_dir=str(raw), archive_dir=str(archive))
