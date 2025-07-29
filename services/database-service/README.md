# Database-Service Service

## Overview
Centralized data storage and retrieval

## Current Code Migration
**Source Files**:
- New service - data patterns from config

## Quick Start

```bash
# Setup shared components
ln -s ../../shared ./shared

# Install dependencies  
pip install -r requirements.txt

# Run service
python src/main.py

# Or use dev runner
python scripts/run-dev.py
```

## Architecture

### Business Layer
- **Models**: email_record.py, report.py, user.py, attachment.py
- **Services**: data_manager.py, query_service.py, migration_service.py

### Infrastructure Layer
- **Components**: database/connection.py, database/models.py, database/migrations.py

## Configuration
- `config/local.toml` - Development settings
- `config/settings.py` - Pydantic configuration model

## Development
```bash
cd services/database-service/
python scripts/run-dev.py
```

Service will be available at: http://localhost:8081

## Testing
```bash
pytest tests/
```

## Monitoring
- Health: http://localhost:8081/health
- Metrics: http://localhost:9091/metrics
