#!/usr/bin/env python3
"""
Create skeleton structure for all Charlie Reporting services
"""

import os
from pathlib import Path

# Service definitions with their specific structures
SERVICES = {
    "outlook-relay": {
        "description": "Email proxy for Outlook/Exchange operations",
        "current_code": ["src/email_fetcher.py", "src/utils.py (email parts)"],
        "business_models": ["email.py", "outlook.py", "attachment.py"],
        "business_services": ["email_fetcher.py", "attachment_processor.py", "outlook_connector.py"],
        "infrastructure": ["outlook/com_client.py", "outlook/graph_client.py"]
    },
    "database-service": {
        "description": "Centralized data storage and retrieval",
        "current_code": ["New service - data patterns from config"],
        "business_models": ["email_record.py", "report.py", "user.py", "attachment.py"],
        "business_services": ["data_manager.py", "query_service.py", "migration_service.py"],
        "infrastructure": ["database/connection.py", "database/models.py", "database/migrations.py"]
    },
    "scheduler-service": {
        "description": "Automated task scheduling and orchestration",
        "current_code": ["run.py (scheduling logic)", "manual triggers"],
        "business_models": ["job.py", "schedule.py", "execution.py"],
        "business_services": ["scheduler.py", "job_manager.py", "orchestrator.py"],
        "infrastructure": ["scheduler/apscheduler_config.py", "scheduler/job_store.py"]
    },
    "report-generator": {
        "description": "Excel report creation and formatting",
        "current_code": ["src/excel_writer.py", "src/transformer.py"],
        "business_models": ["report_template.py", "data_model.py", "excel_format.py"],
        "business_services": ["report_builder.py", "data_transformer.py", "template_engine.py"],
        "infrastructure": ["excel/writer.py", "excel/formatter.py", "excel/templates.py"]
    },
    "email-service": {
        "description": "Outbound email delivery and templates",
        "current_code": ["src/utils.py (email sending)", "new outbound logic"],
        "business_models": ["email_template.py", "recipient.py", "delivery.py"],
        "business_services": ["email_sender.py", "template_processor.py", "delivery_tracker.py"],
        "infrastructure": ["smtp/client.py", "graph/email_client.py", "templates/engine.py"]
    }
}

def create_service_skeleton(service_name: str, service_config: dict):
    """Create complete directory structure for a service"""
    
    print(f"\n🏗️  Creating {service_name} skeleton...")
    
    base_path = Path(f"services/{service_name}")
    
    # Main directories
    directories = [
        # GitHub workflows
        ".github/workflows",
        
        # Configuration
        "config",
        
        # Source code structure
        "src",
        "src/business",
        "src/business/models", 
        "src/business/services",
        "src/interfaces",
        "src/interfaces/rest",
        "src/interfaces/cli",
        "src/infrastructure",
        
        # Tests
        "tests",
        "tests/unit",
        "tests/unit/business",
        "tests/unit/interfaces", 
        "tests/unit/infrastructure",
        "tests/integration",
        "tests/e2e",
        
        # Scripts
        "scripts",
        
        # Logs (for development)
        "logs"
    ]
    
    # Create service-specific infrastructure directories
    if "infrastructure" in service_config:
        for infra_item in service_config["infrastructure"]:
            if "/" in infra_item:
                infra_dir = f"src/infrastructure/{infra_item.split('/')[0]}"
                directories.append(infra_dir)
    
    # Create all directories
    for directory in directories:
        dir_path = base_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py files
    init_dirs = [
        "src",
        "src/business", 
        "src/business/models",
        "src/business/services",
        "src/interfaces",
        "src/interfaces/rest",
        "src/interfaces/cli", 
        "src/infrastructure",
        "tests",
        "tests/unit",
        "tests/integration",
        "config"
    ]
    
    for init_dir in init_dirs:
        init_file = base_path / init_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text('"""{}"""\n'.format(init_dir.replace("/", ".").replace("src.", "").title()))
    
    return base_path

