# Charlie Reporting API Framework

# Phase 2: Microservices Architecture Implementation

## API Service Templates

### 1. Report Generator Service (FastAPI)

```python
# services/report_generator/main.py
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from pathlib import Path
import uuid

app = FastAPI(
    title="Charlie Reporting - Report Generator",
    description="Microservice for CSV processing and Excel report generation",
    version="1.0.0"
)

class ReportRequest(BaseModel):
    files: List[str]
    output_format: str = "xlsx"
    template: Optional[str] = None
    
class ProcessingStatus(BaseModel):
    task_id: str
    status: str
    progress: int
    message: str

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "report-generator"}

@app.post("/process", response_model=ProcessingStatus)
async def process_csv_files(request: ReportRequest):
    """Process CSV files and generate Excel reports"""
    task_id = str(uuid.uuid4())
    
    try:
        # Process CSV files (implementation from Phase 1)
        # Transform data using existing business logic
        # Generate Excel reports
        
        return ProcessingStatus(
            task_id=task_id,
            status="completed",
            progress=100,
            message="Report generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{task_id}")
async def get_processing_status(task_id: str):
    """Get processing status for a task"""
    # Implementation for status tracking
    pass

@app.get("/download/{task_id}")
async def download_report(task_id: str):
    """Download generated report"""
    # Implementation for file download
    pass
```

### 2. File Management Service

```python
# services/file_manager/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import shutil
from pathlib import Path
import uuid

app = FastAPI(
    title="Charlie Reporting - File Manager",
    description="Microservice for file upload, storage, and management",
    version="1.0.0"
)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload CSV file for processing"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    file_id = str(uuid.uuid4())
    file_path = Path(f"uploads/{file_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"file_id": file_id, "filename": file.filename, "status": "uploaded"}

@app.get("/files")
async def list_files():
    """List all uploaded files"""
    # Implementation for file listing
    pass

@app.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """Delete uploaded file"""
    # Implementation for file deletion
    pass
```

### 3. Notification Service

```python
# services/notification/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = FastAPI(
    title="Charlie Reporting - Notification Service",
    description="Microservice for email notifications and alerts",
    version="1.0.0"
)

class EmailNotification(BaseModel):
    recipients: List[EmailStr]
    subject: str
    body: str
    attachment_path: str = None

@app.post("/send-email")
async def send_email_notification(notification: EmailNotification):
    """Send email notification with optional attachment"""
    try:
        # Email sending logic (from Phase 1)
        return {"status": "sent", "recipients": notification.recipients}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-report")
async def send_report_notification(report_id: str, recipients: List[EmailStr]):
    """Send report completion notification"""
    # Implementation for report notifications
    pass
```

## API Gateway Configuration

```python
# api_gateway/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(
    title="Charlie Reporting API Gateway",
    description="Central API gateway for all microservices",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
SERVICES = {
    "report_generator": "http://localhost:8001",
    "file_manager": "http://localhost:8002",
    "notification": "http://localhost:8003"
}

@app.get("/health")
async def health_check():
    """Health check for all services"""
    status = {}
    async with httpx.AsyncClient() as client:
        for service, url in SERVICES.items():
            try:
                response = await client.get(f"{url}/health", timeout=5.0)
                status[service] = "healthy" if response.status_code == 200 else "unhealthy"
            except:
                status[service] = "unreachable"
    
    return {"gateway": "healthy", "services": status}
```

## Docker Configuration

### Report Generator Service

```dockerfile
# services/report_generator/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api-gateway:
    build: ./api_gateway
    ports:
      - "8000:8000"
    depends_on:
      - report-generator
      - file-manager
      - notification-service

  report-generator:
    build: ./services/report_generator
    ports:
      - "8001:8001"
    volumes:
      - ./data:/app/data

  file-manager:
    build: ./services/file_manager
    ports:
      - "8002:8002"
    volumes:
      - ./uploads:/app/uploads

  notification-service:
    build: ./services/notification
    ports:
      - "8003:8003"
```

## API Testing Framework

```python
# tests/api/test_integration.py
import pytest
import httpx
from pathlib import Path

@pytest.mark.asyncio
async def test_complete_api_workflow():
    """Test complete workflow through API"""
    async with httpx.AsyncClient() as client:
        # 1. Upload CSV file
        files = {"file": ("test.csv", open("test_data.csv", "rb"), "text/csv")}
        upload_response = await client.post("http://localhost:8002/upload", files=files)
        assert upload_response.status_code == 200
        
        # 2. Process file
        process_data = {
            "files": [upload_response.json()["file_id"]],
            "output_format": "xlsx"
        }
        process_response = await client.post("http://localhost:8001/process", json=process_data)
        assert process_response.status_code == 200
        
        # 3. Send notification
        notification_data = {
            "recipients": ["test@example.com"],
            "subject": "Report Ready",
            "body": "Your report has been generated."
        }
        notify_response = await client.post("http://localhost:8003/send-email", json=notification_data)
        assert notify_response.status_code == 200
```

## Development Workflow

### 1. Local Development

```bash
# Start all services
docker-compose up -d

# Run tests
pytest tests/api/ -v

# Check service health
curl http://localhost:8000/health
```

### 2. Service Development

```bash
# Develop individual service
cd services/report_generator
uvicorn main:app --reload --port 8001

# Test service endpoints
curl http://localhost:8001/health
```

### 3. API Documentation

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

This API framework provides:

- Microservices architecture
- Service discovery and health checks
- Comprehensive API documentation
- Docker containerization
- Integration testing framework
- Scalable deployment structure
