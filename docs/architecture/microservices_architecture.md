# Charlie Reporting - Microservices Architecture Design

## Overview
A distributed microservices architecture for email-based reporting pipeline with clear separation of concerns, REST API communication, and horizontal scalability.

## Architecture Components

```text
┌──────────────────┐      ┌────────────────────┐      ┌────────────────────┐
│ Outlook Relay    │─────▶│    DB Service      │◀─────│  Email Service     │
│   Service        │ REST │  (Data Backend)    │ REST │  (Outbound Mail)   │
└──────────────────┘      └────────────────────┘      └────────────────────┘
        │                         ▲   ▲                         ▲
        │ REST                    │   │ REST                    │ REST
        ▼                         │   │                         │
┌──────────────────┐               │   │                 ┌──────────────────┐
│ Scheduler /      │───────────────┘   └─────────────────│ Report Generator │
│ User Console     │ REST                     REST       │    Service       │
│ (Orchestrator)   │                                     │ (Excel Builder)  │
└──────────────────┘                                     └──────────────────┘
        │                                                         │
        │ REST                                           ┌────────▼────────┐
        └────────────────────────────────────────────────│ File Storage    │
                                                         │ (Local/OneDrive)│
                                                         └─────────────────┘
```text

## Service Definitions

### 1. Outlook Relay Service
**Purpose**: Thin proxy for Outlook/Exchange email operations
**Port**: 8080
**Platform**: Windows (COM) or Cross-platform (Graph API)

**Responsibilities**:
- Authenticate to Outlook/Exchange (pywin32 COM or Microsoft Graph)
- Fetch emails and CSV attachments for specified date/time ranges
- Forward CSV data and metadata to DB Service via REST
- Send outbound emails on behalf of Email Service
- Handle multiple Outlook accounts and profiles

**API Endpoints**:
```text
GET  /health                          # Service health and Outlook connectivity
POST /emails/fetch                    # Fetch emails by date/filters
POST /emails/send                     # Send outbound emails
GET  /accounts                        # List available email accounts
POST /attachments/extract             # Extract and forward attachments to DB Service
```text

### 2. DB Service  
**Purpose**: Canonical data backend with REST API
**Port**: 8081
**Platform**: Cross-platform

**Responsibilities**:
- Expose REST API for CRUD operations on reporting data
- Deduplicate incoming CSV rows based on configurable keys
- Apply transformations, lookups, and data validation
- Manage table schemas (one table per report type: IB_Calls, Dials, etc.)
- Serve query endpoints for Report Generator
- Handle data archiving and retention policies

**API Endpoints**:
```text
POST /data/ingest                     # Ingest CSV data from Outlook Relay
GET  /data/query                      # Query data for report generation
GET  /data/schemas                    # Get available data schemas
POST /data/transform                  # Apply transformations to raw data
GET  /data/stats                      # Data statistics and health metrics
DELETE /data/cleanup                  # Archive old data
```text

### 3. Scheduler Service / User Console
**Purpose**: Central orchestrator and user interface
**Port**: 8082
**Platform**: Cross-platform

**Responsibilities**:
- Provide CLI and web console for pipeline management
- Schedule daily fetch/transform/report/email jobs
- Handle manual job triggers and reruns
- Orchestrate service communication and workflow
- Track job history, status, and error recovery
- Provide real-time monitoring dashboard

**API Endpoints**:
```text
POST /jobs/schedule                   # Schedule recurring jobs
POST /jobs/trigger                    # Trigger manual job runs
GET  /jobs/status/{job_id}           # Get job status and logs
GET  /jobs/history                    # Job execution history
POST /jobs/cancel/{job_id}           # Cancel running job
GET  /dashboard                       # Web dashboard (HTML)
```text

### 4. Report Generator Service
**Purpose**: Excel report building and file management
**Port**: 8083
**Platform**: Cross-platform

