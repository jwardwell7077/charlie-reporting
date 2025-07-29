# Charlie Reporting - Implementation Roadmap

## Phase 1: Foundation Setup (Week 1)

### 1.1 Project Structure Creation
```bash
# Create new microservices directory structure
mkdir -p services/{outlook-relay,db-service,scheduler,report-generator,email-service}
mkdir -p shared config scripts docs/api tests/integration
mkdir -p monitoring/{prometheus,grafana,logging}
```

### 1.2 Shared Components
- **shared/service_client.py** - Base HTTP client for inter-service communication
- **shared/models.py** - Common Pydantic models (Email, Report, Job, etc.)
- **shared/auth.py** - API key authentication middleware
- **shared/logging_config.py** - Standardized logging setup
- **shared/exceptions.py** - Custom exception hierarchy

### 1.3 Configuration Management
- **config/services.toml** - Service registry and URLs
- **config/development.toml** - Local development settings
- **.env.example** - Environment variables template

## Phase 2: Outlook Relay Service (Week 2)

### 2.1 Core Implementation
```python
# services/outlook-relay/app/main.py
from fastapi import FastAPI, Depends, HTTPException
from .outlook_client import OutlookClient
from .routes import emails, health, accounts

app = FastAPI(title="Outlook Relay Service")
app.include_router(health.router, prefix="/health")
app.include_router(emails.router, prefix="/api/emails")
app.include_router(accounts.router, prefix="/api/accounts")
```

### 2.2 Key Endpoints
- `POST /api/emails/fetch` - Fetch emails by date/time range
- `POST /api/emails/send` - Send emails via Outlook
- `GET /api/accounts` - List available email accounts
- `GET /health` - Service health check

### 2.3 Integration Points
- Forward CSV attachments to DB Service
- Accept send requests from Email Service
- Support both COM (Windows) and Graph API (cross-platform)

## Phase 3: DB Service (Week 3)

### 3.1 Database Models
```python
# services/db-service/app/models.py
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class EmailData(Base):
    __tablename__ = "email_data"
    id = Column(Integer, primary_key=True)
    filename = Column(String, index=True)
    report_type = Column(String, index=True)  # IB_Calls, Dials, etc.
    date_received = Column(DateTime, index=True)
    data_json = Column(Text)  # JSON blob of CSV data
    processed = Column(Boolean, default=False)
```

### 3.2 Key Endpoints
- `POST /api/data/ingest` - Receive CSV data from Outlook Relay
- `GET /api/data/query` - Query data for Report Generator
- `GET /api/data/schemas` - Available data schemas
- `POST /api/data/transform` - Apply data transformations

### 3.3 Features
- Automatic deduplication based on configurable keys
- Data validation and schema enforcement
- Archival and retention policies
- Query optimization for report generation

## Phase 4: Basic Scheduler Service (Week 4)

### 4.1 Job Management
```python
# services/scheduler/app/job_manager.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .service_client import ServiceClient

class JobManager:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.outlook_client = ServiceClient("outlook-relay")
        self.db_client = ServiceClient("db-service")
    
    async def daily_job(self, date: str):
        # 1. Fetch emails
        # 2. Wait for data ingestion
        # 3. Trigger report generation
        # 4. Send reports
```

### 4.2 Key Endpoints
- `POST /api/jobs/schedule` - Schedule recurring jobs
- `POST /api/jobs/trigger` - Manual job execution
- `GET /api/jobs/status/{job_id}` - Job status and logs
- `GET /api/jobs/history` - Execution history

### 4.3 Orchestration Logic
- Coordinate service calls in proper sequence
- Handle failures and retries
- Provide job status updates
- Simple web dashboard for monitoring

## Phase 5: Report Generator Service (Week 5)

### 5.1 Excel Generation
```python
# services/report-generator/app/excel_builder.py
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from .service_client import ServiceClient

class ExcelBuilder:
    def __init__(self):
        self.db_client = ServiceClient("db-service")
    
    async def generate_daily_report(self, date: str) -> str:
        # Query data from DB Service
        # Apply Excel formatting
        # Save to file storage
        # Return file path
```

### 5.2 Key Endpoints
- `POST /api/reports/generate` - Generate reports for date
- `GET /api/reports/templates` - Available report templates
- `GET /api/reports/files` - List generated files
- `GET /api/reports/download/{filename}` - Download report

### 5.3 Features
- Multiple report formats (daily, hourly, summary)
- Excel templating with conditional formatting
- File storage abstraction (local, OneDrive, SharePoint)
- Report archival and cleanup

## Phase 6: Email Service (Week 6)

