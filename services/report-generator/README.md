# Report-Generator Service

## Overview
Excel report creation and formatting

## Current Code Migration
**Source Files**:
- src/excel_writer.py
- src/transformer.py

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
- **Models**: report_template.py, data_model.py, excel_format.py
- **Services**: report_builder.py, data_transformer.py, template_engine.py

### Infrastructure Layer
- **Components**: excel/writer.py, excel/formatter.py, excel/templates.py

## Configuration
- `config/local.toml` - Development settings
- `config/settings.py` - Pydantic configuration model

## Development
```bash
cd services/report-generator/
python scripts/run-dev.py
```

Service will be available at: http://localhost:8083

## Testing
```bash
pytest tests/
```

## Monitoring
- Health: http://localhost:8083/health
- Metrics: http://localhost:9093/metrics
