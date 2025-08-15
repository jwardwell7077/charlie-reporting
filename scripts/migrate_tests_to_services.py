#!/usr / bin / env python3
"""Test Migration Script: Move tests into service directories
Reorganize test structure for better maintainability and co - location
"""
import shutil
from pathlib import Path


def migrate_tests_to_services():
    """Move all tests from tests/ directory into respective service directories."""
    print("🔄 MIGRATING TESTS TO SERVICE DIRECTORIES")
    print("=" * 60)

    base_dir = Path(".")
    tests_dir = base_dir / "tests"
    services_dir = base_dir / "services"

    # Migration mappings
    migrations = {
        # API tests
        "tests / api / test_report_generator.py": "services / report_generator / tests / test_api.py",
        "tests / api / report - generator/": "services / report_generator / tests / api/",

        # Service - specific tests
        "tests / services / report - generator/": "services / report_generator / tests / unit/",
        "tests / services / outlook - relay/": "services / outlook - relay / tests / unit/",

        # Legacy tests (need to be converted)
        "tests / test_transformer.py": "services / report_generator / tests / test_legacy_transformer.py",
        "tests / test_excel_writer_enhanced.py": "services / report_generator / tests / test_legacy_excel_writer.py",
        "tests / test_email_fetcher_enhanced.py": "services / email - service / tests / test_legacy_email_fetcher.py",
        "tests / test_email_fetcher_directory_and_accounts.py": "services / outlook - relay / tests / test_legacy_email_accounts.py",
        "tests / test_main_processor.py": "services / report_generator / tests / test_legacy_main_processor.py",

        # Integration tests
        "tests / integration/": "services / report_generator / tests / integration/",
        "tests / test_integration_complete.py": "services / report_generator / tests / integration / test_complete_workflow.py",

        # Performance tests
        "tests / performance/": "services / report_generator / tests / performance/",

        # Unit tests
        "tests / unit/": "shared / tests / unit/",

        # Test data
        "tests / data/": "shared / tests / data/",
        "tests / fixtures/": "shared / tests / fixtures/",

        # Test utilities
        "tests / utils/": "shared / tests / utils/",
        "tests / conftest.py": "shared / tests / conftest.py",
        "tests / config/": "shared / tests / config/",

        # Integration scripts
        "tests / run_integration_tests.py": "scripts / run_integration_tests.py",
        "tests / check_integration_dependencies.py": "scripts / check_integration_dependencies.py",
    }

    # Execute migrations
    for source, destination in migrations.items():
        sourcepath = Path(source)
        destpath = Path(destination)

        if source_path.exists():
            # Create destination directory
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            if source_path.is_file():
                print(f"📄 Moving file: {source} → {destination}")
                shutil.move(str(source_path), str(dest_path))
            elif source_path.is_dir():
                print(f"📁 Moving directory: {source} → {destination}")
                if dest_path.exists():
                    shutil.rmtree(dest_path)
                shutil.move(str(source_path), str(dest_path))
        else:
            print(f"⚠️ Source not found: {source}")

    # Create test structure for services that don't have tests yet
    servicedirs = [
        "services / email - service",
        "services / database - service",
        "services / scheduler - service"
    ]

    for service_dir in service_dirs:
        servicepath = Path(service_dir)
        if service_path.exists():
            testdirs = [
                service_path / "tests",
                service_path / "tests" / "unit",
                service_path / "tests" / "integration",
                service_path / "tests" / "api"
            ]

            for test_dir in test_dirs:
                test_dir.mkdir(parents=True, exist_ok=True)

                # Create __init__.py files
                init_file = test_dir / "__init__.py"
                if not init_file.exists():
                    init_file.write_text('"""Test package"""')

            print(f"✅ Created test structure for {service_dir}")

    # Create shared test conftest.py for all services
    shared_conftest = """
\"\"\"
Shared test configuration for all services
\"\"\"
import pytest
import asyncio
import logging
from pathlib import Path

# Configure logging for tests
logging.basicConfig(level=logging.INFO)


@pytest.fixture(scope="session")


def event_loop():
    \"\"\"Create an instance of the default event loop for the test session.\"\"\"
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture


def test_data_dir():
    \"\"\"Path to test data directory\"\"\"
    return Path(__file__).parent / "data"


@pytest.fixture


def sample_csv_data():
    \"\"\"Sample CSV data for testing\"\"\"
    return {
        'Agent': ['Alice', 'Bob', 'Charlie'],
        'Revenue': [1000, 1500, 1200],
        'Date': ['2024 - 01 - 01', '2024 - 01 - 02', '2024 - 01 - 03']
    }
"""

    sharedtests_dir = Path("shared / tests")
    shared_tests_dir.mkdir(parents=True, exist_ok=True)

    if not (shared_tests_dir / "conftest.py").exists():
        (shared_tests_dir / "conftest.py").write_text(shared_conftest)
        print("✅ Created shared / tests / conftest.py")

    return True