### 6.1 Email Templating
```python
# services/email-service/app/template_engine.py
from jinja2 import Environment, FileSystemLoader

class EmailTemplateEngine:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader('templates'))
    
    def render_report_email(self, report_data: dict) -> str:
        template = self.env.get_template('daily_report.html')
        return template.render(**report_data)
```

### 6.2 Key Endpoints
- `POST /api/emails/send-reports` - Send reports with attachments
- `GET /api/emails/templates` - Email template management
- `GET /api/emails/status/{email_id}` - Delivery status
- `GET /api/emails/delivery-log` - Delivery history

### 6.3 Features
- HTML email templates with Jinja2
- Large attachment handling
- Delivery tracking and status callbacks
- Email template management interface

## Phase 7: Integration & Testing (Week 7)

### 7.1 Service Communication Testing
```python
# tests/integration/test_service_communication.py
import pytest
import asyncio
from shared.service_client import ServiceClient

@pytest.mark.asyncio
async def test_full_pipeline():
    # Start all services
    # Trigger job via Scheduler
    # Verify data flow through all services
    # Check final email delivery
```

### 7.2 Error Scenario Testing
- Service unavailability handling
- Network timeouts and retries
- Data validation failures
- Email delivery failures

### 7.3 Performance Testing
- Concurrent job execution
- Large data volume handling
- Service response times under load

## Phase 8: Production Hardening (Week 8)

### 8.1 Monitoring Setup
```yaml
# monitoring/prometheus/prometheus.yml
scrape_configs:
  - job_name: 'outlook-relay'
    static_configs:
      - targets: ['outlook-relay:8080']
  - job_name: 'db-service'
    static_configs:
      - targets: ['db-service:8081']
```

### 8.2 Logging Standardization
- Structured logging with correlation IDs
- Centralized log aggregation
- Error alerting and notifications

### 8.3 Deployment Automation
- Docker Compose for development
- Production deployment scripts
- Health check monitoring
- Backup and recovery procedures

## Migration Strategy from Current System

### Step 1: Extract Outlook Relay (Week 2)
1. Create Outlook Relay Service
2. Update current `EmailFetcher` to use REST API
3. Test with existing functionality
4. Deploy side-by-side with current system

### Step 2: Extract Data Layer (Week 3)
1. Create DB Service with current data models
2. Migrate CSV processing logic
3. Update Outlook Relay to forward data
4. Verify data consistency

### Step 3: Extract Report Generation (Week 5)
1. Move Excel generation to Report Generator Service
2. Connect to DB Service for data queries
3. Test report quality and formatting
4. Update file storage paths

### Step 4: Extract Email Sending (Week 6)
1. Create Email Service with current templates
2. Route outbound emails through Email Service
3. Test email delivery and formatting
4. Implement delivery tracking

### Step 5: Add Orchestration (Week 4 & 7)
1. Implement Scheduler Service
2. Migrate job scheduling logic
3. Add web dashboard for monitoring
4. Test end-to-end automation

## Configuration Examples

### Development Environment
```bash
# .env
API_KEY=dev-api-key-12345
DB_URL=sqlite:///./data/charlie.db
LOG_LEVEL=DEBUG
OUTLOOK_RELAY_URL=http://localhost:8080
DB_SERVICE_URL=http://localhost:8081
SCHEDULER_URL=http://localhost:8082
REPORT_GENERATOR_URL=http://localhost:8083
EMAIL_SERVICE_URL=http://localhost:8084
```

### Production Environment
```bash
# .env.production
API_KEY=${SECURE_API_KEY}
DB_URL=postgresql://user:pass@db-server:5432/charlie
LOG_LEVEL=INFO
OUTLOOK_RELAY_URL=https://outlook-relay.company.com
DB_SERVICE_URL=https://db-service.company.com
SCHEDULER_URL=https://scheduler.company.com
REPORT_GENERATOR_URL=https://reports.company.com
EMAIL_SERVICE_URL=https://email.company.com
```

## Success Metrics

### Technical Metrics
- **Service Uptime**: >99.5% for each service
- **API Response Time**: <2s for 95th percentile
- **Job Success Rate**: >99% for scheduled jobs
- **Data Processing Latency**: <5 minutes for daily jobs

### Business Metrics
- **Report Delivery Time**: Consistent 6 AM delivery
- **Data Accuracy**: Zero data loss or corruption
- **Error Recovery**: Automatic retry and notification
- **User Satisfaction**: Simplified manual operations

## Next Steps

1. **Review Architecture** - Validate service boundaries and APIs
2. **Choose Starting Point** - Begin with Outlook Relay or DB Service
3. **Set Up Development Environment** - Docker Compose for local testing
4. **Create Service Templates** - Standardized FastAPI service structure
5. **Implement First Service** - Prove the architecture with working code

Would you like me to start implementing any specific service, or should we dive deeper into a particular aspect of the architecture?
