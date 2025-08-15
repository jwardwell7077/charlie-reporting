# Shared Components for Charlie Reporting Microservices

This directory contains shared components used across all microservices in the Charlie Reporting system.

## Components

### Base Service (`base_service.py`)

- **Purpose**: Abstract base class providing standardized service lifecycle management
- **Features**:
  - Async startup/shutdown procedures
  - Signal handling for graceful shutdown
  - Health monitoring integration
  - Service state management
- **Usage**: All microservices inherit from `BaseService`

### Configuration System (`config.py`)

- **Purpose**: Centralized configuration management with environment-specific loading
- **Features**:
  - TOML and environment variable support
  - Service-specific configuration classes
  - Validation with Pydantic
  - Environment isolation (dev/staging/production)
- **Usage**: Each service extends `BaseServiceConfig`

### Metrics Collection (`metrics.py`)

- **Purpose**: Prometheus-compatible metrics collection for all services
- **Features**:
  - HTTP request metrics (count, duration, status)
  - Business operation tracking
  - Health status metrics
  - Resource utilization monitoring
- **Usage**: `ServiceMetrics` class provides standardized metrics collection

### Logging System (`logging.py`)

- **Purpose**: Structured logging with service-aware context
- **Features**:
  - JSON structured logging
  - Request/operation correlation
  - Automatic service context
  - Multiple output handlers (console, file, external)
- **Usage**: `ServiceLogger` with context managers and operation tracking

### Health Monitoring (`health.py`)

- **Purpose**: Comprehensive health checking system for services and dependencies
- **Features**:
  - Component-level health checks
  - Database, HTTP service, memory, disk monitoring
  - Aggregated service health status
  - Continuous monitoring with configurable intervals
- **Usage**: `HealthMonitor` with pluggable health checkers

### Service Discovery (`discovery.py`)

- **Purpose**: Service registry and inter-service communication
- **Features**:
  - Service registration and heartbeat
  - Service discovery for client calls
  - Load balancing and failover
  - In-memory registry (extensible to Consul/etcd)
- **Usage**: `ServiceDiscoveryMixin` for automatic registration

### Utilities (`utils.py`)

- **Purpose**: Common helper functions and utilities
- **Features**:
  - Date/time handling
  - ID generation
  - File operations
  - Validation utilities
  - Retry logic and circuit breakers
- **Usage**: Import specific utility classes as needed

### HTTP Utilities (`http_utils.py`)

- **Purpose**: FastAPI middleware, error handlers, and HTTP utilities
- **Features**:
  - Request logging middleware
  - Security headers
  - Standardized error responses
  - Health/metrics endpoints
  - CORS configuration
- **Usage**: Setup functions for FastAPI applications

## Architecture Patterns

### Separation of Concerns

All shared components follow clear separation of concerns:

- **Infrastructure**: Database connections, external service clients
- **Interface**: HTTP handlers, API models, middleware
- **Business**: Core business logic and operations
- **Utilities**: Cross-cutting concerns (logging, metrics, health)

### Dependency Injection

Components are designed for easy dependency injection:

```python
# Service setup
logger = ServiceLogger("my-service")
metrics = ServiceMetrics("my-service")
health_monitor = HealthMonitor("my-service")

# Integration
class MyService(BaseService):
    def __init__(self):
        super().__init__(logger, metrics, health_monitor)
```

### Configuration Management

Environment-specific configuration with validation:

```python
class MyServiceConfig(BaseServiceConfig):
    database_url: str
    api_timeout: float = 30.0
    max_retries: int = 3

# Load from TOML/env
config = ConfigLoader.load_config(MyServiceConfig, "my-service")
```

### Health Monitoring

Pluggable health check system:

```python
monitor = HealthMonitor("my-service")
monitor.add_checker(DatabaseHealthChecker("main_db", test_connection))
monitor.add_checker(HTTPServiceHealthChecker("auth-service", "http://auth:8080/health"))
await monitor.start_monitoring()
```

## Development Setup

### Dependencies

Install shared component dependencies:

```bash
pip install -r shared/requirements.txt
```

### Import Resolution

The current environment may not have all dependencies installed. The shared components include fallback implementations for missing dependencies to ensure the codebase remains functional during development.

### Testing

Each component includes comprehensive examples and usage patterns in docstrings. Integration tests validate component interactions.

## Production Considerations

### External Dependencies

- **Service Registry**: Replace `InMemoryServiceRegistry` with Consul or etcd
- **Metrics**: Integrate with Prometheus/Grafana stack
- **Logging**: Configure structured log forwarding to ELK stack
- **Health Checks**: Integrate with Kubernetes liveness/readiness probes

### Security

- All HTTP traffic should use TLS in production
- Service-to-service authentication via JWT or mTLS
- Configuration secrets via Kubernetes secrets or external vault

### Observability

- Distributed tracing with OpenTelemetry
- Centralized logging with correlation IDs
- Comprehensive metrics and alerting
- Health check dashboards

## Usage Examples

See individual component files for detailed usage examples and integration patterns. Each component is designed to work independently or as part of the complete microservices architecture.
