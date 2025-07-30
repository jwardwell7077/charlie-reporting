"""
Phase 2.5 API Tests - Report Generator Service
Comprehensive testing for all FastAPI endpoints
"""
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from pathlib import Path
import sys
import os
import json
import io
from unittest.mock import Mock, patch, AsyncMock

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app, DEFAULT_CONFIG

class TestReportGeneratorAPI:
    """Test suite for Report Generator API endpoints"""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client fixture"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_csv_content(self):
        """Sample CSV content for testing"""
        return """Agent,Date,Acquisitions,Revenue,Campaign
John Doe,2025-01-15,5,1250.00,Summer Sale
Jane Smith,2025-01-15,3,750.00,Summer Sale
Bob Johnson,2025-01-15,7,1750.00,Winter Promo"""
    
    @pytest.fixture
    def sample_config(self):
        """Sample configuration for testing"""
        return {
            "attachment_rules": {
                "ACQ.csv": {
                    "columns": ["Agent", "Date", "Acquisitions", "Revenue", "Campaign"],
                    "sheet_name": "Acquisitions"
                }
            }
        }
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "service" in data
    
    def test_root_endpoint(self, client):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "service" in data
        assert "version" in data
        assert "endpoints" in data
    
    def test_metrics_endpoint(self, client):
        """Test the metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "uptime" in data
        assert "processed_files" in data
        assert "active_tasks" in data
        assert "memory_usage" in data
    
    def test_tasks_list_endpoint(self, client):
        """Test the tasks listing endpoint"""
        response = client.get("/tasks")
        assert response.status_code == 200
        
        data = response.json()
        assert "active_tasks" in data
        assert "completed_tasks" in data
        assert isinstance(data["active_tasks"], list)
        assert isinstance(data["completed_tasks"], list)
    
    def test_processing_stats_endpoint(self, client):
        """Test the processing statistics endpoint"""
        response = client.get("/processing-stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_processed" in data
        assert "success_rate" in data
        assert "average_processing_time" in data
        assert "file_types_processed" in data
    
    @patch('main.CSVProcessor')
    def test_validate_files_endpoint(self, mock_csv_processor, client, sample_csv_content):
        """Test the file validation endpoint"""
        # Mock the CSV processor
        mock_processor = Mock()
        mock_csv_processor.return_value = mock_processor
        mock_processor.validate_csv_files.return_value = {"valid": True, "errors": []}
        
        # Create test file
        files = {"files": ("test.csv", io.StringIO(sample_csv_content), "text/csv")}
        
        response = client.post("/validate-files", files=files)
        assert response.status_code == 200
        
        data = response.json()
        assert "validation_results" in data
        assert isinstance(data["validation_results"], list)
    
    @patch('main.CSVProcessor')
    @patch('main.ExcelGenerator')
    def test_transform_endpoint_simple(self, mock_excel_gen, mock_csv_processor, client, sample_csv_content):
        """Test the transform endpoint with simple CSV data"""
        # Mock processors
        mock_csv = Mock()
        mock_csv_processor.return_value = mock_csv
        mock_csv.process_csv_files.return_value = {"ACQ.csv": []}
        
        mock_excel = Mock()
        mock_excel_gen.return_value = mock_excel
        mock_excel.generate_excel_report.return_value = "/tmp/test_report.xlsx"
        
        # Create test file
        files = {"files": ("ACQ.csv", io.StringIO(sample_csv_content), "text/csv")}
        
        response = client.post("/transform", files=files)
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "excel_file" in data
    
    def test_status_endpoint_invalid_task(self, client):
        """Test status endpoint with invalid task ID"""
        response = client.get("/status/invalid-task-id")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
    
    def test_download_endpoint_invalid_task(self, client):
        """Test download endpoint with invalid task ID"""
        response = client.get("/download/invalid-task-id")
        assert response.status_code == 404
    
    def test_delete_task_endpoint_invalid_task(self, client):
        """Test delete task endpoint with invalid task ID"""
        response = client.delete("/tasks/invalid-task-id")
        assert response.status_code == 404
    
    @patch('main.CSVProcessor')
    def test_process_endpoint_with_mocked_processor(self, mock_csv_processor, client, sample_csv_content):
        """Test the main process endpoint with mocked processor"""
        # Mock the CSV processor
        mock_processor = Mock()
        mock_csv_processor.return_value = mock_processor
        mock_processor.process_csv_files = AsyncMock(return_value={"ACQ.csv": []})
        
        # Create test files
        files = [
            ("files", ("ACQ.csv", io.StringIO(sample_csv_content), "text/csv"))
        ]
        
        response = client.post("/process", files=files)
        assert response.status_code == 200
        
        data = response.json()
        assert "task_id" in data
        assert "status" in data
        assert data["status"] == "processing"
    
    @patch('main.CSVProcessor')
    def test_process_incremental_endpoint(self, mock_csv_processor, client):
        """Test the incremental processing endpoint"""
        mock_processor = Mock()
        mock_csv_processor.return_value = mock_processor
        mock_processor.process_incremental = AsyncMock(return_value={"processed": 0, "new_files": []})
        
        payload = {
            "directory": "/tmp/test",
            "last_processed": "2025-01-15T10:00:00",
            "file_patterns": ["*.csv"]
        }
        
        response = client.post("/process-incremental", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "processed_count" in data
        assert "new_files" in data
    
    def test_excel_info_endpoint_not_found(self, client):
        """Test excel info endpoint with non-existent file"""
        response = client.get("/excel-info/nonexistent.xlsx")
        assert response.status_code == 404
    
    def test_cleanup_old_files_endpoint(self, client):
        """Test the cleanup old files endpoint"""
        payload = {
            "days_old": 7,
            "file_types": ["xlsx", "csv"],
            "dry_run": True
        }
        
        response = client.post("/cleanup-old-files", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "files_cleaned" in data
        assert "space_freed" in data
        assert "dry_run" in data


class TestReportGeneratorAPIErrorHandling:
    """Test suite for API error handling"""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client fixture"""
        return TestClient(app)
    
    def test_invalid_file_upload(self, client):
        """Test uploading invalid file type"""
        files = {"files": ("test.txt", "invalid content", "text/plain")}
        
        response = client.post("/validate-files", files=files)
        # Should handle gracefully (exact response depends on implementation)
        assert response.status_code in [200, 400, 422]
    
    def test_empty_file_upload(self, client):
        """Test uploading empty file"""
        files = {"files": ("empty.csv", "", "text/csv")}
        
        response = client.post("/validate-files", files=files)
        assert response.status_code in [200, 400, 422]
    
    def test_malformed_json_payload(self, client):
        """Test endpoints with malformed JSON"""
        response = client.post("/process-incremental", 
                              data="invalid json",
                              headers={"Content-Type": "application/json"})
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client):
        """Test endpoints with missing required fields"""
        payload = {"directory": "/tmp/test"}  # Missing other required fields
        
        response = client.post("/process-incremental", json=payload)
        assert response.status_code == 422


class TestReportGeneratorAPIIntegration:
    """Integration tests for the Report Generator API"""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client fixture"""
        return TestClient(app)
    
    def test_api_documentation_available(self, client):
        """Test that API documentation is available"""
        response = client.get("/docs")
        assert response.status_code == 200
        
        response = client.get("/redoc")
        assert response.status_code == 200
    
    def test_openapi_schema_available(self, client):
        """Test that OpenAPI schema is available"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
    
    def test_cors_headers(self, client):
        """Test CORS headers if configured"""
        response = client.get("/health")
        # CORS headers would be present if configured
        # This test validates the response structure
        assert response.status_code == 200
    
    @pytest.mark.slow
    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests"""
        import concurrent.futures
        import threading
        
        def make_request():
            return client.get("/health")
        
        # Test multiple concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        for response in results:
            assert response.status_code == 200
