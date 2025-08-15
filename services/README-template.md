# Service README Template

> This service follows the [Charlie Reporting Architecture](../.copilot-context.md)

## Quick Start

```bash
# Setup
cd services/{service-name}
python -m pip install -r requirements.txt

# Run service
python run/service.py

# Run tests
pytest tests/ -v
```

## Architecture Compliance

This service implements the standardized SoC pattern:

- **Business Layer**: `src/business/` - Pure domain logic
- **Interface Layer**: `src/interfaces/` - REST APIs and external communication  
- **Infrastructure Layer**: `src/infrastructure/` - Cross-cutting concerns

## Key APIs

Refer to [Microservices Architecture](../docs/architecture/microservices_architecture.md) for:

- Service communication patterns
- Standard endpoint structures
- Health check implementations

## Development

Always reference the [Common Service Architecture](../docs/architecture/common_service_architecture.md) when:

- Adding new endpoints
- Creating business services
- Implementing health checks
- Writing tests

## Links

- [Main Architecture](../.copilot-context.md)
- [Service Patterns](../docs/architecture/common_service_architecture.md)
- [API Standards](../docs/architecture/microservices_architecture.md)
