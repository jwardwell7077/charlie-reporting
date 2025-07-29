# Windows Email Service Architecture

## Overview
A Windows service that handles Outlook email fetching via COM API and exposes a REST API for cross-platform access.

## Architecture Components

### 1. Windows Email Service
- **Technology**: Python with FastAPI or Flask
- **Deployment**: Windows Service using `python-windows-service` or `nssm`
- **Security**: Runs under service account with Outlook access
- **Location**: Windows server/workstation with Outlook installed

### 2. Main Application (Linux/Cross-platform)
- **Technology**: Current Python application
- **Communication**: HTTP REST client
- **Benefits**: Platform independent, no email dependencies

## API Design

### Base URL: `http://email-service-host:8080/api`

### Endpoints

#### Health & Status
```
GET /health
Response: {"status": "healthy", "outlook_connected": true, "version": "1.0.0"}

GET /status  
Response: {"current_operation": "idle", "last_fetch": "2025-07-28T14:30:00Z"}
```

#### Email Fetching
```
POST /emails/fetch
Body: {
  "date": "2025-07-28",
  "start_hour": 9,     // optional
  "end_hour": 17,      // optional
  "filters": {
    "sender": ["reports@example.com"],
    "subject_contains": ["Daily Report"]
  },
  "attachment_rules": {
    "IB_Calls.csv": {"columns": ["Agent Name"]},
    "Dials.csv": {"columns": ["Agent Name", "Handle"]}
  }
}
Response: {
  "success": true,
  "processed_emails": 5,
  "downloaded_attachments": 8,
  "files": [
    {"filename": "IB_Calls__2025-07-28_0900.csv", "size": 1024, "timestamp": "2025-07-28T09:00:00Z"},
    {"filename": "Dials__2025-07-28_0900.csv", "size": 2048, "timestamp": "2025-07-28T09:00:00Z"}
  ]
}

POST /emails/fetch-recent
Body: {"hours": 2, "filters": {...}, "attachment_rules": {...}}
Response: {same as above}
```

#### Account Management
```
GET /accounts
Response: {
  "accounts": [
    {"email": "user1@company.com", "display_name": "User One", "is_default": false},
    {"email": "user2@company.com", "display_name": "User Two", "is_default": true}
  ]
}
```

#### File Download
```
GET /files/{filename}
Response: Binary file content with appropriate headers

GET /files
Response: {
  "files": [
    {"filename": "IB_Calls__2025-07-28_0900.csv", "size": 1024, "created": "2025-07-28T09:00:00Z"},
    ...
  ]
}
```

## Security Considerations

### Authentication Options
1. **API Key**: Simple header-based auth
2. **Basic Auth**: Username/password 
3. **Certificate**: Mutual TLS for high security
4. **Network Isolation**: Run on internal network only

### Service Account Setup
- Dedicated Windows service account
- Outlook profile configured for service account
- Minimal required permissions
- Regular credential rotation

## Configuration

### Windows Service Config
```toml
[service]
port = 8080
host = "0.0.0.0"  # or specific IP
log_level = "INFO"
max_concurrent_requests = 5

[security]
api_key = "your-secure-api-key"
allowed_ips = ["192.168.1.0/24", "10.0.0.0/8"]

[outlook]
profile_name = "EmailService"
timeout_seconds = 30
retry_attempts = 3

[file_storage]
output_directory = "C:\\EmailService\\Output"
retention_days = 7
max_file_size_mb = 100
```

### Main App Config
```toml
[email_service]
url = "http://email-server.company.com:8080"
api_key = "your-secure-api-key"
timeout_seconds = 60
retry_attempts = 2

[fallback]
enabled = true
directory_scan_path = "/shared/network/emails"  # Network share fallback
```

## Deployment Strategy

### Phase 1: Windows Service Development
1. Create FastAPI service with Outlook COM integration
2. Implement core email fetching endpoints
3. Add file serving capabilities
4. Test on development machine

### Phase 2: Service Deployment
1. Install as Windows Service
2. Configure service account and Outlook profile
3. Set up network access and firewall rules
4. Implement monitoring and logging

### Phase 3: Main App Integration
1. Update EmailFetcher to use REST API
2. Add fallback mechanisms (directory scan, error handling)
3. Update configuration management
4. Test cross-platform functionality

## Benefits

### For Your Current Situation
- **Immediate cross-platform support** - Linux app can access Windows Outlook
- **Security compliance** - Email credentials stay on Windows service
- **Organizational acceptance** - Uses familiar Windows service model
- **Gradual migration** - Can implement incrementally

### Operational Benefits
- **Centralized email processing** - One service handles all email access
- **Better error handling** - Service can retry, queue, and recover
- **Audit trail** - All email access logged in one place
- **Resource efficiency** - One Outlook connection serves multiple clients

## Error Handling & Resilience

### Service-Side
- Connection pooling for Outlook
- Request queuing during high load
- Automatic retry for transient failures
- Health monitoring and automatic restart

### Client-Side  
- Circuit breaker pattern for service unavailability
- Fallback to directory scanning
- Request timeout and retry logic
- Graceful degradation

## Monitoring & Observability

### Metrics to Track
- Request count and response times
- Email processing success/failure rates
- Outlook connection status
- File download volumes
- Error rates by type

### Logging Strategy
- Service logs: email processing, errors, performance
- Client logs: API calls, fallback usage, errors
- Audit logs: access patterns, file downloads
