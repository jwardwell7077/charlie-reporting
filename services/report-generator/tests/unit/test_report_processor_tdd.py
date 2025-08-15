"""TDD Cycle 1: Core Report Generation
RED phase - Write failing tests first
"""

# Import our interfaces and schemas
import sys
from pathlib import Path

import pandas as pd
import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from business.models.csv_file import CSVFile
from interface.schemas import DirectoryProcessRequest, ProcessingResult

from tests.fixtures.mock_services import (
    MockConfigManager,
    MockCSVTransformer,
    MockDirectoryProcessor,
    MockExcelGenerator,
    MockFileManager,
    MockLogger,
    MockMetricsCollector,
)


class TestReportProcessingService:
    """Test suite for core report processing functionality"""

    @pytest.fixture
    def mock_services(self):
        """Create all mock services for testing"""
        return {
            'directory_processor': MockDirectoryProcessor(),
            'csv_transformer': MockCSVTransformer(),
            'excel_generator': MockExcelGenerator(),
            'file_manager': MockFileManager(),
            'config_manager': MockConfigManager(),
            'logger': MockLogger(),
            'metrics': MockMetricsCollector()
        }

    @pytest.fixture
    def sample_csv_file(self):
        """Create sample CSV file for testing"""
        data = pd.DataFrame({
            'Column1': ['Value1', 'Value2'],
            'Column2': ['ValueA', 'ValueB']
        })
        return CSVFile(
            file_name="test_file.csv",
            data=data,
            original_path="/test / path / test_file.csv"
        )

    @pytest.fixture
    def sample_request(self):
        """Create sample processing request"""
        return DirectoryProcessRequest(
            raw_directory="/test / raw",
            archive_directory="/test / archive",
            output_directory="/test / output",
            date_filter="2025 - 07 - 29",
            hour_filter="09",
            attachment_config={
                "rules": [
                    {"pattern": "*.csv", "sheet_name": "Test", "columns": ["Column1"]}
                ]
            }
        )

    @pytest.mark.asyncio
    async def test_process_directory_success(self, mock_services, sample_request):
        """🔴 RED: This test will FAIL because ReportProcessingService doesn't exist yet

        Test the complete directory processing workflow:
        1. Scan directory for CSV files
        2. Transform each CSV file
        3. Generate Excel workbook
        4. Save Excel file
        5. Archive processed CSV files
        """
        # This import will fail - that's the RED phase!
        from business.services.report_processor import ReportProcessingService

        # Create service with mocked dependencies
        service = ReportProcessingService(
            directory_processor=mock_services['directory_processor'],
            csv_transformer=mock_services['csv_transformer'],
            excel_generator=mock_services['excel_generator'],
            file_manager=mock_services['file_manager'],
            config_manager=mock_services['config_manager'],
            logger=mock_services['logger'],
            metrics=mock_services['metrics']
        )

        # Setup mock data
        mock_services['directory_processor'].mockfiles = [
            Path("/test / raw / file1.csv"),
            Path("/test / raw / file2.csv")
        ]

        # Execute the service
        result = await service.process_directory(sample_request)

        # Assertions - what we expect from a successful processing
        assert isinstance(result, ProcessingResult)
        assert result.success is True
        assert result.discovered_files == 2
        assert result.transformed_files == 2
        assert result.excel_filename is not None
        assert len(result.archived_files) == 2

        # Verify service interactions
        assert len(mock_services['directory_processor'].scan_calls) == 1
        assert len(mock_services['csv_transformer'].transform_calls) == 2
        assert len(mock_services['excel_generator'].create_calls) == 1
        assert len(mock_services['file_manager'].save_calls) == 1
        assert len(mock_services['file_manager'].archive_calls) == 2

        # Verify metrics were recorded
        assert len(mock_services['metrics'].counters) > 0
        assert len(mock_services['metrics'].timings) > 0

    @pytest.mark.asyncio
    async def test_process_directory_no_files_found(self, mock_services, sample_request):
        """🔴 RED: Test handling when no CSV files are found
        """
        from business.services.report_processor import ReportProcessingService

        service = ReportProcessingService(**mock_services)

        # Setup: no files found
        mock_services['directory_processor'].mockfiles = []

        result = await service.process_directory(sample_request)

        assert result.success is True  # Still success, just no work to do
        assert result.discovered_files == 0
        assert result.transformed_files == 0
        assert result.message == "No CSV files found matching criteria"

    @pytest.mark.asyncio
    async def test_process_directory_transformation_error(self, mock_services, sample_request):
        """🔴 RED: Test handling when CSV transformation fails
        """
        from business.services.report_processor import ReportProcessingService

        service = ReportProcessingService(**mock_services)

        # Setup: files found but transformation fails
        mock_services['directory_processor'].mockfiles = [Path("/test / raw / bad_file.csv")]

        # Make transformation fail
        async def failing_transform(csv_file, config):
            raise ValueError("Invalid CSV structure")

        mock_services['csv_transformer'].transformcsv = failing_transform

        result = await service.process_directory(sample_request)

        assert result.success is False
        assert result.discovered_files == 1
        assert result.failed_files == 1
        assert "Invalid CSV structure" in result.error_message
        assert len(mock_services['logger'].error_logs) > 0


if __name__ == "__main__":
    # Run the tests to see them fail (RED phase)
    pytest.main([__file__, "-v"])
