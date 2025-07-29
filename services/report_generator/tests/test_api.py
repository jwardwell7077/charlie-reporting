"""
Test FastAPI Report Generator Service
Comprehensive testing for the CSV processing and Excel generation microservice
"""
import pytest
import httpx
import asyncio
import json
import pandas as pd
import io
from pathlib import Path

# Service configuration
SERVICE_URL = "http://localhost:8001"

class TestReportGeneratorService:
    """Test suite for Report Generator microservice"""
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Test service health check"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SERVICE_URL}/health")
            assert response.status_code == 200
            
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "report-generator"
            assert "timestamp" in data
            assert "active_tasks" in data
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self):
        """Test root endpoint service information"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SERVICE_URL}/")
            assert response.status_code == 200
            
            data = response.json()
            assert data["service"] == "Charlie Reporting - Report Generator"
            assert data["version"] == "1.0.0"
            assert "endpoints" in data
    
    @pytest.mark.asyncio
    async def test_process_csv_files(self):
        """Test CSV file processing endpoint"""
        async with httpx.AsyncClient() as client:
            request_data = {
                "files": ["test_file_1.csv", "test_file_2.csv"],
                "output_format": "xlsx",
                "template": "standard"
            }
            
            response = await client.post(f"{SERVICE_URL}/process", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert "task_id" in data
            assert data["status"] == "queued"
            assert data["progress"] == 0
            assert "created_at" in data
            
            return data["task_id"]
    
    @pytest.mark.asyncio
    async def test_task_status_tracking(self):
        """Test task status tracking throughout processing"""
        async with httpx.AsyncClient() as client:
            # Start a processing task
            request_data = {
                "files": ["test_status_tracking.csv"],
                "output_format": "xlsx"
            }
            
            response = await client.post(f"{SERVICE_URL}/process", json=request_data)
            task_id = response.json()["task_id"]
            
            # Check initial status
            status_response = await client.get(f"{SERVICE_URL}/status/{task_id}")
            assert status_response.status_code == 200
            
            initial_status = status_response.json()
            assert initial_status["task_id"] == task_id
            assert initial_status["status"] in ["queued", "processing"]
            
            # Wait for processing to complete
            max_attempts = 20
            attempts = 0
            
            while attempts < max_attempts:
                await asyncio.sleep(1)
                status_response = await client.get(f"{SERVICE_URL}/status/{task_id}")
                current_status = status_response.json()
                
                if current_status["status"] in ["completed", "failed"]:
                    break
                    
                attempts += 1
            
            # Verify final status
            final_status = status_response.json()
            assert final_status["status"] == "completed"
            assert final_status["progress"] == 100
            assert final_status["output_file"] is not None
    
    @pytest.mark.asyncio
    async def test_download_report(self):
        """Test report download functionality"""
        async with httpx.AsyncClient() as client:
            # Start processing
            request_data = {
                "files": ["test_download.csv"],
                "output_format": "xlsx"
            }
            
            response = await client.post(f"{SERVICE_URL}/process", json=request_data)
            task_id = response.json()["task_id"]
            
            # Wait for completion
            max_attempts = 15
            for _ in range(max_attempts):
                await asyncio.sleep(1)
                status_response = await client.get(f"{SERVICE_URL}/status/{task_id}")
                if status_response.json()["status"] == "completed":
                    break
            
            # Test download
            download_response = await client.get(f"{SERVICE_URL}/download/{task_id}")
            assert download_response.status_code == 200
            
            download_data = download_response.json()
            assert "download_url" in download_data
            assert "filename" in download_data
            assert download_data["task_id"] == task_id
    
    @pytest.mark.asyncio
    async def test_csv_transformation(self):
        """Test CSV data transformation endpoint"""
        # Create test CSV data
        test_data = {
            'Agent': ['Alice', 'Bob', 'Alice', 'Charlie', 'Bob'],
            'Revenue': [1000, 1500, 1200, 1800, 1300],
            'Date': ['2024-01-01', '2024-01-01', '2024-01-02', '2024-01-01', '2024-01-02']
        }
        
        df = pd.DataFrame(test_data)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue().encode()
        
        # Test transformation config
        transform_config = {
            "group_by": ["Agent"],
            "aggregations": {"Revenue": "sum"},
            "sort_by": ["Agent"]
        }
        
        async with httpx.AsyncClient() as client:
            files = {"file": ("test.csv", csv_content, "text/csv")}
            data = {"config": json.dumps(transform_config)}
            
            response = await client.post(
                f"{SERVICE_URL}/transform",
                files=files,
                data=data
            )
            
            assert response.status_code == 200
            
            result = response.json()
            assert "original_rows" in result
            assert "columns" in result
            assert "sample_data" in result
            assert result["transformation_applied"] is True
            
            # Verify transformation results
            sample_data = result["sample_data"]
            assert len(sample_data) == 3  # 3 unique agents
            assert all("Agent" in row for row in sample_data)
            assert all("Revenue" in row for row in sample_data)
    
    @pytest.mark.asyncio
    async def test_list_tasks(self):
        """Test task listing functionality"""
        async with httpx.AsyncClient() as client:
            # Create a few tasks
            task_ids = []
            for i in range(3):
                request_data = {
                    "files": [f"test_list_{i}.csv"],
                    "output_format": "xlsx"
                }
                response = await client.post(f"{SERVICE_URL}/process", json=request_data)
                task_ids.append(response.json()["task_id"])
            
            # List all tasks
            response = await client.get(f"{SERVICE_URL}/tasks")
            assert response.status_code == 200
            
            data = response.json()
            assert "tasks" in data
            assert "total" in data
            assert data["total"] >= 3
            
            # Verify our tasks are in the list
            task_ids_in_response = [task["task_id"] for task in data["tasks"]]
            for task_id in task_ids:
                assert task_id in task_ids_in_response
    
    @pytest.mark.asyncio
    async def test_service_metrics(self):
        """Test service metrics endpoint"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SERVICE_URL}/metrics")
            assert response.status_code == 200
            
            metrics = response.json()
            required_metrics = [
                "total_tasks", "completed_tasks", "failed_tasks",
                "active_tasks", "success_rate", "average_processing_time"
            ]
            
            for metric in required_metrics:
                assert metric in metrics
                assert isinstance(metrics[metric], (int, float))
            
            # Verify success rate is between 0 and 1
            assert 0.0 <= metrics["success_rate"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_invalid_task_id(self):
        """Test handling of invalid task IDs"""
        async with httpx.AsyncClient() as client:
            fake_task_id = "invalid-task-id-12345"
            
            # Test status endpoint
            response = await client.get(f"{SERVICE_URL}/status/{fake_task_id}")
            assert response.status_code == 404
            
            # Test download endpoint
            response = await client.get(f"{SERVICE_URL}/download/{fake_task_id}")
            assert response.status_code == 404
            
            # Test delete endpoint
            response = await client.delete(f"{SERVICE_URL}/tasks/{fake_task_id}")
            assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_invalid_csv_transformation(self):
        """Test error handling for invalid CSV transformation"""
        # Test with non-CSV file
        async with httpx.AsyncClient() as client:
            files = {"file": ("test.txt", b"Not a CSV file", "text/plain")}
            
            response = await client.post(f"{SERVICE_URL}/transform", files=files)
            assert response.status_code == 400
            assert "Only CSV files are allowed" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_invalid_transformation_config(self):
        """Test error handling for invalid transformation config"""
        # Create valid CSV
        test_data = {'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']}
        df = pd.DataFrame(test_data)
        csv_content = df.to_csv(index=False).encode()
        
        async with httpx.AsyncClient() as client:
            files = {"file": ("test.csv", csv_content, "text/csv")}
            data = {"config": "invalid json"}
            
            response = await client.post(
                f"{SERVICE_URL}/transform",
                files=files,
                data=data
            )
            
            assert response.status_code == 400
            assert "Invalid config" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_delete_completed_task(self):
        """Test deletion of completed tasks"""
        async with httpx.AsyncClient() as client:
            # Create and complete a task
            request_data = {"files": ["test_delete.csv"], "output_format": "xlsx"}
            response = await client.post(f"{SERVICE_URL}/process", json=request_data)
            task_id = response.json()["task_id"]
            
            # Wait for completion
            max_attempts = 15
            for _ in range(max_attempts):
                await asyncio.sleep(1)
                status_response = await client.get(f"{SERVICE_URL}/status/{task_id}")
                if status_response.json()["status"] == "completed":
                    break
            
            # Delete the task
            delete_response = await client.delete(f"{SERVICE_URL}/tasks/{task_id}")
            assert delete_response.status_code == 200
            
            # Verify task is deleted
            status_response = await client.get(f"{SERVICE_URL}/status/{task_id}")
            assert status_response.status_code == 404

