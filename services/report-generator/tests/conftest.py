"""Test Configuration for Report Generator Tests
"""

import sys
from pathlib import Path

import pytest

# Add the service source directory to Python path
service_root = Path(__file__).parent.parent
src_path = service_root / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")


def service_root_path():
    """Provides the service root directory path"""
    return service_root


@pytest.fixture(scope="session")


def test_data_path():
    """Provides the test data directory path"""
    return Path(__file__).parent / "data"


@pytest.fixture


def mock_csv_data():
    """Sample CSV data for testing"""
    return """Agent,Date,Acquisitions,Revenue,Campaign


John Doe,2025 - 01 - 15,5,1250.00,Summer Sale
Jane Smith,2025 - 01 - 15,3,750.00,Summer Sale
Bob Johnson,2025 - 01 - 15,7,1750.00,Winter Promo"""


@pytest.fixture


def mock_transformation_result():
    """Mock transformation result for testing"""
    from unittest.mock import Mock

    import pandas as pd

    result = Mock()
    result.success = True
    result.errormessage = None  # legacy attribute name retained if used elsewhere
    result.transformeddata = pd.DataFrame({  # legacy attribute name retained
        "Agent": ["John Doe", "Jane Smith", "Bob Johnson"],
        "Date": ["2025 - 01 - 15", "2025 - 01 - 15", "2025 - 01 - 15"],
        "Acquisitions": [5, 3, 7],
        "Revenue": [1250.00, 750.00, 1750.00],
        "Campaign": ["Summer Sale", "Summer Sale", "Winter Promo"]
    })
    return result

# To use custom markers (unit, integration, slow), declare them in pytest.ini or pyproject.toml
# Example in pyproject.toml under [tool.pytest.ini_options]:
"""
markers = [
    "unit: unit level tests",
    "integration: integration tests",
    "slow: slow running tests"
]
"""
