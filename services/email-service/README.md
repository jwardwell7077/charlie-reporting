# Email-Service Service

## Overview
Outbound email delivery and templates

## Current Code Migration
**Source Files**:
- src/utils.py (email sending)
- new outbound logic

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
- **Models**: email_template.py, recipient.py, delivery.py
- **Services**: email_sender.py, template_processor.py, delivery_tracker.py

### Infrastructure Layer
- **Components**: smtp/client.py, graph/email_client.py, templates/engine.py

## Configuration
- `config/local.toml` - Development settings
- `config/settings.py` - Pydantic configuration model

## Development
```bash
cd services/email-service/
python scripts/run-dev.py
```

Service will be available at: http://localhost:8084

## Testing
```bash
pytest tests/
```

## Monitoring
- Health: http://localhost:8084/health
- Metrics: http://localhost:9094/metrics
