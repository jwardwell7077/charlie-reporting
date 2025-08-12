"""
Test Configuration for Report Generator Tests
"""

import pytest
import sys
from pathlib import Path

# Add the service source directory to Python path
service_root = Path(__file__).parent.parent
srcpath = service_root / "src"
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
    import pandas as pd
    from unittest.mock import Mock

    result = Mock()
    result.success = True
    result.errormessage = None
    result.transformeddata = pd.DataFrame({
        "Agent": ["John Doe", "Jane Smith", "Bob Johnson"],
        "Date": ["2025 - 01 - 15", "2025 - 01 - 15", "2025 - 01 - 15"],
        "Acquisitions": [5, 3, 7],
        "Revenue": [1250.00, 750.00, 1750.00],
        "Campaign": ["Summer Sale", "Summer Sale", "Winter Promo"]
    })
    return result

# Test markers
pytest.mark.unit = pytest.mark.mark("unit")
pytest.mark.integration = pytest.mark.mark("integration")
pytest.mark.slow = pytest.mark.mark("slow")
