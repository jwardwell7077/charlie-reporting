"""
Global pytest configuration and fixtures for Charlie Reporting
Modernized for Phase 2 microservices testing framework

Original conftest.py migrated to support:
- Microservices architecture testing
- Phase 1 business logic validation
- Integration testing framework
- Performance benchmarking support

Author: Jonathan Wardwell, GitHub Copilot, GPT-4o
License: MIT
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

# Add services to Python path for testing
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root / "services"))
sys.path.insert(0, str(workspace_root / "shared"))
sys.path.insert(0, str(workspace_root / "src"))  # Legacy support

# Legacy imports for backward compatibility
try:
    from config_loader import ConfigLoader
    from transformer import CSVTransformer
except ImportError:
    ConfigLoader = None
    CSVTransformer = None


@pytest.fixture(scope="session")
def workspace_root():
    """Provide the workspace root directory"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session") 
def test_data_dir(workspace_root):
    """Provide the test data directory"""
    return workspace_root / "tests" / "data"


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for tests"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture(scope='session')
def config_loader():
    """
    Legacy fixture for loading the TOML config for tests.
    Maintained for backward compatibility with existing tests.
    """
    if ConfigLoader is None:
        pytest.skip("ConfigLoader not available")
        
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.toml')
    return ConfigLoader(config_path)


@pytest.fixture
def transformer(tmp_path, config_loader):
    """
    Legacy fixture for creating a CSVTransformer with loaded config.
    Maintained for backward compatibility with existing tests.
    """
    if CSVTransformer is None:
        pytest.skip("CSVTransformer not available")
        
    # Create required directories for legacy transformer
    raw = tmp_path / 'raw'
    archive = tmp_path / 'archive'
    raw.mkdir()
    archive.mkdir()
    return CSVTransformer(config_loader, raw_dir=str(raw), archive_dir=str(archive))


# New Phase 2 fixtures for microservices testing

@pytest.fixture
def sample_csv_data():
    """Provide sample CSV data for testing"""
    return {
        'ACQ.csv': [
            {'Customer': 'Test Client 1', 'Amount': '1000', 'Status': 'Complete'},
            {'Customer': 'Test Client 2', 'Amount': '2000', 'Status': 'Pending'},
            {'Customer': 'Test Client 3', 'Amount': '1500', 'Status': 'Complete'},
        ],
        'Dials.csv': [
            {'Agent': 'Agent 1', 'Calls': '50', 'Date': '2025-07-28'},
            {'Agent': 'Agent 2', 'Calls': '45', 'Date': '2025-07-28'},
        ]
    }


@pytest.fixture
def sample_transformation_config():
    """Provide sample transformation configuration"""
    return {
        "ACQ.csv": {
            "rules": [
                {"filter_column": "Status", "filter_value": "Complete"},
                {"rename_column": {"old": "Customer", "new": "Client"}}
            ]
        },
        "Dials.csv": {
            "rules": [
                {"filter_column": "Calls", "filter_operator": ">", "filter_value": "40"}
            ]
        }
    }


@pytest.fixture
def mock_logger():
    """Provide a mock logger for testing"""
    class MockLogger:
        def __init__(self):
            self.messages = []
            
        def info(self, msg, **kwargs):
            self.messages.append(('INFO', msg, kwargs))
            
        def warning(self, msg, **kwargs):
            self.messages.append(('WARNING', msg, kwargs))
            
        def error(self, msg, **kwargs):
            self.messages.append(('ERROR', msg, kwargs))
            
        def debug(self, msg, **kwargs):
            self.messages.append(('DEBUG', msg, kwargs))
            
        def get_messages(self, level=None):
            if level:
                return [m for m in self.messages if m[0] == level]
            return self.messages
    
    return MockLogger()


@pytest.fixture
def performance_thresholds():
    """Provide performance testing thresholds"""
    return {
        'csv_processing_seconds': 30,
        'excel_generation_seconds': 120,
        'memory_usage_mb': 100,
        'api_response_seconds': 2
    }


# Test markers for organization
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