**Responsibilities**:
- Generate Excel workbooks with multiple sheets per report type
- Query DB Service for precise data slices needed
- Apply Excel formatting, charts, and conditional formatting
- Save reports to local filesystem, OneDrive, or SharePoint
- Archive previous versions with retention policies
- Hand off generated files to Email Service for distribution

**API Endpoints**:
```text
POST /reports/generate               # Generate report for specific date
GET  /reports/templates              # Available report templates
GET  /reports/files                  # List generated report files
GET  /reports/download/{filename}    # Download specific report
POST /reports/archive                # Archive old reports
```text

### 5. Email Service
**Purpose**: Outbound email delivery and templating
**Port**: 8084
**Platform**: Cross-platform

**Responsibilities**:
- Receive report files and recipient lists from Report Generator
- Compose emails using configurable templates
- Attach Excel files and handle large attachments
- Send via Outlook Relay Service (unified email sending)
- Track delivery status and bounce handling
- Provide delivery notifications to Scheduler Service

**API Endpoints**:
```text
POST /emails/send-reports            # Send reports via email
GET  /emails/templates               # Email template management
GET  /emails/status/{email_id}       # Email delivery status
POST /emails/templates/create        # Create/update email templates
GET  /emails/delivery-log            # Email delivery history
```text

## Data Flow Scenarios

### Daily Automated Run
```text
1. Scheduler triggers daily job at 6:00 AM
2. Scheduler → Outlook Relay: "Fetch CSVs for yesterday"
3. Outlook Relay → DB Service: "Store these CSV files" (POST /data/ingest)
4. DB Service processes, dedupes, transforms data
5. Scheduler → Report Generator: "Generate reports for yesterday"
6. Report Generator → DB Service: "Query data for reports" (GET /data/query)
7. Report Generator builds Excel files, stores to filesystem/OneDrive
8. Report Generator → Email Service: "Send these reports to recipients"
9. Email Service → Outlook Relay: "Send these emails with attachments"
10. Email Service → Scheduler: "Delivery complete" (status callback)
```text

### Manual Reprocessing
```text
1. User via Console: "Reprocess data for 2025-07-15"
2. Scheduler → DB Service: "Clear data for 2025-07-15"
3. Scheduler → Outlook Relay: "Re-fetch emails for 2025-07-15"
4. [Standard flow continues from step 3 above]
```text

### Hourly Incremental Updates
```text
1. Scheduler triggers hourly job
2. Outlook Relay fetches last hour's emails
3. DB Service merges new data with existing
4. Report Generator updates live dashboard reports
5. Email Service sends alerts if thresholds exceeded
```text

## Service Configuration

### Inter-Service Communication
```toml
# Each service maintains registry of other services
[services]
outlook_relay = "http://email-server:8080"
db_service = "http://db-server:8081"  
scheduler = "http://scheduler-server:8082"
report_generator = "http://reports-server:8083"
email_service = "http://email-server:8084"

[security]
api_key = "shared-service-key"
inter_service_timeout = 30
retry_attempts = 3
```text

### Service Discovery & Health Monitoring
```toml
[health_check]
interval_seconds = 30
endpoints = [
    "http://outlook-relay:8080/health",
    "http://db-service:8081/health", 
    "http://scheduler:8082/health",
    "http://report-generator:8083/health",
    "http://email-service:8084/health"
]
```text

## Technology Stack by Service

### Outlook Relay Service (Windows/Cross-platform)
- **Framework**: FastAPI (Python)
- **Email**: pywin32 (Windows) or Microsoft Graph API (Cross-platform)
- **Deployment**: Windows Service or Docker container

### DB Service
- **Framework**: FastAPI (Python)
- **Database**: SQLite (dev) → PostgreSQL (production)
- **ORM**: SQLAlchemy
- **Migrations**: Alembic

### Scheduler Service
- **Framework**: FastAPI (Python) + APScheduler
- **Frontend**: HTML/JavaScript dashboard
- **Queue**: Redis or in-memory (simple deployments)

