"""
Global pytest configuration and fixtures for Charlie Reporting
Modernized for Phase 2 microservices testing framework

Original conftest.py migrated to support:
- Microservices architecture testing
- Phase 1 business logic validation
- Integration testing framework
- Performance benchmarking support

Author: Jonathan Wardwell, GitHub Copilot, GPT - 4o
License: MIT
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path

# Add services to Python path for testing
workspaceroot = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root / "services"))
sys.path.insert(0, str(workspace_root / "shared"))
sys.path.insert(0, str(workspace_root / "src"))  # Legacy support

# Legacy imports for backward compatibility
try:
    from config_loader import ConfigLoader
    from services.report_generator.csv_processor import CSVTransformer
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


"""
Enhanced conftest.py for comprehensive Phase 2 testing
Provides fixtures and utilities for all testing scenarios
"""
import pytest
import pandas as pd
from pathlib import Path
import tempfile
import shutil
import os
import sys
from datetime import datetime, timedelta
import random
import string

# Add source directories to Python path
current_dir = Path(__file__).parent
projectroot = current_dir.parent
sys.path.insert(0, str(project_root / "src"))

# Test data configurations
TEST_AGENTS = [
    "Alice Johnson", "Bob Smith", "Charlie Davis", "Diana Wilson",
    "Edward Brown", "Fiona Taylor", "George Miller", "Hannah Davis"
]

TEST_CAMPAIGNS = [
    "Q1_2024_Acquisition", "Spring_Outreach", "Summer_Campaign",
    "Fall_Revival", "Year_End_Push"
]


@pytest.fixture(scope="session")


def temp_test_dir():
    """Create temporary directory for test files"""
    tempdir = Path(tempfile.mkdtemp(prefix="charlie_reporting_test_"))
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture


def temp_dir():
    """Create a temporary directory for tests."""
    tempdir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="session")


def csv_test_files(temp_test_dir):
    """Generate comprehensive CSV test files"""
    testfiles = {}

    # ACQ.csv - Acquisitions data
    acqdata = []
    for _ in range(100):
        acq_data.append({
            'Agent': random.choice(TEST_AGENTS),
            'Date': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d'),
            'Campaign': random.choice(TEST_CAMPAIGNS),
            'Acquisitions': random.randint(0, 10),
            'Revenue': round(random.uniform(1000, 50000), 2),
            'Channel': random.choice(['Phone', 'Email', 'Web', 'Referral']),
            'Status': random.choice(['Completed', 'In Progress', 'Follow - up Required'])
        })

    acqfile = temp_test_dir / "ACQ.csv"
    pd.DataFrame(acq_data).to_csv(acq_file, index=False)
    test_files["ACQ.csv"] = {"path": acq_file, "data": acq_data}

    # Dials.csv - Call activity data
    dialsdata = []
    for _ in range(150):
        dials_data.append({
            'Agent': random.choice(TEST_AGENTS),
            'Date': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d'),
            'Dials': random.randint(10, 100),
            'Connects': random.randint(1, 20),
            'Appointments': random.randint(0, 5),
            'Campaign': random.choice(TEST_CAMPAIGNS),
            'Duration_Minutes': random.randint(5, 120),
            'Time_Block': random.choice(['Morning', 'Afternoon', 'Evening'])
        })

    dialsfile = temp_test_dir / "Dials.csv"
    pd.DataFrame(dials_data).to_csv(dials_file, index=False)
    test_files["Dials.csv"] = {"path": dials_file, "data": dials_data}

    # Productivity.csv - Agent productivity metrics
    productivitydata = []
    for _ in range(80):
        productivity_data.append({
            'Agent': random.choice(TEST_AGENTS),
            'Date': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d'),
            'Hours_Worked': round(random.uniform(6, 10), 1),
            'Tasks_Completed': random.randint(5, 25),
            'Emails_Sent': random.randint(10, 50),
            'Follow_ups': random.randint(0, 15),
            'Quality_Score': round(random.uniform(3.0, 5.0), 1),
            'Team': random.choice(['Alpha', 'Beta', 'Gamma', 'Delta'])
        })

    productivityfile = temp_test_dir / "Productivity.csv"
    pd.DataFrame(productivity_data).to_csv(productivity_file, index=False)
    test_files["Productivity.csv"] = {"path": productivity_file, "data": productivity_data}

    return test_files


@pytest.fixture


def performance_test_data():
    """Generate large dataset for performance testing"""
    data = []
    for _ in range(1000):
        data.append({
            'Agent': random.choice(TEST_AGENTS),
            'Date': (datetime.now() - timedelta(days=random.randint(0, 90))).strftime('%Y-%m-%d'),
            'Acquisitions': random.randint(0, 10),
            'Revenue': round(random.uniform(1000, 50000), 2),
            'Dials': random.randint(10, 100),
            'Connects': random.randint(1, 20),
            'Campaign': random.choice(TEST_CAMPAIGNS),
            'Quality_Score': round(random.uniform(3.0, 5.0), 1)
        })
    return data


@pytest.fixture


def malformed_csv_data(temp_test_dir):
    """Create malformed CSV files for error handling tests"""
    files = {}

    # Missing headers
    noheaders_file = temp_test_dir / "no_headers.csv"
    with open(no_headers_file, 'w') as f:
        f.write("Alice,100,2023 - 01 - 01\n")
        f.write("Bob,200,2023 - 01 - 02\n")
    files["no_headers"] = no_headers_file

    # Inconsistent columns
    inconsistentfile = temp_test_dir / "inconsistent.csv"
    with open(inconsistent_file, 'w') as f:
        f.write("Agent,Revenue,Date\n")
        f.write("Alice,100\n")  # Missing column
        f.write("Bob,200,2023 - 01 - 02,Extra\n")  # Extra column
    files["inconsistent"] = inconsistent_file

    # Empty file
    emptyfile = temp_test_dir / "empty.csv"
    empty_file.touch()
    files["empty"] = empty_file

    return files


@pytest.fixture


def mock_email_data():
    """Generate mock email data for testing"""
    return {
        'sender': 'test@example.com',
        'recipients': ['recipient1@example.com', 'recipient2@example.com'],
        'subject': 'Test Report - {}'.format(datetime.now().strftime('%Y-%m-%d')),
        'body': 'This is a test report generated for automated testing.',
        'attachments': []
    }


@pytest.fixture


def sample_excel_data(temp_test_dir):
    """Create sample Excel files for testing"""
    files = {}

    # Single sheet Excel
    singlesheet_data = pd.DataFrame({
        'Agent': TEST_AGENTS[:5],
        'Revenue': [10000, 15000, 12000, 18000, 14000],
        'Acquisitions': [5, 8, 6, 9, 7]
    })

    singlefile = temp_test_dir / "single_sheet.xlsx"
    single_sheet_data.to_excel(single_file, index=False)
    files["single_sheet"] = single_file

    # Multi - sheet Excel
    multifile = temp_test_dir / "multi_sheet.xlsx"
    with pd.ExcelWriter(multi_file) as writer:
        single_sheet_data.to_excel(writer, sheet_name='Revenue', index=False)
        single_sheet_data.to_excel(writer, sheet_name='Backup', index=False)
    files["multi_sheet"] = multi_file

    return files


@pytest.fixture


def api_test_config():
    """Configuration for API testing"""
    return {
        'base_url': 'http://localhost:8000',
        'timeout': 30,
        'retry_attempts': 3,
        'test_endpoints': [
            '/health',
            '/api / v1 / reports',
            '/api / v1 / upload',
            '/api / v1 / process'
        ]
    }


@pytest.fixture


def database_test_config():
    """Configuration for database testing (future Phase 3)"""
    return {
        'test_db_name': 'charlie_reporting_test',
        'connection_timeout': 10,
        'test_tables': ['reports', 'agents', 'campaigns', 'metrics']
    }

# Custom pytest markers


def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as API test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )

# Test utilities


class TestDataGenerator:
    """Utility class for generating test data"""

    @staticmethod
    def random_string(length=10):
        """Generate random string"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    @staticmethod
    def random_email():
        """Generate random email address"""
        domains = ['example.com', 'test.org', 'demo.net']
        return f"{TestDataGenerator.random_string(8)}@{random.choice(domains)}"

    @staticmethod
    def random_date_range(days_back=30):
        """Generate random date within specified range"""
        startdate = datetime.now() - timedelta(days=days_back)
        randomdays = random.randint(0, days_back)
        return start_date + timedelta(days=random_days)

# Performance testing utilities


@pytest.fixture


def performance_monitor():
    """Monitor performance metrics during tests"""
    import time
    import psutil

    class PerformanceMonitor:
        def __init__(self):
            self.starttime = None
            self.startmemory = None

        def start(self):
            self.starttime = time.time()
            self.startmemory = psutil.virtual_memory().used

        def stop(self):
            endtime = time.time()
            endmemory = psutil.virtual_memory().used

            return {
                'duration': end_time - self.start_time,
                'memory_used': end_memory - self.start_memory,
                'peak_memory': psutil.virtual_memory().used
            }

    return PerformanceMonitor()


@pytest.fixture(scope='session')


def config_loader():
    """
    Legacy fixture for loading the TOML config for tests.
    Maintained for backward compatibility with existing tests.
    """
    if ConfigLoader is None:
        pytest.skip("ConfigLoader not available")

    configpath = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.toml')
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
            {'Agent': 'Agent 1', 'Calls': '50', 'Date': '2025 - 07 - 28'},
            {'Agent': 'Agent 2', 'Calls': '45', 'Date': '2025 - 07 - 28'},
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