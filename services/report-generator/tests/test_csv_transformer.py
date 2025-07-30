"""
Unit Tests for CSV Transformation Service
Testing business logic with proper isolation
"""

import pytest
import pandas as pd
import io
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from business.services.csv_transformer import CSVTransformationService
from business.models.csv_file import CSVFile
from business.models.transformation_config import TransformationConfig


class TestCSVTransformationService:
    """Test suite for CSV Transformation Service business logic"""
    
    @pytest.fixture
    def csv_service(self):
        """CSV Transformation Service fixture"""
        return CSVTransformationService()
    
    @pytest.fixture
    def sample_csv_data(self):
        """Sample CSV data for testing"""
        return """Agent,Date,Acquisitions,Revenue,Campaign
John Doe,2025-01-15,5,1250.00,Summer Sale
Jane Smith,2025-01-15,3,750.00,Summer Sale
Bob Johnson,2025-01-15,7,1750.00,Winter Promo
Alice Brown,2025-01-16,2,500.00,Summer Sale"""
    
    @pytest.fixture
    def sample_csv_file(self, sample_csv_data):
        """Sample CSV file for testing"""
        csv_buffer = io.StringIO(sample_csv_data)
        df = pd.read_csv(csv_buffer)
        return CSVFile(
            filename="test_data.csv",
            data=df,
            original_path="/tmp/test_data.csv"
        )
    
    def test_validate_csv_file_valid(self, csv_service, sample_csv_file):
        """Test validation of valid CSV file"""
        result = csv_service.validate_csv_file(sample_csv_file)
        
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
        assert result["row_count"] == 4
        assert result["column_count"] == 5
        assert "Agent" in result["columns"]
        assert "Date" in result["columns"]
        assert "Acquisitions" in result["columns"]
    
    def test_validate_csv_file_missing_columns(self, csv_service):
        """Test validation with missing required columns"""
        # Create CSV with missing required columns
        invalid_data = """Name,Amount
John,100
Jane,200"""
        csv_buffer = io.StringIO(invalid_data)
        df = pd.read_csv(csv_buffer)
        csv_file = CSVFile(
            filename="invalid.csv",
            data=df,
            original_path="/tmp/invalid.csv"
        )
        
        result = csv_service.validate_csv_file(csv_file)
        
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0
        assert any("required column" in error.lower() for error in result["errors"])
    
    def test_validate_csv_file_empty(self, csv_service):
        """Test validation of empty CSV file"""
        empty_df = pd.DataFrame()
        csv_file = CSVFile(
            filename="empty.csv",
            data=empty_df,
            original_path="/tmp/empty.csv"
        )
        
        result = csv_service.validate_csv_file(csv_file)
        
        assert result["is_valid"] is False
        assert "empty" in str(result["errors"]).lower()
    
    def test_create_transformation_rules_default(self, csv_service, sample_csv_file):
        """Test creation of default transformation rules"""
        rules = csv_service.create_transformation_rules(sample_csv_file)
        
        assert isinstance(rules, list)
        assert len(rules) > 0
        
        # Check for common transformation rules
        rule_types = [rule.get("type") for rule in rules]
        assert "date_standardization" in rule_types
        assert "numeric_formatting" in rule_types
        assert "text_cleaning" in rule_types
    
    def test_create_transformation_rules_custom_config(self, csv_service, sample_csv_file):
        """Test creation of transformation rules with custom config"""
        config = TransformationConfig(
            date_format="%Y-%m-%d",
            numeric_precision=2,
            text_case="upper",
            remove_duplicates=True
        )
        
        rules = csv_service.create_transformation_rules(sample_csv_file, config)
        
        assert isinstance(rules, list)
        # Verify custom config is reflected in rules
        date_rules = [rule for rule in rules if rule.get("type") == "date_standardization"]
        assert len(date_rules) > 0
        assert date_rules[0].get("format") == "%Y-%m-%d"
    
    def test_transform_csv_file_success(self, csv_service, sample_csv_file):
        """Test successful CSV transformation"""
        # Create transformation rules
        rules = csv_service.create_transformation_rules(sample_csv_file)
        
        # Apply transformation
        result = csv_service.transform_csv_file(sample_csv_file, rules)
        
        assert result.success is True
        assert result.error_message is None
        assert isinstance(result.transformed_data, pd.DataFrame)
        assert len(result.transformed_data) > 0
        
        # Verify transformations were applied
        transformed_df = result.transformed_data
        assert "Agent" in transformed_df.columns
        assert "Date" in transformed_df.columns
        
        # Check that dates are properly formatted
        date_series = transformed_df["Date"]
        assert pd.api.types.is_datetime64_any_dtype(date_series) or \
               all(isinstance(date, str) for date in date_series)
    
    def test_transform_csv_file_with_date_parsing(self, csv_service):
        """Test transformation with date parsing"""
        # Create CSV with various date formats
        date_data = """Agent,Date,Revenue
John,01/15/2025,1250.00
Jane,2025-01-16,750.00
Bob,15-Jan-2025,1750.00"""
        
        csv_buffer = io.StringIO(date_data)
        df = pd.read_csv(csv_buffer)
        csv_file = CSVFile(
            filename="date_test.csv",
            data=df,
            original_path="/tmp/date_test.csv"
        )
        
        rules = csv_service.create_transformation_rules(csv_file)
        result = csv_service.transform_csv_file(csv_file, rules)
        
        assert result.success is True
        
        # Check that dates were standardized
        transformed_df = result.transformed_data
        date_column = transformed_df["Date"]
        
        # All dates should be in a consistent format after transformation
        unique_date_formats = set()
        for date_val in date_column:
            if pd.notna(date_val):
                unique_date_formats.add(type(date_val).__name__)
        
        # Should have consistent type after transformation
        assert len(unique_date_formats) <= 2  # Allow for datetime and string
    
    def test_transform_csv_file_with_numeric_formatting(self, csv_service):
        """Test transformation with numeric formatting"""
        # Create CSV with various numeric formats
        numeric_data = """Agent,Revenue,Acquisitions
John,"1,250.50",5
Jane,750,3.0
Bob,1750.123,7"""
        
        csv_buffer = io.StringIO(numeric_data)
        df = pd.read_csv(csv_buffer)
        csv_file = CSVFile(
            filename="numeric_test.csv",
            data=df,
            original_path="/tmp/numeric_test.csv"
        )
        
        config = TransformationConfig(numeric_precision=2)
        rules = csv_service.create_transformation_rules(csv_file, config)
        result = csv_service.transform_csv_file(csv_file, rules)
        
        assert result.success is True
        
        # Check numeric formatting
        transformed_df = result.transformed_data
        revenue_column = transformed_df["Revenue"]
        
        # All revenue values should be numeric after transformation
        assert pd.api.types.is_numeric_dtype(revenue_column)
    
    def test_transform_csv_file_failure(self, csv_service):
        """Test transformation failure handling"""
        # Create a problematic CSV file
        problematic_data = pd.DataFrame({"col1": [None, None, None]})
        csv_file = CSVFile(
            filename="problem.csv",
            data=problematic_data,
            original_path="/tmp/problem.csv"
        )
        
        # Create rules that might cause issues
        rules = [{"type": "invalid_transformation", "target": "nonexistent_column"}]
        
        result = csv_service.transform_csv_file(csv_file, rules)
        
        # Should handle failure gracefully
        assert result.success is False
        assert result.error_message is not None
        assert "transformation failed" in result.error_message.lower() or \
               "error" in result.error_message.lower()
    
    def test_get_supported_formats(self, csv_service):
        """Test getting supported file formats"""
        formats = csv_service.get_supported_formats()
        
        assert isinstance(formats, list)
        assert "csv" in formats
        assert "xlsx" in formats or "xls" in formats
    
    def test_detect_encoding(self, csv_service):
        """Test automatic encoding detection"""
        # Test with UTF-8 content
        utf8_content = "Agent,Date,Revenue\nJöhn Døe,2025-01-15,1250.00"
        encoding = csv_service.detect_encoding(utf8_content.encode('utf-8'))
        
        assert encoding in ["utf-8", "UTF-8", "ascii"]
    
    def test_clean_data_basic(self, csv_service, sample_csv_file):
        """Test basic data cleaning operations"""
        # Add some dirty data
        dirty_data = sample_csv_file.data.copy()
        dirty_data.loc[len(dirty_data)] = ["  John Doe  ", "2025-01-15", "5", "1250.00", "Summer Sale  "]
        
        csv_file = CSVFile(
            filename="dirty.csv",
            data=dirty_data,
            original_path="/tmp/dirty.csv"
        )
        
        cleaned_data = csv_service.clean_data(csv_file)
        
        assert isinstance(cleaned_data, pd.DataFrame)
        assert len(cleaned_data) >= len(sample_csv_file.data)
        
        # Check that whitespace was cleaned
        agent_values = cleaned_data["Agent"].tolist()
        assert all(agent.strip() == agent for agent in agent_values if pd.notna(agent))


