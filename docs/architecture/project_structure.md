# Charlie Reporting - Microservices Project Structure

```
charlie-reporting/
├── README.md
├── docker-compose.yml                    # Multi-service deployment
├── requirements.txt                      # Shared dependencies
├── .env.example                         # Environment variables template
├── pyproject.toml                       # Project metadata and build config
│
├── services/                            # Individual microservices
│   ├── outlook-relay/                   # Service 1: Email proxy
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py                  # FastAPI app
│   │   │   ├── models.py                # Pydantic models
│   │   │   ├── outlook_client.py        # COM/Graph API wrapper
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── health.py
│   │   │   │   ├── emails.py
│   │   │   │   └── accounts.py
│   │   │   └── config.py
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── config.toml
│   │   └── tests/
│   │       ├── test_outlook_client.py
│   │       └── test_routes.py
│   │
│   ├── db-service/                      # Service 2: Data backend
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── models.py                # SQLAlchemy models
│   │   │   ├── database.py              # DB connection & session
│   │   │   ├── crud.py                  # Database operations
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── health.py
│   │   │   │   ├── data.py
│   │   │   │   └── schemas.py
│   │   │   └── migrations/              # Alembic migrations
│   │   │       └── versions/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── alembic.ini
│   │   └── tests/
│   │       ├── test_crud.py
│   │       └── test_routes.py
│   │
│   ├── scheduler/                       # Service 3: Orchestrator
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── scheduler.py             # APScheduler integration
│   │   │   ├── job_manager.py           # Job execution logic
│   │   │   ├── service_client.py        # Inter-service communication
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── jobs.py
│   │   │   │   ├── dashboard.py
│   │   │   │   └── health.py
│   │   │   └── templates/               # Web dashboard templates
│   │   │       ├── dashboard.html
│   │   │       └── job_status.html
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── tests/
│   │       ├── test_scheduler.py
│   │       └── test_job_manager.py
│   │
│   ├── report-generator/                # Service 4: Excel builder
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── excel_builder.py         # Excel generation logic
│   │   │   ├── template_manager.py      # Report templates
│   │   │   ├── file_storage.py          # File storage abstraction
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── reports.py
│   │   │   │   ├── templates.py
│   │   │   │   └── health.py
│   │   │   └── templates/               # Excel templates
│   │   │       ├── daily_report.xlsx
│   │   │       └── hourly_summary.xlsx
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── tests/
│   │       ├── test_excel_builder.py
│   │       └── test_routes.py
│   │
│   └── email-service/                   # Service 5: Outbound email
│       ├── app/
│       │   ├── __init__.py
│       │   ├── main.py
│       │   ├── email_client.py          # Email sending logic
│       │   ├── template_engine.py       # Jinja2 templates
│       │   ├── delivery_tracker.py      # Track email status
│       │   ├── routes/
│       │   │   ├── __init__.py
│       │   │   ├── emails.py
│       │   │   ├── templates.py
│       │   │   └── health.py
│       │   └── templates/               # Email templates
│       │       ├── daily_report.html
│       │       └── alert_notification.html
│       ├── Dockerfile
│       ├── requirements.txt
│       └── tests/
│           ├── test_email_client.py
│           └── test_routes.py
│
├── shared/                              # Shared utilities
│   ├── __init__.py
│   ├── models.py                        # Common data models
│   ├── service_client.py                # Base service client
│   ├── auth.py                          # Authentication utilities
│   ├── logging_config.py                # Shared logging setup
│   ├── health_check.py                  # Health check utilities
│   └── exceptions.py                    # Custom exceptions
│
├── config/                              # Configuration files
│   ├── development.toml                 # Dev environment config
│   ├── production.toml                  # Production config
│   ├── docker.toml                      # Docker environment config
│   └── services.toml                    # Service registry
│
├── scripts/                             # Deployment and utility scripts
│   ├── deploy.sh                        # Deployment script
│   ├── health_check.py                  # Multi-service health check
│   ├── setup_dev.py                     # Development environment setup
│   ├── migrate_legacy.py                # Migration from monolith
│   └── generate_service_docs.py         # API documentation generator
│
├── data/                                # Data storage (development)
│   ├── raw/                             # Raw CSV files
│   ├── processed/                       # Processed data
│   ├── reports/                         # Generated reports
│   └── archive/                         # Archived files
│
├── docs/                                # Documentation
│   ├── api/                             # API documentation
│   │   ├── outlook-relay.md
│   │   ├── db-service.md
│   │   ├── scheduler.md
│   │   ├── report-generator.md
│   │   └── email-service.md
│   ├── deployment/
│   │   ├── docker.md
│   │   ├── production.md
│   │   └── windows-service.md
│   ├── architecture.md
│   └── migration-guide.md
│
├── tests/                               # Integration tests
│   ├── integration/
│   │   ├── test_full_pipeline.py
│   │   ├── test_service_communication.py
│   │   └── test_error_scenarios.py
│   ├── performance/
│   │   ├── test_load.py
│   │   └── test_concurrent_jobs.py
│   └── fixtures/
│       ├── sample_emails.json
│       ├── test_data.csv
│       └── mock_responses.json
│
├── monitoring/                          # Monitoring and observability
│   ├── prometheus/
│   │   └── prometheus.yml
│   ├── grafana/
│   │   ├── dashboards/
│   │   └── datasources/
│   └── logging/
│       └── logstash.conf
│
└── deployment/                          # Deployment configurations
    ├── kubernetes/
    │   ├── namespace.yaml
    │   ├── services/
    │   └── ingress.yaml
    ├── docker-swarm/
    │   └── stack.yml
    └── ansible/
        ├── playbook.yml
        └── roles/
```