def create_service_files(service_name: str, service_config: dict, base_path: Path):
    """Create skeleton files for a service"""
    
    # Service-specific requirements.txt
    requirements_content = f"""# {service_name.title()} Service Requirements

# === Shared Components ===
# Install shared requirements: pip install -r ../../shared/requirements.txt

# === Service-Specific Dependencies ===
"""
    
    if service_name == "outlook-relay":
        requirements_content += """
# Outlook integration
pywin32>=306; sys_platform == "win32"
msal>=1.24.0
msgraph-core>=0.2.2

# File processing  
openpyxl>=3.1.0
pandas>=2.1.0
"""
    elif service_name == "database-service":
        requirements_content += """
# Database
sqlalchemy[asyncio]>=2.0.0
asyncpg>=0.29.0
alembic>=1.12.0

# Data processing
pandas>=2.1.0
"""
    elif service_name == "scheduler-service":
        requirements_content += """
# Scheduling
apscheduler>=3.10.0
croniter>=1.4.0

# Background tasks
celery>=5.3.0
redis>=5.0.0
"""
    elif service_name == "report-generator":
        requirements_content += """
# Excel generation
openpyxl>=3.1.0
xlsxwriter>=3.1.0
xlrd>=2.0.0

# Data processing
pandas>=2.1.0
numpy>=1.24.0

# Templating
jinja2>=3.1.0
"""
    elif service_name == "email-service":
        requirements_content += """
# Email
aiosmtplib>=3.0.0
email-validator>=2.1.0

# Templates
jinja2>=3.1.0
premailer>=3.10.0

# Microsoft Graph (alternative)
msal>=1.24.0
msgraph-core>=0.2.2
"""
    
    (base_path / "requirements.txt").write_text(requirements_content)
    
    # Configuration files
    config_content = f"""[service]
name = "{service_name}"
host = "localhost"
port = {8080 + list(SERVICES.keys()).index(service_name)}
debug = true
environment = "local"

[logging]
level = "DEBUG"
file = "logs/{service_name}-local.log"
json_format = true

[metrics]
enabled = true
port = {9090 + list(SERVICES.keys()).index(service_name)}

[health]
check_interval = 30.0
"""
    
    (base_path / "config" / "local.toml").write_text(config_content)
    
    # Service settings.py
    settings_content = f'''"""
{service_name.title()} Service Configuration
"""

from typing import Optional
from pydantic import Field
import sys
import os

# Add shared components to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

try:
    from shared.config import BaseServiceConfig
except ImportError:
    from pydantic_settings import BaseSettings
    class BaseServiceConfig(BaseSettings):
        service_name: str = "{service_name}"
        service_port: int = {8080 + list(SERVICES.keys()).index(service_name)}

class {service_name.replace("-", "").title()}Config(BaseServiceConfig):
    """Configuration for {service_name} service"""
    
    service_name: str = "{service_name}"
    service_port: int = Field(default={8080 + list(SERVICES.keys()).index(service_name)}, description="Service HTTP port")
    service_host: str = Field(default="0.0.0.0", description="Service bind host")
    
    # Add service-specific configuration here
    
    class Config:
        env_file = ".env"
        env_prefix = "{service_name.upper().replace('-', '_')}_"

def load_config() -> {service_name.replace("-", "").title()}Config:
    """Load configuration"""
    try:
        from shared.config import ConfigLoader
        return ConfigLoader.load_config({service_name.replace("-", "").title()}Config, "{service_name}")
    except ImportError:
        return {service_name.replace("-", "").title()}Config()
'''
    
    (base_path / "config" / "settings.py").write_text(settings_content)
    
    # Main service entry point
    main_content = f'''"""
{service_name.title()} Service - Main Entry Point
{service_config["description"]}
"""

import asyncio
import sys
import os
from pathlib import Path

# Add shared components to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from config.settings import load_config

try:
    from shared.base_service import BaseService
    from shared.logging import setup_service_logging
    from shared.metrics import ServiceMetrics
    from shared.health import HealthMonitor
except ImportError:
    # Fallback implementations
    class BaseService:
        def __init__(self, *args, **kwargs): pass
        async def startup(self): pass
        async def shutdown(self): pass
        async def run(self): pass
    
    def setup_service_logging(name, level=None):
        import logging
        return logging.getLogger(name)
    
    class ServiceMetrics:
        def __init__(self, name): pass
    
    class HealthMonitor:
        def __init__(self, name): pass

class {service_name.replace("-", "").title()}Service(BaseService):
    """
    {service_name.title()} Service
    {service_config["description"]}
    """
    
    def __init__(self):
        self.config = load_config()
        
        self.logger = setup_service_logging(
            self.config.service_name,
            self.config.log_level if hasattr(self.config, 'log_level') else 'INFO'
        )
        
        self.metrics = ServiceMetrics(self.config.service_name)
        self.health_monitor = HealthMonitor(self.config.service_name)
        
        super().__init__(self.logger, self.metrics, self.health_monitor)
    
    async def startup(self):
        """Service startup logic"""
        self.logger.info("Starting {service_name.title()} Service", version="1.0.0")
        
        # TODO: Initialize service-specific components
        
        self.logger.info(
            "{service_name.title()} Service started successfully",
            port=self.config.service_port
        )
    
    async def shutdown(self):
        """Service shutdown logic"""
        self.logger.info("Shutting down {service_name.title()} Service")
        
        # TODO: Cleanup service-specific components

async def main():
    """Main entry point"""
    service = {service_name.replace("-", "").title()}Service()
    
    try:
        await service.startup()
        await service.run()
    except KeyboardInterrupt:
        print("\\nReceived interrupt signal")
    except Exception as e:
        print(f"Service error: {{e}}")
    finally:
        await service.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    (base_path / "src" / "main.py").write_text(main_content)
    
    # Create business model files
    for model_file in service_config["business_models"]:
        model_name = model_file.replace(".py", "")
        model_content = f'''"""
{model_name.title()} domain model for {service_name}
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class {model_name.title()}:
    """
    {model_name.title()} domain model
    TODO: Define attributes and methods
    """
    
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # TODO: Add domain-specific attributes
'''
        
        (base_path / "src" / "business" / "models" / model_file).write_text(model_content)
    
    # Create business service files
    for service_file in service_config["business_services"]:
        service_file_name = service_file.replace(".py", "")
        service_content = f'''"""
{service_file_name.title()} business service for {service_name}
"""

from typing import List, Optional
import logging

class {service_file_name.replace("_", "").title()}:
    """
    {service_file_name.title()} business logic
    Pure domain logic with no infrastructure dependencies
    """
    
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
    
    # TODO: Implement business methods
'''
        
        (base_path / "src" / "business" / "services" / service_file).write_text(service_content)
    
    # Create development runner
    dev_runner_content = f'''#!/usr/bin/env python3
"""
Development runner for {service_name.title()} Service
"""

import sys
import os
from pathlib import Path

current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

shared_dir = current_dir / "shared"
if shared_dir.exists():
    sys.path.insert(0, str(shared_dir))

def main():
    """Run the service in development mode"""
    print("🚀 Starting {service_name.title()} Service (Development Mode)")
    print("=" * 50)
    
    if not shared_dir.exists():
        print("⚠️  Shared components not found. Creating symlink...")
        try:
            shared_source = current_dir.parent.parent / "shared"
            if shared_source.exists():
                shared_dir.symlink_to(shared_source)
                print("✅ Created shared components symlink")
            else:
                print("❌ Shared components source not found")
                return 1
        except Exception as e:
            print(f"❌ Failed to create symlink: {{e}}")
            return 1
    
    try:
        from legacy_bridge import main as service_main
        import asyncio
        asyncio.run(service_main())
    except ImportError as e:
        print(f"❌ Import error: {{e}}")
        return 1
    except Exception as e:
        print(f"❌ Service error: {{e}}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''
    
    (base_path / "scripts" / "run-dev.py").write_text(dev_runner_content)
    os.chmod(base_path / "scripts" / "run-dev.py", 0o755)
    
    # Service README
    readme_content = f'''# {service_name.title()} Service

## Overview
{service_config["description"]}

## Current Code Migration
**Source Files**:
{chr(10).join(f"- {code}" for code in service_config["current_code"])}

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
- **Models**: {", ".join(service_config["business_models"])}
- **Services**: {", ".join(service_config["business_services"])}

### Infrastructure Layer
- **Components**: {", ".join(service_config.get("infrastructure", []))}

## Configuration
- `config/local.toml` - Development settings
- `config/settings.py` - Pydantic configuration model

## Development
```bash
cd services/{service_name}/
python scripts/run-dev.py
```

Service will be available at: http://localhost:{8080 + list(SERVICES.keys()).index(service_name)}

## Testing
```bash
pytest tests/
```

## Monitoring
- Health: http://localhost:{8080 + list(SERVICES.keys()).index(service_name)}/health
- Metrics: http://localhost:{9090 + list(SERVICES.keys()).index(service_name)}/metrics
'''
    
    (base_path / "README.md").write_text(readme_content)
    
    print(f"✅ Created {service_name} skeleton structure")

def main():
    """Create all service skeletons"""
    print("🏗️  Creating Charlie Reporting Service Skeletons")
    print("=" * 60)
    
    for service_name, service_config in SERVICES.items():
        base_path = create_service_skeleton(service_name, service_config)
        create_service_files(service_name, service_config, base_path)
    
    print(f"\n🎉 Created {len(SERVICES)} service skeletons!")
    print("\n📋 Next Steps:")
    print("1. Move existing code into appropriate services")
    print("2. Set up shared component symlinks")
    print("3. Implement service-specific business logic")
    print("4. Test individual services")
    
    print(f"\n🚀 Quick test:")
    print("python tools/run-all-services.py")

if __name__ == "__main__":
    main()