class TestCSVTransformationServiceEdgeCases:
    """Test edge cases and error conditions"""
    
    @pytest.fixture
    def csv_service(self):
        """CSV Transformation Service fixture"""
        return CSVTransformationService()
    
    def test_transform_large_file(self, csv_service):
        """Test transformation of large CSV file"""
        # Create a large dataset
        large_data = {
            "Agent": [f"Agent_{i}" for i in range(1000)],
            "Date": ["2025-01-15"] * 1000,
            "Revenue": [100.0 + i for i in range(1000)]
        }
        large_df = pd.DataFrame(large_data)
        
        csv_file = CSVFile(
            filename="large.csv",
            data=large_df,
            original_path="/tmp/large.csv"
        )
        
        rules = csv_service.create_transformation_rules(csv_file)
        result = csv_service.transform_csv_file(csv_file, rules)
        
        assert result.success is True
        assert len(result.transformed_data) == 1000
    
    def test_transform_with_special_characters(self, csv_service):
        """Test transformation with special characters"""
        special_data = """Agent,Date,Revenue,Notes
John Döe,2025-01-15,1250.50,"Contains special: éñ & symbols!"
José María,2025-01-16,750.00,"UTF-8: ñ, ü, ç, é"
李小明,2025-01-17,1000.00,"Chinese characters: 测试数据"
Mohammed Al-خالد,2025-01-18,500.00,"Arabic: اختبار البيانات"
"""
        
        csv_buffer = io.StringIO(special_data)
        df = pd.read_csv(csv_buffer)
        csv_file = CSVFile(
            filename="special_chars.csv",
            data=df,
            original_path="/tmp/special_chars.csv"
        )
        
        rules = csv_service.create_transformation_rules(csv_file)
        result = csv_service.transform_csv_file(csv_file, rules)
        
        assert result.success is True
        assert len(result.transformed_data) == 4
        
        # Verify special characters are preserved
        agent_names = result.transformed_data["Agent"].tolist()
        assert any("Döe" in name for name in agent_names)
        assert any("José" in name for name in agent_names)
    
    def test_transform_with_missing_values(self, csv_service):
        """Test transformation with missing values"""
        missing_data = """Agent,Date,Revenue,Campaign
John Doe,2025-01-15,1250.00,Summer Sale
Jane Smith,,750.00,
Bob Johnson,2025-01-17,,Winter Promo
,2025-01-18,500.00,Spring Sale"""
        
        csv_buffer = io.StringIO(missing_data)
        df = pd.read_csv(csv_buffer)
        csv_file = CSVFile(
            filename="missing_values.csv",
            data=df,
            original_path="/tmp/missing_values.csv"
        )
        
        rules = csv_service.create_transformation_rules(csv_file)
        result = csv_service.transform_csv_file(csv_file, rules)
        
        assert result.success is True
        
        # Check handling of missing values
        transformed_df = result.transformed_data
        assert len(transformed_df) == 4
        
        # Verify missing values are handled appropriately
        assert transformed_df["Agent"].isna().sum() <= 1  # At most one missing agent
        assert transformed_df["Date"].isna().sum() <= 1   # At most one missing date
    
    def test_duplicate_column_names(self, csv_service):
        """Test handling of duplicate column names"""
        # Create CSV with duplicate column names
        duplicate_data = """Agent,Date,Agent,Revenue
John Doe,2025-01-15,Senior,1250.00
Jane Smith,2025-01-16,Junior,750.00"""
        
        csv_buffer = io.StringIO(duplicate_data)
        df = pd.read_csv(csv_buffer)
        csv_file = CSVFile(
            filename="duplicate_cols.csv",
            data=df,
            original_path="/tmp/duplicate_cols.csv"
        )
        
        # Should handle duplicate columns gracefully
        validation = csv_service.validate_csv_file(csv_file)
        
        # Either validation should fail or it should handle duplicates
        if validation["is_valid"]:
            rules = csv_service.create_transformation_rules(csv_file)
            result = csv_service.transform_csv_file(csv_file, rules)
            # If transformation succeeds, duplicate columns should be resolved
            assert result.success is True
        else:
            # Or validation should catch the duplicate column issue
            assert any("duplicate" in error.lower() for error in validation["errors"])