## File Templates

### Service Main File Template
```python
# services/{service-name}/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from typing import Dict, Any

from .config import settings
from .routes import health, {service_routes}
from shared.logging_config import setup_logging

# Setup logging
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="{Service Name} API",
    description="{Service description}",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router({service_routes}.router, prefix="/api", tags=["{service}"])

@app.on_event("startup")
async def startup_event():
    logger.info("{Service Name} starting up...")
    # Initialize service-specific resources

@app.on_event("shutdown") 
async def shutdown_event():
    logger.info("{Service Name} shutting down...")
    # Clean up resources

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
```

### Docker Compose Template
```yaml
# docker-compose.yml
version: '3.8'

services:
  outlook-relay:
    build: ./services/outlook-relay
    ports:
      - "8080:8080"
    environment:
      - API_KEY=${API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./config:/app/config:ro
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db-service:
    build: ./services/db-service
    ports:
      - "8081:8081"
    environment:
      - DATABASE_URL=sqlite:///app/data/charlie.db
      - API_KEY=${API_KEY}
    volumes:
      - ./data:/app/data
      - ./config:/app/config:ro
    depends_on:
      - postgres
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8081/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  scheduler:
    build: ./services/scheduler
    ports:
      - "8082:8082"
    environment:
      - API_KEY=${API_KEY}
      - OUTLOOK_RELAY_URL=http://outlook-relay:8080
      - DB_SERVICE_URL=http://db-service:8081
      - REPORT_GENERATOR_URL=http://report-generator:8083
      - EMAIL_SERVICE_URL=http://email-service:8084
    volumes:
      - ./config:/app/config:ro
    depends_on:
      - outlook-relay
      - db-service
      - report-generator
      - email-service
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8082/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  report-generator:
    build: ./services/report-generator
    ports:
      - "8083:8083"
    environment:
      - API_KEY=${API_KEY}
      - DB_SERVICE_URL=http://db-service:8081
    volumes:
      - ./data/reports:/app/reports
      - ./config:/app/config:ro
    depends_on:
      - db-service
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8083/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  email-service:
    build: ./services/email-service
    ports:
      - "8084:8084"
    environment:
      - API_KEY=${API_KEY}
      - OUTLOOK_RELAY_URL=http://outlook-relay:8080
    volumes:
      - ./config:/app/config:ro
    depends_on:
      - outlook-relay
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8084/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=charlie_reporting
      - POSTGRES_USER=charlie
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

## Implementation Priority

### Phase 1: Core Services (Weeks 1-4)
1. **Outlook Relay Service** - Extract email functionality
2. **DB Service** - Centralize data operations  
3. **Basic Scheduler** - Simple job orchestration

### Phase 2: Reporting (Weeks 5-6)
4. **Report Generator Service** - Excel generation
5. **Email Service** - Outbound email delivery

### Phase 3: Polish (Weeks 7-8) 
6. **Web Dashboard** - User interface for Scheduler
7. **Monitoring & Logging** - Production observability
8. **Documentation & Testing** - Complete API docs and integration tests

This structure gives you a clean separation of concerns, clear APIs between services, and a path to scale each component independently. Each service can be developed, tested, and deployed separately while maintaining the overall system functionality.
