# Charlie Reporting - Common Service Architecture

## Standardized Service Structure

Every service follows this exact structure for consistency, maintainability, and developer experience:

```
service-name/
├── config/                           # Configuration Management
│   ├── __init__.py
│   ├── settings.py                   # Pydantic settings model
│   ├── local.toml                    # Local development config
│   ├── production.toml               # Production config
│   └── service.toml                  # Service-specific config
│
├── run/                              # Entry Points & Runners
│   ├── __init__.py
│   ├── service.py                    # Main service runner
│   ├── cli.py                        # CLI commands
│   ├── windows_service.py            # Windows service wrapper
│   └── health_check.py               # Standalone health checker
│
├── src/                              # Source Code
│   ├── __init__.py
│   │
│   ├── business/                     # Business Logic Layer (Pure Domain Logic)
│   │   ├── __init__.py
│   │   ├── models/                   # Domain models
│   │   │   ├── __init__.py
│   │   │   ├── entities.py           # Core business entities
│   │   │   ├── value_objects.py      # Value objects
│   │   │   └── aggregates.py         # Domain aggregates
│   │   ├── services/                 # Business services
│   │   │   ├── __init__.py
│   │   │   ├── processors.py         # Core business logic processors
│   │   │   ├── validators.py         # Business rule validators
│   │   │   └── transformers.py       # Data transformers
│   │   └── exceptions.py             # Business exceptions
│   │
│   ├── interfaces/                   # Interface Layer (External Communication)
│   │   ├── __init__.py
│   │   ├── rest/                     # REST API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── routes.py             # FastAPI routes
│   │   │   ├── schemas.py            # Pydantic request/response models
│   │   │   ├── middleware.py         # Custom middleware
│   │   │   └── dependencies.py       # FastAPI dependencies
│   │   ├── events/                   # Event handling (future Kafka)
│   │   │   ├── __init__.py
│   │   │   ├── publishers.py         # Event publishers
│   │   │   ├── consumers.py          # Event consumers
│   │   │   └── schemas.py            # Event schemas
│   │   └── clients/                  # External service clients
│   │       ├── __init__.py
│   │       ├── http_client.py        # HTTP service client
│   │       └── service_registry.py   # Service discovery
│   │
│   ├── infrastructure/               # Infrastructure Layer (Technical Concerns)
│   │   ├── __init__.py
│   │   ├── persistence/              # Data persistence
│   │   │   ├── __init__.py
│   │   │   ├── database.py           # Database connections
│   │   │   ├── repositories.py       # Data repositories
│   │   │   └── migrations/           # Database migrations
│   │   ├── monitoring/               # Observability
│   │   │   ├── __init__.py
│   │   │   ├── metrics.py            # Prometheus metrics
│   │   │   ├── tracing.py            # Distributed tracing
│   │   │   └── health.py             # Health checks
│   │   ├── messaging/                # Message handling
│   │   │   ├── __init__.py
│   │   │   ├── kafka_client.py       # Kafka client (future)
│   │   │   ├── http_messaging.py     # HTTP-based messaging
│   │   │   └── message_router.py     # Message routing
│   │   └── security/                 # Security concerns
│   │       ├── __init__.py
│   │       ├── auth.py               # Authentication
│   │       ├── authorization.py      # Authorization
│   │       └── encryption.py         # Encryption utilities
│   │
│   ├── utils/                        # Shared Utilities
│   │   ├── __init__.py
│   │   ├── common.py                 # Common utilities
│   │   ├── datetime_helpers.py       # Date/time utilities
│   │   ├── file_helpers.py           # File operations
│   │   └── validation.py             # Common validators
│   │
│   └── logging/                      # Logging Configuration
│       ├── __init__.py
│       ├── setup.py                  # Logging setup
│       ├── formatters.py             # Custom formatters
│       └── handlers.py               # Custom handlers
│
├── tests/                            # Test Suite
│   ├── __init__.py
│   ├── unit/                         # Unit tests
│   │   ├── business/                 # Business logic tests
│   │   ├── interfaces/               # Interface tests
│   │   └── infrastructure/           # Infrastructure tests
│   ├── integration/                  # Integration tests
│   │   ├── test_api.py               # API integration tests
│   │   ├── test_database.py          # Database integration tests
│   │   └── test_messaging.py         # Messaging integration tests
│   ├── e2e/                          # End-to-end tests
│   │   └── test_workflows.py         # Full workflow tests
│   ├── fixtures/                     # Test data and fixtures
│   │   ├── data/                     # Test data files
│   │   └── mocks.py                  # Mock objects
│   └── conftest.py                   # Pytest configuration
│
├── docs/                             # Service Documentation
│   ├── api.md                        # API documentation
│   ├── deployment.md                 # Deployment guide
│   ├── configuration.md              # Configuration guide
│   └── troubleshooting.md            # Troubleshooting guide
│
├── scripts/                          # Utility Scripts
│   ├── setup.py                      # Environment setup
│   ├── migrate.py                    # Database migrations
│   ├── seed_data.py                  # Test data seeding
│   └── windows_install.bat           # Windows installation
│
├── requirements/                     # Dependencies
│   ├── base.txt                      # Base requirements
│   ├── development.txt               # Development requirements
│   ├── production.txt                # Production requirements
│   └── windows.txt                   # Windows-specific requirements
│
├── Dockerfile                        # Container definition
├── docker-compose.yml                # Local development compose
├── .dockerignore                     # Docker ignore file
├── .gitignore                        # Git ignore file
├── Makefile                          # Common tasks
├── README.md                         # Service documentation
└── pyproject.toml                    # Python project configuration
```

