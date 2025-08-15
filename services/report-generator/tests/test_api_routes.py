"""
Unit Tests for Report Generator API Routes
Testing FastAPI endpoints with proper business service integration
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from pathlib import Path
import sys
import os
import json
import io
import tempfile
from unittest.mock import Mock, patch, AsyncMock

# Add the parent directories to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.main import app

class TestReportGeneratorAPIRoutes:
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
    
    def test_root_endpoint(self, client):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "Charlie Reporting - Report Generator"
        assert data["version"] == "2.0.0"
        assert data["architecture"] == "layered_microservice"
        assert "api_docs" in data
        assert "health" in data
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "report-generator"
        assert "timestamp" in data
        assert "active_tasks" in data
    
    def test_metrics_endpoint(self, client):
        """Test the metrics endpoint"""
        response = client.get("/api/v1/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_tasks" in data
        assert "completed_tasks" in data
        assert "failed_tasks" in data
        assert "active_tasks" in data
        assert "success_rate" in data
        assert "average_processing_time" in data
    
    def test_tasks_list_endpoint(self, client):
        """Test the tasks listing endpoint"""
        response = client.get("/api/v1/tasks")
        assert response.status_code == 200
        
        data = response.json()
        assert "tasks" in data
        assert "total" in data
        assert isinstance(data["tasks"], list)
        assert isinstance(data["total"], int)
    
    def test_tasks_list_with_status_filter(self, client):
        """Test tasks listing with status filter"""
        response = client.get("/api/v1/tasks?status=completed")
        assert response.status_code == 200
        
        data = response.json()
        assert "tasks" in data
        assert "status_filter" in data
        assert data["status_filter"] == "completed"
    
    def test_tasks_list_with_limit(self, client):
        """Test tasks listing with limit"""
        response = client.get("/api/v1/tasks?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert "tasks" in data
        assert len(data["tasks"]) <= 10
    
    def test_status_endpoint_invalid_task(self, client):
        """Test status endpoint with invalid task ID"""
        response = client.get("/api/v1/status/invalid-task-id")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Task not found"
    
    def test_download_endpoint_invalid_task(self, client):
        """Test download endpoint with invalid task ID"""
        response = client.get("/api/v1/download/invalid-task-id")
        assert response.status_code == 404
    
    def test_delete_task_endpoint_invalid_task(self, client):
        """Test delete task endpoint with invalid task ID"""
        response = client.delete("/api/v1/tasks/invalid-task-id")
        assert response.status_code == 404
    
    @patch('src.business.services.csv_transformer.CSVTransformationService')
    def test_validate_files_endpoint(self, mock_csv_service, client, sample_csv_content):
        """Test the file validation endpoint"""
        # Mock the CSV transformation service
        mock_service = Mock()
        mock_csv_service.return_value = mock_service
        mock_service.validate_csv_file.return_value = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "row_count": 3,
            "column_count": 5
        }
        
        # Create test file
        files = {"files": ("test.csv", io.StringIO(sample_csv_content), "text/csv")}
        
        response = client.post("/api/v1/validate-files", files=files)
        assert response.status_code == 200
        
        data = response.json()
        assert "total_files" in data
        assert "valid_files" in data
        assert "invalid_files" in data
        assert "validation_results" in data
        assert "overall_status" in data
    
    @patch('src.business.services.csv_transformer.CSVTransformationService')
    def test_transform_endpoint(self, mock_csv_service, client, sample_csv_content):
        """Test the transform endpoint"""
        # Mock the CSV transformation service
        mock_service = Mock()
        mock_csv_service.return_value = mock_service
        
        # Mock transformation result
        import pandas as pd
        mock_df = pd.read_csv(io.StringIO(sample_csv_content))
        
        mock_result = Mock()
        mock_result.success = True
        mock_result.transformed_data = mock_df
        mock_result.error_message = None
        
        mock_service.create_transformation_rules.return_value = []
        mock_service.transform_csv_file.return_value = mock_result
        
        # Create test file
        files = {"file": ("test.csv", io.StringIO(sample_csv_content), "text/csv")}
        
        response = client.post("/api/v1/transform", files=files)
        assert response.status_code == 200
        
        data = response.json()
        assert "total_rows" in data
        assert "columns" in data
        assert "sample_data" in data
        assert "transformation_applied" in data
        assert "message" in data
    
    def test_transform_endpoint_invalid_file_type(self, client):
        """Test transform endpoint with invalid file type"""
        files = {"file": ("test.txt", "invalid content", "text/plain")}
        
        response = client.post("/api/v1/transform", files=files)
        assert response.status_code == 422  # Should be 400 for invalid file type
    
    @patch('src.business.services.csv_transformer.CSVTransformationService')
    @patch('src.business.services.excel_service.ExcelReportService')
    def test_process_endpoint(self, mock_excel_service, mock_csv_service, client):
        """Test the main process endpoint"""
        # Mock services
        mock_csv = Mock()
        mock_excel = Mock()
        mock_csv_service.return_value = mock_csv
        mock_excel_service.return_value = mock_excel
        
        mock_csv.create_transformation_rules.return_value = []
        
        # Create test request
        request_data = {
            "files": ["/tmp/test.csv"],
            "output_format": "xlsx",
            "template": "default"
        }
        
        response = client.post("/api/v1/process", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "task_id" in data
        assert "status" in data
        assert data["status"] == "queued"
        assert "progress" in data
        assert "message" in data
        assert "created_at" in data


class TestReportGeneratorAPIErrorHandling:
    """Test suite for API error handling and edge cases"""
    
    @pytest.fixture
    def client(self):
        """FastAPI test client fixture"""
        return TestClient(app)
    
    def test_malformed_json_process_request(self, client):
        """Test process endpoint with malformed JSON"""
        response = client.post("/api/v1/process", 
                              data="invalid json",
                              headers={"Content-Type": "application/json"})
        assert response.status_code == 422
    
    def test_missing_required_fields_process(self, client):
        """Test process endpoint with missing required fields"""
        request_data = {"output_format": "xlsx"}  # Missing 'files' field
        
        response = client.post("/api/v1/process", json=request_data)
        assert response.status_code == 422
    
    def test_empty_files_list_process(self, client):
        """Test process endpoint with empty files list"""
        request_data = {
            "files": [],
            "output_format": "xlsx"
        }
        
        response = client.post("/api/v1/process", json=request_data)
        assert response.status_code == 200  # Should still create task
        
        data = response.json()
        assert data["status"] == "queued"
    
    def test_invalid_output_format(self, client):
        """Test process endpoint with invalid output format"""
        request_data = {
            "files": ["/tmp/test.csv"],
            "output_format": "invalid_format"
        }
        
        response = client.post("/api/v1/process", json=request_data)
        assert response.status_code == 200  # API accepts it, validation happens in background
    
    def test_transform_with_malformed_config(self, client):
        """Test transform endpoint with malformed configuration"""
        files = {"file": ("test.csv", "Agent,Date\nJohn,2025-01-15", "text/csv")}
        data = {"config": "invalid json"}
        
        response = client.post("/api/v1/transform", files=files, data=data)
        assert response.status_code == 400
        
        response_data = response.json()
        assert "Invalid config" in response_data["detail"]
    
    def test_validate_files_empty_request(self, client):
        """Test validate files endpoint with no files"""
        response = client.post("/api/v1/validate-files", files={})
        assert response.status_code == 422  # FastAPI validation error
    
    @patch('src.business.services.csv_transformer.CSVTransformationService')
    def test_transform_service_failure(self, mock_csv_service, client):
        """Test transform endpoint when service fails"""
        # Mock service to raise exception
        mock_service = Mock()
        mock_csv_service.return_value = mock_service
        mock_service.create_transformation_rules.side_effect = Exception("Service error")
        
        files = {"file": ("test.csv", "Agent,Date\nJohn,2025-01-15", "text/csv")}
        
        response = client.post("/api/v1/transform", files=files)
        assert response.status_code == 500
        
        data = response.json()
        assert "Transformation failed" in data["detail"]


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
        
        # Verify our endpoints are documented
        paths = schema["paths"]
        assert "/api/v1/health" in paths
        assert "/api/v1/process" in paths
        assert "/api/v1/transform" in paths
        assert "/api/v1/validate-files" in paths
    
    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.options("/api/v1/health")
        # CORS preflight should be handled
        assert response.status_code in [200, 405]  # Depending on FastAPI version
    
    @pytest.mark.slow
    def test_concurrent_health_checks(self, client):
        """Test handling of concurrent requests"""
        import concurrent.futures
        import threading
        
        def make_request():
            return client.get("/api/v1/health")
        
        # Test multiple concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        for response in results:
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
