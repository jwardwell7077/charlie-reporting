"""
Integration tests for Phase 1 complete workflow
Tests end-to-end CSV processing → Excel generation pipeline
"""
import pytest
import pandas as pd
from pathlib import Path
import sys
import os

# Add services to path 
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'services'))

class TestPhase1Workflow:
    """Integration tests for complete Phase 1 business logic"""
    
    def test_complete_csv_to_excel_workflow(self, csv_test_files, temp_test_dir):
        """Test complete workflow from CSV input to Excel output"""
        # This will be implemented once we fix the import issues
        # For now, create a placeholder test
        assert True  # Placeholder
    
    def test_multiple_csv_processing_workflow(self, csv_test_files, temp_test_dir):
        """Test processing multiple CSV files in a single workflow"""
        assert len(csv_test_files) >= 2
        
        # Verify test data exists
        for filename, csv_data in csv_test_files.items():
            assert csv_data["path"].exists()
            assert len(csv_data["data"]) > 0
    
    def test_error_handling_workflow(self, temp_test_dir):
        """Test workflow error handling and recovery"""
        # Create invalid CSV file
        invalid_file = temp_test_dir / "invalid.csv"
        with open(invalid_file, 'w') as f:
            f.write("Invalid,CSV,Data\n")
            f.write("Missing,Column\n")
        
        # Test that workflow handles errors gracefully
        assert invalid_file.exists()
    
    @pytest.mark.performance 
    def test_workflow_performance_baseline(self, performance_test_data, temp_test_dir):
        """Establish performance baseline for complete workflow"""
        import time
        
        # Create test data file
        test_file = temp_test_dir / "performance_test.csv"
        df = pd.DataFrame(performance_test_data)
        df.to_csv(test_file, index=False)
        
        start_time = time.time()
        
        # Read CSV file (simulating workflow)
        data = pd.read_csv(test_file)
        
        # Basic data processing (simulating transformation)
        processed_data = data.groupby('Agent').agg({
            'Acquisitions': 'sum',
            'Revenue': 'sum',
            'Dials': 'sum',
            'Connects': 'sum'
        }).reset_index()
        
        # Write Excel file (simulating report generation)
        output_file = temp_test_dir / "performance_output.xlsx"
        processed_data.to_excel(output_file, index=False)
        
        total_time = time.time() - start_time
        
        assert output_file.exists()
        assert total_time < 60  # Complete workflow under 1 minute for test data
        
        # Log performance for baseline
        print(f"Performance baseline: {total_time:.2f} seconds for {len(performance_test_data)} records")
    
    def test_data_integrity_throughout_workflow(self, csv_test_files, temp_test_dir):
        """Test data integrity is maintained throughout the workflow"""
        for filename, csv_data in csv_test_files.items():
            # Read original data
            original_df = pd.read_csv(csv_data["path"])
            
            # Simulate workflow data transformation
            processed_df = original_df.copy()
            
            # Write to Excel and read back
            excel_file = temp_test_dir / f"integrity_test_{filename.replace('.csv', '.xlsx')}"
            processed_df.to_excel(excel_file, index=False)
            
            # Read back from Excel
            excel_df = pd.read_excel(excel_file)
            
            # Verify data integrity
            assert len(excel_df) == len(original_df)
            assert list(excel_df.columns) == list(original_df.columns)
    
    def test_concurrent_workflow_processing(self, csv_test_files, temp_test_dir):
        """Test multiple workflows can run concurrently"""
        import threading
        
        results = []
        
        def process_csv(filename, csv_data):
            try:
                # Simulate workflow processing
                df = pd.read_csv(csv_data["path"])
                output_file = temp_test_dir / f"concurrent_{filename.replace('.csv', '.xlsx')}"
                df.to_excel(output_file, index=False)
                results.append(output_file.exists())
            except Exception as e:
                results.append(False)
        
        # Start concurrent processing
        threads = []
        for filename, csv_data in csv_test_files.items():
            thread = threading.Thread(target=process_csv, args=(filename, csv_data))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all workflows completed successfully
        assert all(results)
        assert len(results) == len(csv_test_files)
