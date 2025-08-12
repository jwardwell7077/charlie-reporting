"""
Basic Test for Report Generator Service
Tests the main components to ensure they're working correctly
"""

import pytest
import sys
from pathlib import Path
import tempfile
import pandas as pd

# Add src to path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from business.services.report_processor import ReportProcessingService
from business.models.csv_data import CSVFile, CSVRule
from business.models.transformation_config import TransformationConfig
from infrastructure.config import ServiceConfig, ConfigurationManager
from infrastructure.metrics import MetricsCollector
from infrastructure.logging import StructuredLogger


class TestReportProcessingService:
    """Test the main report processing service"""

    def setup_method(self):
        """Setup for each test"""
        self.processor = ReportProcessingService()
        self.tempdir = Path(tempfile.mkdtemp())

    def test_service_initialization(self):
        """Test that the service initializes correctly"""
        assert self.processor is not None
        assert self.processor.csv_transformer is not None
        assert self.processor.excel_service is not None

    def test_directory_validation(self):
        """Test directory validation"""
        # Test valid directory
        validation = self.processor.validate_input_directory(self.temp_dir)
        assert validation["is_valid"]
        assert validation["directory_exists"]
        assert validation["csv_file_count"] == 0

        # Test invalid directory
        invalid_dir = self.temp_dir / "nonexistent"
        validation = self.processor.validate_input_directory(invalid_dir)
        assert not validation["is_valid"]
        assert not validation["directory_exists"]

    def test_csv_file_creation(self):
        """Test CSV file domain model"""
        csv_file = CSVFile(
            file_name="test.csv",
            file_path="/tmp / test.csv",
            date_str="2025 - 01 - 28",
            hour_str="09",
            timestamp=pd.Timestamp.now()
        )

        assert csv_file.file_name == "test.csv"
        assert csv_file.matches_date_filter("2025 - 01 - 28")
        assert not csv_file.matches_date_filter("2025 - 01 - 29")

    def test_csv_rule_creation(self):
        """Test CSV rule domain model"""
        rule = CSVRule(
            file_pattern="ACQ",
            columns=["Date", "Agent", "Sales"],
            sheet_name="Acquisitions",
            required_columns=["Date", "Agent"]
        )

        assert rule.matches_filename("ACQ__2025 - 01 - 28_0900.csv")
        assert not rule.matches_filename("QCBS__2025 - 01 - 28_0900.csv")

    def test_transformation_config(self):
        """Test transformation configuration"""
        config = TransformationConfig.default_config()

        assert config is not None
        assert config.auto_detect_dates
        assert config.trim_whitespace
        assert config.remove_duplicates


class TestInfrastructureComponents:
    """Test infrastructure components"""

    def test_metrics_collector(self):
        """Test metrics collection"""
        collector = MetricsCollector()
        collector.initialize()

        assert collector.is_healthy()

        # Test recording metrics
        collector.record_request("GET", "/test", 200, 0.1)
        collector.record_file_processing("test.csv", 100, True, 1.0)

        metrics = collector.get_metrics()
        assert metrics["total_requests"] == 1
        assert metrics["successful_requests"] == 1
        assert metrics["total_files_processed"] == 1

    def test_structured_logger(self):
        """Test structured logging"""
        logger = StructuredLogger()

        assert logger.is_healthy()

        # Test logging methods (should not raise exceptions)
        logger.log_info("Test message", test_field="test_value")
        logger.log_error("Test error", error_code="TEST_001")
        logger.log_warning("Test warning", component="test")

    def test_configuration_manager(self):
        """Test configuration management"""
        config_manager = ConfigurationManager()
        config = config_manager.get_config()

        assert isinstance(config, ServiceConfig)
        assert config.port == 8083
        assert config.host == "0.0.0.0"

        # Test configuration dictionary
        config_dict = config_manager.get_config_dict()
        assert "port" in config_dict
        assert "host" in config_dict


class TestAPISchemas:
    """Test API schema models"""

    def test_processing_request_schema(self):
        """Test processing request validation"""
        from interface.schemas import DirectoryProcessRequest

        # Valid request
        request_data = {
            "raw_directory": "/tmp / raw",
            "archive_directory": "/tmp / archive",
            "output_directory": "/tmp / output",
            "date_filter": "2025 - 01 - 28",
            "attachment_config": {"test.csv": {"columns": ["Date", "Agent"]}}
        }

        request = DirectoryProcessRequest(**request_data)
        assert request.date_filter == "2025 - 01 - 28"
        assert request.raw_directory == "/tmp / raw"

    def test_processing_result_schema(self):
        """Test processing result schema"""
        from interface.schemas import ProcessingResult

        result = ProcessingResult(
            success=True,
            processing_time_seconds=1.5
        )

        assert result.success
        assert result.processing_time_seconds == 1.5


@pytest.mark.asyncio
async def test_fastapi_app():
    """Test that the FastAPI app can be imported and initialized"""
    from interface.app import app

    assert app is not None
    assert app.title == "Report Generator Service"


if __name__ == "__main__":
    # Run basic tests
    test_processor = TestReportProcessingService()
    test_processor.setup_method()
    test_processor.test_service_initialization()
    test_processor.test_directory_validation()
    test_processor.test_csv_file_creation()
    test_processor.test_csv_rule_creation()
    test_processor.test_transformation_config()

    test_infra = TestInfrastructureComponents()
    test_infra.test_metrics_collector()
    test_infra.test_structured_logger()
    test_infra.test_configuration_manager()

    test_schemas = TestAPISchemas()
    test_schemas.test_processing_request_schema()
    test_schemas.test_processing_result_schema()

    print("✅ All basic tests passed! The report-generator service is ready.")
    print("🚀 Start the service with: python src/main.py")
    print("📖 API documentation available at: http://localhost:8083 / docs")