@pytest.mark.performance
class TestReportGeneratorPerformance:
    """Performance tests for Report Generator service"""
    
    @pytest.mark.asyncio
    async def test_concurrent_processing(self):
        """Test concurrent task processing"""
        async with httpx.AsyncClient() as client:
            # Start multiple tasks concurrently
            tasks = []
            num_concurrent_tasks = 5
            
            for i in range(num_concurrent_tasks):
                request_data = {
                    "files": [f"concurrent_test_{i}.csv"],
                    "output_format": "xlsx"
                }
                task = client.post(f"{SERVICE_URL}/process", json=request_data)
                tasks.append(task)
            
            # Wait for all tasks to start
            responses = await asyncio.gather(*tasks)
            task_ids = [r.json()["task_id"] for r in responses]
            
            # Verify all tasks were created
            assert len(task_ids) == num_concurrent_tasks
            for response in responses:
                assert response.status_code == 200
            
            # Wait for all tasks to complete
            max_wait_time = 30  # seconds
            completed_tasks = 0
            
            for _ in range(max_wait_time):
                await asyncio.sleep(1)
                completed_count = 0
                
                for task_id in task_ids:
                    status_response = await client.get(f"{SERVICE_URL}/status/{task_id}")
                    if status_response.json()["status"] == "completed":
                        completed_count += 1
                
                if completed_count == num_concurrent_tasks:
                    completed_tasks = completed_count
                    break
            
            assert completed_tasks == num_concurrent_tasks
    
    @pytest.mark.asyncio
    async def test_large_csv_transformation(self):
        """Test transformation of large CSV data"""
        # Generate large dataset
        large_data = {
            'Agent': [f'Agent_{i%10}' for i in range(1000)],
            'Revenue': [1000 + (i * 10) for i in range(1000)],
            'Date': ['2024-01-01' for _ in range(1000)]
        }
        
        df = pd.DataFrame(large_data)
        csv_content = df.to_csv(index=False).encode()
        
        transform_config = {
            "group_by": ["Agent"],
            "aggregations": {"Revenue": "sum"}
        }
        
        import time
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            files = {"file": ("large_test.csv", csv_content, "text/csv")}
            data = {"config": json.dumps(transform_config)}
            
            response = await client.post(
                f"{SERVICE_URL}/transform",
                files=files,
                data=data
            )
            
            processing_time = time.time() - start_time
            
            assert response.status_code == 200
            assert processing_time < 10.0  # Should complete within 10 seconds
            
            result = response.json()
            assert result["original_rows"] == 10  # Grouped by 10 agents
            assert result["transformation_applied"] is True
