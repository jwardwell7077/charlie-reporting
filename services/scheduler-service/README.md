# Scheduler-Service Service

## Overview
Automated task scheduling and orchestration

## Current Code Migration
**Source Files**:
- run.py (scheduling logic)
- manual triggers

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
- **Models**: job.py, schedule.py, execution.py
- **Services**: scheduler.py, job_manager.py, orchestrator.py

### Infrastructure Layer
- **Components**: scheduler/apscheduler_config.py, scheduler/job_store.py

## Configuration
- `config/local.toml` - Development settings
- `config/settings.py` - Pydantic configuration model

## Development
```bash
cd services/scheduler-service/
python scripts/run-dev.py
```

Service will be available at: http://localhost:8082

## Testing
```bash
pytest tests/
```

## Monitoring
- Health: http://localhost:8082/health
- Metrics: http://localhost:9092/metrics
