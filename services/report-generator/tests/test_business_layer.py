"""
Business Layer Unit Tests
Tests for the business logic without infrastructure dependencies
"""

import pytest
import pandas as pd
from pathlib import Path
from datetime import datetime
import tempfile
import os

from business.models.csv_file import CSVFile
from business.models.csv_data import CSVRule, CSVTransformationResult
from business.models.transformation_config import TransformationConfig
from business.services.csv_transformer import CSVTransformationService
from business.services.excel_service import ExcelReportService
from business.services.report_processor import ReportProcessingService
from business.exceptions import BusinessException


class TestCSVFile:
    """Test CSV file domain model"""
    
    def test_csv_file_creation(self):
        """Test creating a CSV file object"""
        # Create sample data
        data = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Charlie'],
            'Age': [25, 30, 35],
            'Date': ['2025-01-01', '2025-01-02', '2025-01-03']
        })
        
        csv_file = CSVFile(
            filename="test.csv",
            file_path="/test/test.csv",
            data=data
        )
        
        assert csv_file.filename == "test.csv"
        assert csv_file.row_count == 3
        assert csv_file.column_count == 3
        assert csv_file.columns == ['Name', 'Age', 'Date']
        assert not csv_file.is_empty
    
    def test_csv_file_validation(self):
        """Test CSV file validation"""
        data = pd.DataFrame({
            'Name': ['Alice', 'Bob'],
            'Age': [25, 30]
        })
        
        csv_file = CSVFile(
            filename="test.csv",
            file_path="/test/test.csv", 
            data=data
        )
        
        # Test required columns validation
        required_columns = ['Name', 'Age', 'Email']
        missing = csv_file.validate_required_columns(required_columns)
        assert 'Email' in missing
        
        # Test duplicate detection
        data_with_dupes = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Alice'],
            'Age': [25, 30, 25]
        })
        
        csv_file_dupes = CSVFile(
            filename="test_dupes.csv",
            file_path="/test/test_dupes.csv",
            data=data_with_dupes
        )
        
        assert csv_file_dupes.has_duplicates()
        assert csv_file_dupes.get_duplicate_count() == 1


class TestCSVRule:
    """Test CSV transformation rule"""
    
    def test_csv_rule_creation(self):
        """Test creating a CSV rule"""
        rule = CSVRule(
            file_pattern="ACQ.csv",
            columns=['Date', 'Agent', 'Count'],
            sheet_name="Acquisitions",
            required_columns=['Date', 'Agent']
        )
        
        assert rule.file_pattern == "ACQ.csv"
        assert rule.sheet_name == "Acquisitions"
        assert len(rule.columns) == 3
    
    def test_filename_matching(self):
        """Test filename pattern matching"""
        rule = CSVRule(
            file_pattern="ACQ.csv",
            columns=['Date'],
            sheet_name="ACQ"
        )
        
        assert rule.matches_filename("ACQ__2025-01-28_0900.csv")
        assert not rule.matches_filename("QCBS__2025-01-28_0900.csv")
    
    def test_dataframe_validation(self):
        """Test DataFrame validation against rule"""
        rule = CSVRule(
            file_pattern="test.csv",
            columns=['Name', 'Age'],
            sheet_name="Test",
            required_columns=['Name']
        )
        
        # Valid DataFrame
        valid_df = pd.DataFrame({
            'Name': ['Alice', 'Bob'],
            'Age': [25, 30],
            'Extra': ['X', 'Y']
        })
        
        validation = rule.validate_dataframe(valid_df)
        assert validation['is_valid']
        
        # Invalid DataFrame (missing required column)
        invalid_df = pd.DataFrame({
            'Age': [25, 30],
            'Extra': ['X', 'Y']
        })
        
        validation = rule.validate_dataframe(invalid_df)
        assert not validation['is_valid']
        assert len(validation['errors']) > 0