## Layer Responsibilities

### 1. Business Layer (Pure Domain Logic)
- **No external dependencies** - Can be tested in isolation
- **Domain models** - Core business entities and rules
- **Business services** - Pure business logic operations
- **Domain events** - Business events that trigger workflows

### 2. Interface Layer (External Communication)
- **REST APIs** - HTTP endpoints for external communication
- **Event handlers** - Kafka consumers/producers (future)
- **Service clients** - Communication with other services
- **Protocol translation** - Convert between external and internal formats

### 3. Infrastructure Layer (Technical Concerns)
- **Persistence** - Database operations and repositories
- **Monitoring** - Metrics, health checks, tracing
- **Messaging** - Message queue operations
- **Security** - Authentication, authorization, encryption

### 4. Configuration Layer
- **Environment-specific settings** - Dev, staging, production
- **Service discovery** - Other service locations
- **Feature flags** - Enable/disable functionality
- **Secret management** - API keys, database credentials

## Common Base Classes

### Base Service Class
```python
# shared/base_service.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio
import signal
import structlog

class BaseService(ABC):
    """Base class for all microservices"""
    
    def __init__(self, name: str, config: Any):
        self.name = name
        self.config = config
        self.logger = structlog.get_logger(service=name)
        self.running = False
        self.health_status = "starting"
        
        # Infrastructure components
        self.metrics = None
        self.database = None
        self.message_client = None
        
    async def start(self):
        """Start the service"""
        self.logger.info("Starting service", service=self.name)
        
        # Initialize infrastructure
        await self._initialize_infrastructure()
        
        # Start business logic
        await self._start_business_logic()
        
        # Setup signal handlers
        self._setup_signal_handlers()
        
        self.running = True
        self.health_status = "healthy"
        self.logger.info("Service started successfully", service=self.name)
    
    async def stop(self):
        """Stop the service gracefully"""
        self.logger.info("Stopping service", service=self.name)
        self.running = False
        self.health_status = "stopping"
        
        # Stop business logic
        await self._stop_business_logic()
        
        # Cleanup infrastructure
        await self._cleanup_infrastructure()
        
        self.health_status = "stopped"
        self.logger.info("Service stopped", service=self.name)
    
    @abstractmethod
    async def _initialize_infrastructure(self):
        """Initialize infrastructure components (DB, messaging, etc.)"""
        pass
    
    @abstractmethod
    async def _start_business_logic(self):
        """Start business logic components"""
        pass
    
    @abstractmethod
    async def _stop_business_logic(self):
        """Stop business logic components"""
        pass
    
    @abstractmethod
    async def _cleanup_infrastructure(self):
        """Cleanup infrastructure components"""
        pass
    
    def _setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers"""
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info("Received shutdown signal", signal=signum)
        asyncio.create_task(self.stop())
```

### Standard Configuration
```python
# shared/config/base_config.py
from pydantic import BaseSettings, Field
from typing import Dict, List, Optional
import os

class BaseServiceConfig(BaseSettings):
    """Base configuration for all services"""
    
    # Service identity
    service_name: str
    service_version: str = "1.0.0"
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Network configuration
    host: str = "0.0.0.0"
    port: int
    
    # Security
    api_key: str = Field(..., env="API_KEY")
    allowed_origins: List[str] = ["*"]
    
    # Service registry
    service_registry: Dict[str, str] = {}
    
    # Infrastructure
    log_level: str = "INFO"
    metrics_enabled: bool = True
    health_check_interval: int = 30
    
    # Database (if needed)
    database_url: Optional[str] = None
    
    # Messaging (future Kafka)
    messaging_enabled: bool = False
    kafka_bootstrap_servers: Optional[List[str]] = None
    
    # File storage
    storage_path: str = "./data"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
    @classmethod
    def load_config(cls, config_file: Optional[str] = None):
        """Load configuration from file and environment"""
        if config_file and os.path.exists(config_file):
            import toml
            config_data = toml.load(config_file)
            return cls(**config_data)
        return cls()
```

