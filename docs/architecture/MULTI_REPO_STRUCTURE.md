# Charlie Reporting - Multi-Repository Service Structure

## Current Challenge
The project currently has all services in a single `src/` directory, but needs to be split into 5 independent services that can each become separate repositories for independent deployment and development.

## Proposed Directory Structure

### Root Repository Structure
```text
charlie-reporting/                    # Main orchestration repository
├── shared/                          # Shared components (Git submodule or package)
├── services/                        # Local service development
│   ├── outlook-relay/
│   ├── database-service/
│   ├── scheduler-service/
│   ├── report-generator/
│   └── email-service/
├── deployment/                      # Multi-service deployment configs
│   ├── docker-compose.yml
│   ├── kubernetes/
│   └── scripts/
├── docs/                           # Overall architecture documentation
└── tools/                          # Development and deployment tools
```text

### Individual Service Structure (Repo-Ready)
Each service follows this structure, making it easy to copy into a new repository:

```text
outlook-relay/                       # Service root (future repo root)
├── .github/                        # GitHub Actions (CI/CD)
│   └── workflows/
│       ├── ci.yml
│       ├── build-docker.yml
│       └── deploy.yml
├── shared/                         # Git submodule or copied shared components
│   ├── base_service.py
│   ├── config.py
│   ├── logging.py
│   ├── metrics.py
│   ├── health.py
│   ├── discovery.py
│   ├── http_utils.py
│   ├── utils.py
│   └── requirements.txt
├── config/                         # Service configuration
│   ├── __init__.py
│   ├── settings.py                 # Pydantic settings model
│   ├── local.toml                  # Development config
│   ├── staging.toml                # Staging environment
│   ├── production.toml             # Production config
│   └── service.toml                # Service-specific defaults
├── src/                           # Service source code
│   ├── __init__.py
│   ├── business/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── email.py           # Email domain models
│   │   │   └── outlook.py         # Outlook-specific models
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── email_fetcher.py   # Core email fetching logic
│   │   │   ├── attachment_processor.py
│   │   │   └── outlook_connector.py
│   │   └── exceptions.py
│   ├── interfaces/               # Interface layer
│   │   ├── __init__.py
│   │   ├── rest/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py         # FastAPI routes
│   │   │   ├── schemas.py        # API models
│   │   │   └── dependencies.py   # FastAPI dependencies
│   │   └── cli/
│   │       ├── __init__.py
│   │       └── commands.py       # CLI commands
│   ├── infrastructure/           # Infrastructure layer
│   │   ├── __init__.py
│   │   ├── outlook/              # Outlook-specific infrastructure
│   │   │   ├── __init__.py
│   │   │   ├── com_client.py     # Windows COM client
│   │   │   └── graph_client.py   # Microsoft Graph client
│   │   ├── config.py             # Service-specific config
│   │   ├── logging.py            # Service-specific logging setup
│   │   ├── metrics.py            # Service-specific metrics
│   │   └── health.py             # Service-specific health checks
│   └── main.py                   # Service entry point
├── tests/                        # Comprehensive test suite
│   ├── __init__.py
│   ├── conftest.py               # Pytest configuration
│   ├── unit/
│   │   ├── test_business/
│   │   ├── test_interfaces/
│   │   └── test_infrastructure/
│   ├── integration/
│   │   ├── test_outlook_integration.py
│   │   └── test_api_endpoints.py
│   └── e2e/
│       └── test_email_fetch_flow.py
├── scripts/                      # Service-specific scripts
│   ├── setup.py                  # Environment setup
│   ├── run-dev.py                # Development runner
│   └── health-check.py           # Standalone health check
├── Dockerfile                    # Container definition
├── .dockerignore
├── requirements.txt              # Service-specific dependencies
├── requirements-dev.txt          # Development dependencies
├── pyproject.toml               # Python project configuration
├── README.md                    # Service-specific documentation
├── CHANGELOG.md                 # Service version history
└── .gitignore                   # Service-specific ignore patterns
```text

## Service-Specific Mapping

### 1. Outlook Relay Service (`outlook-relay/`)
**Current Code**: `src/email_fetcher.py`, `src/utils.py` (email parts)
**New Structure**:
- `src/business/services/email_fetcher.py` - Core email logic from current email_fetcher.py
- `src/business/services/outlook_connector.py` - Outlook COM/Graph integration
- `src/infrastructure/outlook/com_client.py` - Windows COM implementation
- `src/infrastructure/outlook/graph_client.py` - Microsoft Graph implementation