class TestTransformationConfig:
    """Test transformation configuration"""
    
    def test_default_config(self):
        """Test default transformation configuration"""
        config = TransformationConfig.default_config()
        
        assert config.date_format == "YYYY-MM-DD"
        assert config.numeric_precision == 2
        assert config.trim_whitespace is True
        assert config.remove_duplicates is False
    
    def test_custom_config(self):
        """Test custom transformation configuration"""
        config = TransformationConfig(
            date_format="MM/DD/YYYY",
            numeric_precision=3,
            trim_whitespace=True,
            remove_duplicates=True,
            column_mappings={"Old_Name": "New_Name"}
        )
        
        assert config.date_format == "MM/DD/YYYY"
        assert config.numeric_precision == 3
        assert config.column_mappings["Old_Name"] == "New_Name"


class TestCSVTransformationService:
    """Test CSV transformation business service"""
    
    def setUp(self):
        self.service = CSVTransformationService()
    
    def test_service_creation(self):
        """Test service instantiation"""
        service = CSVTransformationService()
        assert service is not None
        assert service.logger is not None
    
    def test_create_transformation_rules(self):
        """Test rule creation from configuration"""
        service = CSVTransformationService()
        
        config = {
            "ACQ.csv": {
                "columns": ["Date", "Agent", "Count"],
                "required_columns": ["Date", "Agent"]
            },
            "QCBS.csv": {
                "columns": ["Date", "Agent", "Calls"],
                "required_columns": ["Date"]
            }
        }
        
        rules = service.create_transformation_rules(config)
        assert len(rules) == 2
        assert rules[0].file_pattern == "ACQ.csv"
        assert rules[1].file_pattern == "QCBS.csv"


class TestExcelReportService:
    """Test Excel report business service"""
    
    def test_service_creation(self):
        """Test service instantiation"""
        service = ExcelReportService()
        assert service is not None
        assert service.logger is not None
    
    def test_safe_sheet_name(self):
        """Test Excel-safe sheet name generation"""
        service = ExcelReportService()
        
        # Test long name truncation
        long_name = "This_is_a_very_long_sheet_name_that_exceeds_Excel_limits"
        safe_name = service._get_safe_sheet_name(long_name)
        assert len(safe_name) <= 31
        
        # Test invalid character replacement
        invalid_name = "Sheet[with*invalid?chars]"
        safe_name = service._get_safe_sheet_name(invalid_name)
        assert '[' not in safe_name
        assert '*' not in safe_name
        assert '?' not in safe_name


class TestReportProcessingService:
    """Test main report processing orchestration service"""
    
    def test_service_creation(self):
        """Test service instantiation"""
        service = ReportProcessingService()
        assert service is not None
        assert service.csv_transformer is not None
        assert service.excel_service is not None
    
    def test_validate_input_directory(self):
        """Test input directory validation"""
        service = ReportProcessingService()
        
        # Test non-existent directory
        non_existent = Path("/non/existent/directory")
        validation = service.validate_input_directory(non_existent)
        assert not validation["is_valid"]
        assert "does not exist" in validation["errors"][0]
        
        # Test with temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            validation = service.validate_input_directory(temp_path)
            assert validation["is_valid"]
            assert validation["directory_exists"]
    
    def test_processing_statistics(self):
        """Test processing statistics generation"""
        service = ReportProcessingService()
        
        # Mock processing results
        results = {
            "processing_time_seconds": 10.5,
            "discovered_files": 5,
            "transformed_files": 4,
            "total_records": 1000,
            "warnings": ["Warning 1"],
            "errors": []
        }
        
        stats = service.get_processing_statistics(results)
        assert stats["success_rate"] == 80.0  # 4/5 * 100
        assert stats["files_per_second"] > 0
        assert stats["records_per_second"] > 0
        assert stats["processing_efficiency"] == "good"  # 10.5 seconds
    
    def test_processing_summary(self):
        """Test processing summary generation"""
        service = ReportProcessingService()
        
        # Success case
        success_results = {
            "success": True,
            "transformed_files": 4,
            "discovered_files": 5,
            "report_sheets": 3,
            "total_records": 1000,
            "processing_time_seconds": 15.2,
            "excel_filename": "report.xlsx",
            "archived_files": ["file1.csv", "file2.csv"],
            "warnings": [],
            "failed_files": 1
        }
        
        summary = service.create_processing_summary(success_results)
        assert "✅ Successfully processed" in summary
        assert "4 of 5 files" in summary
        assert "1,000 total records" in summary
        assert "15.2 seconds" in summary
        
        # Failure case
        failure_results = {
            "success": False,
            "error_message": "Processing failed",
            "processing_time_seconds": 5.0
        }
        
        summary = service.create_processing_summary(failure_results)
        assert "❌ Error:" in summary
        assert "Processing failed" in summary


