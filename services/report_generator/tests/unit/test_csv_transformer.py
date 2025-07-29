"""
Test suite for CSVTransformationService
Validates CSV parsing, transformation, and error handling
"""
import pytest
import pandas as pd
from pathlib import Path
import sys
import os

# Add services to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'services'))

from report_generator.src.business.services.csv_transformer import CSVTransformationService
from report_generator.src.business.models.csv_data import CSVRule

class TestCSVTransformationService:
    """Test suite for CSV transformation business logic"""
    
    @pytest.fixture
    def csv_transformer(self, mock_logger):
        """Create CSVTransformationService instance for testing"""
        return CSVTransformationService(mock_logger)
    
    @pytest.fixture
    def sample_csv_rule(self):
        """Sample CSV transformation rule"""
        return CSVRule(
            filename="ACQ.csv",
            agent_column="Agent",
            date_column="Date",
            value_columns=["Acquisitions", "Revenue"],
            sheet_name="ACQ_Report"
        )
    
    def test_csv_parsing_basic(self, csv_transformer, csv_test_files, sample_csv_rule):
        """Test basic CSV file parsing"""
        csv_file = csv_test_files["ACQ.csv"]
        
        result = csv_transformer.parse_csv(csv_file["path"], sample_csv_rule)
        
        assert result is not None
        assert len(result) == 2  # Two rows of test data
        assert "Agent" in result.columns
        assert "Date" in result.columns
        assert "Acquisitions" in result.columns
        assert "Revenue" in result.columns
    
    def test_csv_transformation_rules(self, csv_transformer, csv_test_files, sample_csv_rule):
        """Test CSV data transformation with rules"""
        csv_file = csv_test_files["ACQ.csv"]
        
        result = csv_transformer.transform_data(csv_file["path"], sample_csv_rule)
        
        assert result is not None
        assert not result.empty
        # Verify data types are correct after transformation
        assert result["Acquisitions"].dtype in ['int64', 'float64']
        assert result["Revenue"].dtype in ['int64', 'float64']
    
    def test_malformed_csv_handling(self, csv_transformer, temp_test_dir, sample_csv_rule):
        """Test error handling with malformed CSV files"""
        # Create malformed CSV file
        malformed_file = temp_test_dir / "malformed.csv"
        with open(malformed_file, 'w') as f:
            f.write("Header1,Header2\n")
            f.write("Value1\n")  # Missing column
            f.write("Value2,Value3,ExtraValue\n")  # Extra column
        
        with pytest.raises(Exception):
            csv_transformer.parse_csv(malformed_file, sample_csv_rule)
    
    def test_empty_csv_handling(self, csv_transformer, temp_test_dir, sample_csv_rule):
        """Test handling of empty CSV files"""
        empty_file = temp_test_dir / "empty.csv"
        with open(empty_file, 'w') as f:
            f.write("Agent,Date,Acquisitions,Revenue\n")  # Header only
        
        result = csv_transformer.parse_csv(empty_file, sample_csv_rule)
        assert result is not None
        assert len(result) == 0
    
    def test_data_validation(self, csv_transformer, temp_test_dir, sample_csv_rule):
        """Test data validation during transformation"""
        # Create CSV with invalid data
        invalid_file = temp_test_dir / "invalid_data.csv"
        with open(invalid_file, 'w') as f:
            f.write("Agent,Date,Acquisitions,Revenue\n")
            f.write("John Doe,2025-07-28,not_a_number,1000\n")
        
        with pytest.raises(Exception):
            csv_transformer.transform_data(invalid_file, sample_csv_rule)
    
    @pytest.mark.performance
    def test_large_csv_processing(self, csv_transformer, temp_test_dir, sample_csv_rule, performance_test_data):
        """Test performance with large CSV files"""
        import time
        
        # Create large CSV file
        large_file = temp_test_dir / "large.csv"
        df = pd.DataFrame(performance_test_data)
        df.to_csv(large_file, index=False)
        
        start_time = time.time()
        result = csv_transformer.parse_csv(large_file, sample_csv_rule)
        processing_time = time.time() - start_time
        
        assert result is not None
        assert len(result) > 0
        assert processing_time < 30  # Should process within 30 seconds
    
    def test_multiple_csv_processing(self, csv_transformer, csv_test_files):
        """Test processing multiple CSV files"""
        results = {}
        
        for filename, csv_data in csv_test_files.items():
            rule = CSVRule(
                filename=filename,
                agent_column="Agent",
                date_column="Date",
                value_columns=["Acquisitions", "Revenue"] if "ACQ" in filename else ["Dials", "Connects"],
                sheet_name=f"{filename.split('.')[0]}_Report"
            )
            
            results[filename] = csv_transformer.parse_csv(csv_data["path"], rule)
        
        assert len(results) == len(csv_test_files)
        for filename, result in results.items():
            assert result is not None
            assert len(result) > 0
    
    def test_csv_rule_validation(self, csv_transformer):
        """Test CSV rule validation"""
        # Valid rule
        valid_rule = CSVRule(
            filename="test.csv",
            agent_column="Agent",
            date_column="Date", 
            value_columns=["Value1", "Value2"],
            sheet_name="Test_Sheet"
        )
        assert valid_rule.filename == "test.csv"
        assert valid_rule.agent_column == "Agent"
        
        # Invalid rule - missing required fields
        with pytest.raises(Exception):
            invalid_rule = CSVRule(
                filename="",  # Empty filename
                agent_column="Agent",
                date_column="Date",
                value_columns=[],  # Empty value columns
                sheet_name="Test"
            )
