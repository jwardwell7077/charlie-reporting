# Outlook-Relay Service

## Overview
Email proxy for Outlook/Exchange operations

## Current Code Migration
**Source Files**:
- src/email_fetcher.py
- src/utils.py (email parts)

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
- **Models**: email.py, outlook.py, attachment.py
- **Services**: email_fetcher.py, attachment_processor.py, outlook_connector.py

### Infrastructure Layer
- **Components**: outlook/com_client.py, outlook/graph_client.py

## Configuration
- `config/local.toml` - Development settings
- `config/settings.py` - Pydantic configuration model

## Development
```bash
cd services/outlook-relay/
python scripts/run-dev.py
```

Service will be available at: http://localhost:8080

## Testing
```bash
pytest tests/
```

## Monitoring
- Health: http://localhost:8080/health
- Metrics: http://localhost:9090/metrics
