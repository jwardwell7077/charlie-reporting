# Charlie Reporting - Enterprise Microservices Architecture
## Portfolio Project: From Windows Desktop to Kubernetes

### Project Vision
A production-ready microservices platform demonstrating enterprise patterns:
- **Phase 1**: Windows desktop automation (current friend's use case)
- **Phase 2**: Containerized services with Docker Compose
- **Phase 3**: Kubernetes deployment with GitOps and observability

## Core Architecture Principles

### 1. Separation of Concerns (SoC)
```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Business      │    │   Interface     │    │   Infrastructure│
│   Logic Layer   │    │   Layer         │    │   Layer         │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Data Models   │    │ • REST APIs     │    │ • Metrics       │
│ • Transformers  │    │ • Event Schemas │    │ • Logging       │
│ • Validators    │    │ • CLI Commands  │    │ • Health Checks │
│ • Rules Engine  │    │ • Web Dashboard │    │ • Config Mgmt   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```text

### 2. Service Architecture Pattern
Each service follows the same structure for consistency and maintainability:

```text
service-name/
├── app/
│   ├── business/          # Business Logic Layer
│   │   ├── models/        # Domain models
│   │   ├── services/      # Business services
│   │   └── handlers/      # Business logic handlers
│   ├── interfaces/        # Interface Layer
│   │   ├── rest/          # REST API endpoints
│   │   ├── events/        # Event handlers (future Kafka)
│   │   └── cli/           # CLI commands
│   ├── infrastructure/    # Infrastructure Layer
│   │   ├── config/        # Configuration management
│   │   ├── metrics/       # Prometheus metrics
│   │   ├── logging/       # Structured logging
│   │   └── health/        # Health checks
│   └── main.py           # Service entry point
├── tests/
├── Dockerfile
├── requirements.txt
└── service.bat           # Windows service runner
```text

## Service Definitions with Enterprise Patterns

### 1. Outlook Relay Service
**Business Logic**: Email fetching, attachment processing, COM interface management
**Interface**: REST API, Windows service interface
**Infrastructure**: Metrics on email processing, health checks for Outlook connectivity

```python
# Business Layer
class EmailProcessor:
    def process_emails(self, filters: EmailFilters) -> ProcessingResult
    def extract_attachments(self, email: Email) -> List[Attachment]
    def validate_email_data(self, email: Email) -> ValidationResult

# Interface Layer  
class EmailAPI:
    POST /api/v1/emails/fetch
    GET /api/v1/emails/status
    GET /api/v1/health

# Infrastructure Layer
class EmailMetrics:
    emails_processed_total = Counter()
    email_processing_duration = Histogram()
    outlook_connection_status = Gauge()
```text

### 2. Data Service
**Business Logic**: Data ingestion, deduplication, transformation, storage
**Interface**: REST API, future Kafka consumer
**Infrastructure**: Database metrics, data quality metrics

```python
# Business Layer
class DataProcessor:
    def ingest_csv_data(self, data: CSVData) -> IngestionResult
    def deduplicate_records(self, records: List[Record]) -> List[Record]
    def transform_data(self, data: RawData) -> ProcessedData

# Interface Layer
class DataAPI:
    POST /api/v1/data/ingest
    GET /api/v1/data/query
    GET /api/v1/data/schemas

# Infrastructure Layer
class DataMetrics:
    records_ingested_total = Counter()
    duplicate_records_found = Counter()
    data_processing_duration = Histogram()
```text

### 3. Scheduler Service (Orchestrator)
**Business Logic**: Job scheduling, workflow orchestration, dependency management
**Interface**: REST API, Web dashboard, CLI
**Infrastructure**: Job execution metrics, system health monitoring

```python
# Business Layer
class JobOrchestrator:
    def schedule_job(self, job_spec: JobSpec) -> JobId
    def execute_workflow(self, workflow: Workflow) -> WorkflowResult
    def handle_job_failure(self, job_id: JobId, error: Error) -> RecoveryAction

# Interface Layer
class SchedulerAPI:
    POST /api/v1/jobs/schedule
    GET /api/v1/jobs/{job_id}/status
    GET /api/v1/workflows

# Infrastructure Layer
class SchedulerMetrics:
    jobs_scheduled_total = Counter()
    job_execution_duration = Histogram()
    workflow_success_rate = Gauge()
```text

### 4. Report Generator Service
**Business Logic**: Excel generation, template management, data aggregation
**Interface**: REST API, file serving
**Infrastructure**: Report generation metrics, file storage metrics

```python
# Business Layer
class ReportGenerator:
    def generate_report(self, spec: ReportSpec) -> ReportResult
    def apply_template(self, data: Data, template: Template) -> FormattedReport
    def aggregate_data(self, data: List[Data]) -> AggregatedData

# Interface Layer
class ReportAPI:
    POST /api/v1/reports/generate
    GET /api/v1/reports/{report_id}/download
    GET /api/v1/templates

# Infrastructure Layer
class ReportMetrics:
    reports_generated_total = Counter()
    report_generation_duration = Histogram()
    template_usage_count = Counter()
```text

### 5. Email Delivery Service
**Business Logic**: Email templating, delivery management, recipient handling
**Interface**: REST API, delivery status webhooks
**Infrastructure**: Delivery metrics, template metrics

```python
# Business Layer
class EmailDeliveryService:
    def compose_email(self, template: Template, data: Dict) -> ComposedEmail
    def send_email(self, email: ComposedEmail) -> DeliveryResult
    def track_delivery(self, email_id: EmailId) -> DeliveryStatus

# Interface Layer
class EmailDeliveryAPI:
    POST /api/v1/emails/send
    GET /api/v1/emails/{email_id}/status
    GET /api/v1/delivery/stats

# Infrastructure Layer
class EmailDeliveryMetrics:
    emails_sent_total = Counter()
    email_delivery_duration = Histogram()
    delivery_success_rate = Gauge()
```text

## Common Service Infrastructure

### 1. Base Service Class
```python
# shared/base_service.py
from abc import ABC, abstractmethod
from prometheus_client import CollectorRegistry, Counter, Histogram, Gauge
import structlog

class BaseService(ABC):
    def __init__(self, name: str, config: Config):
        self.name = name
        self.config = config
        self.logger = structlog.get_logger(service=name)
        self.metrics = self._setup_metrics()
        self.health_status = "starting"
    
    def _setup_metrics(self):
        registry = CollectorRegistry()
        return {
            'requests_total': Counter('requests_total', 'Total requests', ['service', 'endpoint'], registry=registry),
            'request_duration': Histogram('request_duration_seconds', 'Request duration', ['service'], registry=registry),
            'health_status': Gauge('service_health', 'Service health status', ['service'], registry=registry)
        }
    
    @abstractmethod
    async def start(self):
        """Start the service"""
        pass
    
    @abstractmethod
    async def stop(self):
        """Stop the service"""
        pass
    
    async def health_check(self) -> HealthStatus:
        """Common health check implementation"""
        return HealthStatus(
            service=self.name,
            status=self.health_status,
            timestamp=datetime.utcnow(),
            dependencies=await self._check_dependencies()
        )
```text

### 2. Service Communication Layer
```python
# shared/service_client.py
import httpx
import asyncio
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

class ServiceClient:
    def __init__(self, service_name: str, base_url: str, api_key: str):
        self.service_name = service_name
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0
        )
        self.circuit_breaker = CircuitBreaker(service_name)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if self.circuit_breaker.is_open():
            raise ServiceUnavailableError(f"{self.service_name} circuit breaker is open")
        
        try:
            response = await self.client.post(f"{self.base_url}{endpoint}", json=data)
            response.raise_for_status()
            self.circuit_breaker.record_success()
            return response.json()
        except Exception as e:
            self.circuit_breaker.record_failure()
            raise ServiceCommunicationError(f"Failed to call {self.service_name}: {e}")

# Future Kafka Integration
class EventPublisher:
    def __init__(self, kafka_config: KafkaConfig):
        self.producer = None  # Will be KafkaProducer
    
    async def publish_event(self, topic: str, event: Event):
        # For now, HTTP callback
        # Later: await self.producer.send(topic, event.dict())
        pass
```text

### 3. Configuration Management
```python
# shared/config.py
from pydantic import BaseSettings, Field
from typing import Dict, List, Optional

class ServiceConfig(BaseSettings):
    name: str
    port: int
    host: str = "0.0.0.0"
    log_level: str = "INFO"
    api_key: str = Field(..., env="API_KEY")
    
    # Service registry
    services: Dict[str, str] = {}
    
    # Infrastructure
    metrics_enabled: bool = True
    health_check_interval: int = 30
    
    # Future Kafka config
    kafka_bootstrap_servers: Optional[List[str]] = None
    kafka_enabled: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Service-specific configs inherit from base
class OutlookRelayConfig(ServiceConfig):
    outlook_profile: str = "EmailService"
    outlook_timeout: int = 30
    max_attachment_size_mb: int = 100

class DataServiceConfig(ServiceConfig):
    database_url: str = Field(..., env="DATABASE_URL")
    max_batch_size: int = 1000
    dedup_strategy: str = "strict"
```text

### 4. Observability Stack
```python
# shared/observability.py
import structlog
from prometheus_client import CollectorRegistry, generate_latest
import time
from functools import wraps

# Structured Logging
def setup_logging(service_name: str, level: str = "INFO"):
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

# Metrics Decorator
def track_metrics(service_name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                METRICS['requests_total'].labels(service=service_name, status='success').inc()
                return result
            except Exception as e:
                METRICS['requests_total'].labels(service=service_name, status='error').inc()
                raise
            finally:
                duration = time.time() - start_time
                METRICS['request_duration'].labels(service=service_name).observe(duration)
        return wrapper
    return decorator

# Health Check Framework
class HealthChecker:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.dependencies = []
    
    def add_dependency(self, name: str, check_func):
        self.dependencies.append((name, check_func))
    
    async def check_health(self) -> Dict[str, Any]:
        health_status = {
            "service": self.service_name,
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "dependencies": {}
        }
        
        for dep_name, check_func in self.dependencies:
            try:
                dep_status = await check_func()
                health_status["dependencies"][dep_name] = dep_status
            except Exception as e:
                health_status["dependencies"][dep_name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health_status["status"] = "degraded"
        
        return health_status
```text

## Windows Desktop Deployment (Phase 1)

### Service Runner Script
```python
# scripts/run_services.py
"""
Windows Desktop Service Runner
Starts all services as separate Python processes with monitoring
"""
import subprocess
import time
import threading
import signal
import sys
from pathlib import Path

class ServiceManager:
    def __init__(self):
        self.services = {
            'outlook-relay': {'port': 8080, 'process': None},
            'data-service': {'port': 8081, 'process': None},
            'scheduler': {'port': 8082, 'process': None},
            'report-generator': {'port': 8083, 'process': None},
            'email-service': {'port': 8084, 'process': None}
        }
        self.running = True
    
    def start_service(self, name: str, config: dict):
        cmd = [
            sys.executable, 
            f"services/{name}/app/main.py",
            "--port", str(config['port'])
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        config['process'] = process
        print(f"Started {name} on port {config['port']} (PID: {process.pid})")
    
    def monitor_services(self):
        while self.running:
            for name, config in self.services.items():
                if config['process'] and config['process'].poll() is not None:
                    print(f"Service {name} crashed, restarting...")
                    self.start_service(name, config)
            time.sleep(10)
    
    def start_all(self):
        for name, config in self.services.items():
            self.start_service(name, config)
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_services)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Wait for interrupt
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_all()
    
    def stop_all(self):
        self.running = False
        for name, config in self.services.items():
            if config['process']:
                config['process'].terminate()
                print(f"Stopped {name}")

if __name__ == "__main__":
    manager = ServiceManager()
    manager.start_all()
```text

### Windows Batch File
```batch
@echo off
REM services/start_charlie_reporting.bat
echo Starting Charlie Reporting Services...

REM Set environment variables
set API_KEY=your-api-key-here
set DATABASE_URL=sqlite:///data/charlie.db
set LOG_LEVEL=INFO

REM Create data directories
if not exist "data" mkdir data
if not exist "data\raw" mkdir data\raw
if not exist "data\reports" mkdir data\reports
if not exist "logs" mkdir logs

REM Start service manager
python scripts/run_services.py

pause
```text

## Portfolio Demonstration Value

### 1. Enterprise Architecture Patterns
- **Microservices**: Proper service decomposition
- **Domain-Driven Design**: Clear business boundaries
- **Event-Driven Architecture**: Prepared for async messaging
- **Observability**: Metrics, logging, health checks

### 2. Technology Stack Breadth
- **Backend**: Python, FastAPI, SQLAlchemy
- **Databases**: SQLite → PostgreSQL migration path
- **Messaging**: HTTP → Kafka migration path
- **Containerization**: Docker, Docker Compose
- **Orchestration**: Kubernetes, Helm
- **Monitoring**: Prometheus, Grafana
- **CI/CD**: GitOps pipeline ready

### 3. Real-World Problem Solving
- **Legacy system modernization**
- **Cross-platform compatibility**
- **Gradual migration strategy**
- **Enterprise constraints handling**

### 4. DevOps & Operations
- **Infrastructure as Code**
- **Service mesh ready**
- **Monitoring and alerting**
- **Disaster recovery planning**

## Next Steps

1. **Refactor Existing Code** - Split monolith into service modules
2. **Implement Base Infrastructure** - Shared components and patterns
3. **Create Service Templates** - Standardized service structure
4. **Build Windows Deployment** - Desktop automation for friend
5. **Containerize Services** - Docker preparation
6. **Add Observability** - Metrics and monitoring
7. **Kubernetes Deployment** - Cloud-native transformation

This architecture demonstrates enterprise-level thinking while solving real business problems. It shows your ability to design systems that scale from desktop automation to cloud-native deployments.

Would you like to start by refactoring your existing codebase into this service structure?