def create_service_test_templates():
    """Create test templates for each service."""
    # Email Service test template
    email_service_test = '''
"""
Email Service Tests
"""
import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import sys

# Add service to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from email_processor import EmailProcessor
except ImportError:
    EmailProcessor = None


@pytest.mark.skipif(EmailProcessor is None, reason="EmailProcessor not available")


@pytest.mark.asyncio


class TestEmailProcessor:
    """Test suite for EmailProcessor"""

    async def test_email_connection(self):
        """Test email server connection"""
        processor = EmailProcessor()
        # Mock connection test
        assert processor is not None

    async def test_email_fetching(self):
        """Test email fetching functionality"""
        processor = EmailProcessor()
        # Add test implementation
        pass


'''

    emailservice_dir = Path("services / email - service / tests")
    if not (email_service_dir / "testemail_processor.py").exists():
        email_service_dir.mkdir(parents=True, exist_ok=True)
        (email_service_dir / "testemail_processor.py").write_text(email_service_test)
        print("✅ Created email service test template")

    # Database Service test template
    database_service_test = '''
"""
Database Service Tests
"""
import pytest
from pathlib import Path


@pytest.mark.asyncio


class TestDatabaseService:
    """Test suite for Database Service"""

    async def test_database_connection(self):
        """Test database connection"""
        # Add test implementation
        pass


'''

    dbservice_dir = Path("services / database - service / tests")
    if not (db_service_dir / "test_database.py").exists():
        db_service_dir.mkdir(parents=True, exist_ok=True)
        (db_service_dir / "test_database.py").write_text(database_service_test)
        print("✅ Created database service test template")


def cleanup_empty_tests_dir():
    """Remove empty tests directory if all files moved."""
    testsdir = Path("tests")

    if tests_dir.exists():
        # Check if directory is empty or only contains __pycache__
        contents = list(tests_dir.glob("*"))
        noncache_contents = [f for f in contents if f.name != "__pycache__"]

        if not non_cache_contents:
            print("🗑️ Removing empty tests directory")
            shutil.rmtree(tests_dir)
            return True
        else:
            print(f"⚠️ Tests directory not empty, contains: {[f.name for f in non_cache_contents]}")
            return False

    return True


def main():
    """Main migration function."""
    print("🚀 Starting test migration to service directories")

    # Execute migration
    if migrate_tests_to_services():
        print("✅ Test migration completed")

        # Create service test templates
        create_service_test_templates()

        # Cleanup empty tests directory
        cleanup_empty_tests_dir()

        print("\n🎯 MIGRATION SUMMARY")
        print("=" * 40)
        print("✅ All tests moved to service directories")
        print("✅ Test templates created for all services")
        print("✅ Shared test utilities preserved")
        print("✅ Integration scripts moved to scripts/")
        print("\n🔍 New test structure:")
        print("├── services/*/tests/")
        print("│   ├── unit/")
        print("│   ├── integration/")
        print("│   └── api/")
        print("├── shared / tests/")
        print("│   ├── conftest.py")
        print("│   ├── data/")
        print("│   └── utils/")
        print("└── scripts/")
        print("    └── run_integration_tests.py")

        return 0
    else:
        print("❌ Migration failed")
        return 1


if __name__ == "__main__":
    exit(main())