### 2. Database Service (`database-service/`)
**Current Code**: New service, data storage patterns from existing config
**New Structure**:
- `src/business/models/` - Data models (emails, reports, users)
- `src/business/services/data_manager.py` - Core data operations
- `src/infrastructure/database/` - SQLAlchemy setup and migrations

### 3. Scheduler Service (`scheduler-service/`)
**Current Code**: Scheduling logic from `run.py` and manual triggers
**New Structure**:
- `src/business/services/scheduler.py` - Core scheduling logic
- `src/business/models/job.py` - Job definitions and state
- `src/infrastructure/scheduler/` - APScheduler setup

### 4. Report Generator Service (`report-generator/`)
**Current Code**: `src/excel_writer.py`, `src/transformer.py`
**New Structure**:
- `src/business/services/report_builder.py` - Core report logic from excel_writer.py
- `src/business/services/data_transformer.py` - Data transformation from transformer.py
- `src/infrastructure/excel/` - Excel generation libraries

### 5. Email Service (`email-service/`)
**Current Code**: Email sending parts from current utils, new outbound logic
**New Structure**:
- `src/business/services/email_sender.py` - Core email sending logic
- `src/business/models/template.py` - Email templates
- `src/infrastructure/smtp/` - SMTP/Graph email delivery

## Shared Components Strategy

### Option 1: Git Submodules (Recommended for Development)
```bash
# In each service repository
git submodule add https://github.com/yourorg/charlie-shared.git shared
```text

### Option 2: Python Package (Recommended for Production)
```bash
# Publish shared components as a package
pip install charlie-shared==1.0.0
```text

### Option 3: Copy + Sync (Simple but Manual)
- Copy `/shared/` into each service
- Manually sync changes across services

## Migration Strategy

### Phase 1: Reorganize Current Repository
1. Create `services/` directory structure
2. Move existing code into appropriate service directories
3. Update imports and dependencies
4. Test that each service can run independently

### Phase 2: Extract to Separate Repositories
1. Create individual repositories for each service
2. Set up Git submodules for shared components
3. Configure CI/CD for each service
4. Set up independent deployment pipelines

### Phase 3: Independent Development
1. Teams can work on services independently
2. Version shared components separately
3. Deploy services with different release cycles
4. Maintain overall system integration tests

## Development Workflow

### Single Repository Development (Current)
```bash
# Work on outlook-relay service
cd services/outlook-relay/
python src/main.py

# Work on database service
cd services/database-service/
python src/main.py
```text

### Multi-Repository Development (Future)
```bash
# Each service in its own repo
git clone https://github.com/yourorg/outlook-relay.git
cd outlook-relay/
git submodule update --init --recursive
python src/main.py
```text

## Benefits of This Structure

### 1. Repository Independence
- ✅ Each service can be copied to a new repository with minimal changes
- ✅ Independent versioning and release cycles
- ✅ Team ownership and access control per service

### 2. Shared Code Management
- ✅ Common patterns maintained in shared components
- ✅ Updates to shared code can be propagated to all services
- ✅ Version compatibility management

### 3. Deployment Flexibility
- ✅ Services can be deployed independently
- ✅ Different scaling requirements per service
- ✅ Technology stack evolution per service

### 4. Development Experience
- ✅ Smaller, focused codebases
- ✅ Faster CI/CD pipelines per service
- ✅ Clear service boundaries and responsibilities

## Implementation Steps

Let's implement this structure by:

1. **✅ Creating the service directories** in the current repository (DONE)
2. **Moving existing code** into the appropriate service structures  
3. **Setting up the shared component integration** (symlinks for development)
4. **Creating the first service** (Outlook Relay) as a working example
5. **Skip Docker** for now - focus on native Python execution

## Development-First Approach (No Docker)

### Service Execution
Each service runs as a standalone Python application:
```bash
# Run outlook-relay service
cd services/outlook-relay/
python src/main.py

# Run database service  
cd services/database-service/
python src/main.py

# Run all services (development script)
python tools/run-all-services.py
```text

### Shared Components Integration
For development, we'll use symlinks to share components:
```bash
# Create symlinks to shared components in each service
cd services/outlook-relay/
ln -s ../../shared ./shared

cd services/database-service/  
ln -s ../../shared ./shared
```text

This approach gives you both the immediate benefits of organized code and the future flexibility of independent repositories, while keeping development simple with native Python execution.