# Integration test
class TestBusinessLayerIntegration:
    """Integration tests for the complete business layer"""
    
    def test_complete_workflow_simulation(self):
        """Test the complete business workflow without infrastructure"""
        # This test simulates the complete workflow using in-memory data
        # without touching file system or external dependencies
        
        # Step 1: Create sample CSV data
        sample_data = pd.DataFrame({
            'Date': ['2025-01-28', '2025-01-28', '2025-01-28'],
            'Agent': ['Alice', 'Bob', 'Charlie'], 
            'Count': [10, 15, 8],
            'Revenue': [1000.50, 1500.75, 800.25]
        })
        
        # Step 2: Create CSV file model
        csv_file = CSVFile(
            filename="ACQ__2025-01-28_0900.csv",
            file_path="/mock/path/ACQ__2025-01-28_0900.csv",
            data=sample_data
        )
        
        # Step 3: Create transformation rule
        rule = CSVRule(
            file_pattern="ACQ.csv",
            columns=['Date', 'Agent', 'Count', 'Revenue'],
            sheet_name="Acquisitions",
            required_columns=['Date', 'Agent']
        )
        
        csv_file.rule = rule
        
        # Step 4: Transform the data
        csv_transformer = CSVTransformationService()
        transformation_result = csv_transformer.transform_csv_file(csv_file)
        
        assert transformation_result.success
        assert transformation_result.dataframe is not None
        assert len(transformation_result.dataframe) == 3
        
        # Step 5: Create report
        report = csv_transformer.create_report_from_results(
            [transformation_result], 
            "2025-01-28"
        )
        
        assert len(report.sheets) == 1
        assert "Acquisitions" in report.sheets
        assert report.get_total_records() == 3
        
        # Step 6: Validate for Excel
        excel_service = ExcelReportService()
        validation = excel_service.validate_report_for_excel(report)
        assert validation['is_valid']
        
        # Step 7: Prepare Excel data
        excel_data = excel_service.prepare_excel_data(report)
        assert len(excel_data) == 1
        assert "Acquisitions" in excel_data
        
        # Step 8: Generate filename
        filename = excel_service.generate_filename(report, "test_report")
        assert filename.endswith(".xlsx")
        assert "2025-01-28" in filename


if __name__ == "__main__":
    # Run basic smoke tests
    print("Running business layer smoke tests...")
    
    # Test 1: Create CSV file
    data = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    csv_file = CSVFile("test.csv", "/test/test.csv", data)
    print(f"✓ CSV file created: {csv_file.filename} with {csv_file.row_count} rows")
    
    # Test 2: Create services
    csv_service = CSVTransformationService()
    excel_service = ExcelReportService()
    report_service = ReportProcessingService()
    print("✓ All business services created successfully")
    
    # Test 3: Create transformation config
    config = TransformationConfig.default_config()
    print(f"✓ Transformation config created with date format: {config.date_format}")
    
    print("🎉 Business layer smoke tests passed!")