### Standard Metrics
```python
# shared/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
from typing import Dict, Any

class ServiceMetrics:
    """Standard metrics for all services"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.registry = CollectorRegistry()
        
        # Request metrics
        self.requests_total = Counter(
            'requests_total',
            'Total number of requests',
            ['service', 'endpoint', 'method', 'status'],
            registry=self.registry
        )
        
        self.request_duration = Histogram(
            'request_duration_seconds',
            'Request duration in seconds',
            ['service', 'endpoint'],
            registry=self.registry
        )
        
        # Health metrics
        self.service_health = Gauge(
            'service_health',
            'Service health status (1=healthy, 0=unhealthy)',
            ['service'],
            registry=self.registry
        )
        
        # Business metrics (to be extended by each service)
        self.business_operations_total = Counter(
            'business_operations_total',
            'Total business operations',
            ['service', 'operation', 'status'],
            registry=self.registry
        )
        
        self.business_operation_duration = Histogram(
            'business_operation_duration_seconds',
            'Business operation duration',
            ['service', 'operation'],
            registry=self.registry
        )
    
    def record_request(self, endpoint: str, method: str, status: str, duration: float):
        """Record HTTP request metrics"""
        self.requests_total.labels(
            service=self.service_name,
            endpoint=endpoint,
            method=method,
            status=status
        ).inc()
        
        self.request_duration.labels(
            service=self.service_name,
            endpoint=endpoint
        ).observe(duration)
    
    def record_business_operation(self, operation: str, status: str, duration: float):
        """Record business operation metrics"""
        self.business_operations_total.labels(
            service=self.service_name,
            operation=operation,
            status=status
        ).inc()
        
        self.business_operation_duration.labels(
            service=self.service_name,
            operation=operation
        ).observe(duration)
    
    def set_health_status(self, healthy: bool):
        """Set service health status"""
        self.service_health.labels(service=self.service_name).set(1 if healthy else 0)
```

### Standard REST Interface
```python
# shared/interfaces/rest/base_api.py
from fastapi import FastAPI, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
import structlog
from typing import Any

class BaseAPI:
    """Base REST API for all services"""
    
    def __init__(self, service_name: str, config: Any, metrics: Any):
        self.service_name = service_name
        self.config = config
        self.metrics = metrics
        self.logger = structlog.get_logger(service=service_name)
        
        self.app = FastAPI(
            title=f"{service_name} API",
            description=f"REST API for {service_name} service",
            version=config.service_version
        )
        
        self._setup_middleware()
        self._setup_routes()
    
    def _setup_middleware(self):
        """Setup common middleware"""
        
        # CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Request logging and metrics
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            start_time = time.time()
            
            # Log request
            self.logger.info(
                "Request started",
                method=request.method,
                url=str(request.url),
                client_ip=request.client.host
            )
            
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            self.logger.info(
                "Request completed",
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                duration=duration
            )
            
            # Record metrics
            self.metrics.record_request(
                endpoint=request.url.path,
                method=request.method,
                status=str(response.status_code),
                duration=duration
            )
            
            return response
    
    def _setup_routes(self):
        """Setup common routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "service": self.service_name,
                "status": "healthy",
                "version": self.config.service_version
            }
        
        @self.app.get("/metrics")
        async def metrics():
            """Prometheus metrics endpoint"""
            from prometheus_client import generate_latest
            return Response(
                generate_latest(self.metrics.registry),
                media_type="text/plain"
            )
        
        @self.app.get("/")
        async def root():
            """Root endpoint"""
            return {
                "service": self.service_name,
                "version": self.config.service_version,
                "status": "running"
            }
```

## Service-Specific Examples

### Outlook Relay Service Structure
```python
# services/outlook-relay/src/business/models/entities.py
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Email:
    id: str
    subject: str
    sender: str
    received_time: datetime
    attachments: List['Attachment']

@dataclass  
class Attachment:
    filename: str
    size: int
    content_type: str
    data: bytes

# services/outlook-relay/src/business/services/processors.py
class EmailProcessor:
    def process_emails(self, emails: List[Email]) -> ProcessingResult:
        """Pure business logic for email processing"""
        pass
    
    def extract_csv_attachments(self, email: Email) -> List[Attachment]:
        """Extract CSV attachments from email"""
        pass

# services/outlook-relay/src/interfaces/rest/routes.py
from fastapi import APIRouter, Depends
from ...business.services.processors import EmailProcessor

router = APIRouter()

@router.post("/emails/fetch")
async def fetch_emails(request: FetchEmailsRequest, processor: EmailProcessor = Depends()):
    """Fetch emails endpoint"""
    pass
```

This structure ensures:
1. **Consistency** across all services
2. **Clear separation** of concerns
3. **Testability** at each layer  
4. **Scalability** for future requirements
5. **Portfolio demonstration** of enterprise architecture skills

Would you like me to start implementing this structure with your existing codebase, beginning with a specific service?