### Report Generator Service  
- **Framework**: FastAPI (Python)
- **Excel**: openpyxl or xlsxwriter
- **Storage**: Local filesystem, OneDrive API, or SharePoint

### Email Service
- **Framework**: FastAPI (Python)
- **Templates**: Jinja2
- **Delivery**: Via Outlook Relay Service (unified sending)

## Deployment Options

### Option 1: Single Machine Development
```bash
# All services on localhost with different ports
python outlook_relay_service.py    # Port 8080
python db_service.py              # Port 8081  
python scheduler_service.py       # Port 8082
python report_generator_service.py # Port 8083
python email_service.py           # Port 8084
```text

### Option 2: Docker Compose
```yaml
# docker-compose.yml
services:
  outlook-relay:
    build: ./services/outlook-relay
    ports: ["8080:8080"]
    
  db-service:
    build: ./services/db-service
    ports: ["8081:8081"]
    volumes: ["./data:/app/data"]
    
  scheduler:
    build: ./services/scheduler
    ports: ["8082:8082"]
    
  report-generator:
    build: ./services/report-generator
    ports: ["8083:8083"]
    volumes: ["./reports:/app/reports"]
    
  email-service:
    build: ./services/email-service
    ports: ["8084:8084"]
```text

### Option 3: Distributed Deployment
- Outlook Relay: Windows server with Outlook
- DB Service: Linux server with PostgreSQL
- Scheduler: Linux server (central orchestrator)
- Report Generator: Linux server with file storage
- Email Service: Linux server

## Benefits of This Architecture

### Scalability
- **Horizontal scaling**: Each service can be scaled independently
- **Load distribution**: Multiple instances of CPU-intensive services
- **Resource optimization**: Right-size each service for its workload

### Maintainability  
- **Clear boundaries**: Each service has single responsibility
- **Independent deployment**: Update services without affecting others
- **Technology flexibility**: Different services can use different tech stacks

### Reliability
- **Fault isolation**: One service failure doesn't bring down entire system
- **Circuit breakers**: Services can gracefully handle downstream failures
- **Retry logic**: Built-in resilience for inter-service communication

### Extensibility
- **Plugin architecture**: Easy to add new report types or data sources
- **API-first**: All functionality exposed via REST APIs
- **Integration ready**: External systems can easily integrate

## Migration Strategy

### Phase 1: Extract Outlook Relay (Week 1-2)
1. Create standalone Outlook Relay Service
2. Update existing EmailFetcher to use REST API
3. Test cross-platform compatibility

### Phase 2: Extract DB Service (Week 3-4)  
1. Create DB Service with current data models
2. Migrate existing CSV processing logic
3. Update Outlook Relay to use DB Service API

### Phase 3: Extract Report Generator (Week 5-6)
1. Move Excel generation logic to standalone service
2. Implement file storage and archiving
3. Connect to DB Service for data queries

### Phase 4: Extract Email Service (Week 7-8)
1. Create email templating and delivery service
2. Integrate with Outlook Relay for actual sending
3. Add delivery tracking and status reporting

### Phase 5: Create Scheduler Service (Week 9-10)
1. Build orchestration and job scheduling
2. Add web dashboard for monitoring
3. Implement job history and error recovery

### Phase 6: Production Hardening (Week 11-12)
1. Add comprehensive error handling and logging
2. Implement health checks and monitoring
3. Create deployment automation and documentation

## Future Extensions

### Potential Additions
- **Web Dashboard Service**: Rich web UI for reporting and analytics
- **Notification Service**: Slack, Teams, SMS alerts  
- **API Gateway**: Centralized authentication and rate limiting
- **Configuration Service**: Centralized config management
- **Metrics Service**: Prometheus/Grafana monitoring
- **File Service**: Dedicated file storage with CDN capabilities
