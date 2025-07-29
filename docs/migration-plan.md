# Phase 2: Code Migration and Integration Plan

## Migration Strategy Overview

We're transitioning from the monolithic Phase 1 architecture in `src/` to the microservices Phase 2 architecture in `services/`. This document outlines the complete migration and integration plan.

## Current State Analysis

### Phase 1 (src/) - TO BE MIGRATED/DEPRECATED

- **main.py**: Monolithic entry point with ReportProcessor class
- **transformer.py**: CSV transformation business logic
- **email_fetcher.py**: Email processing and attachment handling
- **excel_writer.py**: Excel report generation
- **config_loader.py**: Configuration management
- **logger.py**: Logging utilities
- **archiver.py**: File archiving functionality
- **utils.py**: Utility functions

### Phase 2 (services/) - NEW ARCHITECTURE

- **report-generator/**: FastAPI microservice for CSV processing
- **email-service/**: Email handling microservice
- **database-service/**: Data persistence service
- **scheduler-service/**: Task scheduling service
- **outlook-relay/**: Outlook integration service

## Migration Plan

### Step 1: Extract and Integrate Business Logic

#### A. CSV Transformation Logic (`transformer.py` → `services/report-generator/`)

- Move CSVTransformer class logic into report-generator FastAPI service
- Integrate config-driven column selection
- Preserve data validation and cleaning logic
- Add API endpoints for transformation operations

#### B. Excel Generation Logic (`excel_writer.py` → `services/report-generator/`)

- Integrate ExcelWriter functionality into report-generator service
- Convert to async operations for better performance
- Add streaming support for large reports
- Maintain formatting and template capabilities

#### C. Email Processing (`email_fetcher.py` → `services/email-service/`)

- Extract email fetching logic into dedicated email service
- Modernize with Graph API instead of win32com
- Add support for multiple email accounts
- Implement proper async processing

#### D. Configuration Management (`config_loader.py` → `shared/`)

- Move to shared utilities for cross-service access
- Update to support microservices configuration
- Add environment-based configuration
- Implement configuration validation

### Step 2: Service Integration Points

#### A. Report Generator Service Enhancement

```python
# services/report-generator/csv_processor.py
class CSVProcessor:
    """Migrated from src/transformer.py"""
    
# services/report-generator/excel_generator.py  
class ExcelGenerator:
    """Migrated from src/excel_writer.py"""
```text

#### B. Email Service Implementation

```python
# services/email-service/main.py
class EmailProcessor:
    """Migrated from src/email_fetcher.py"""
```text

#### C. Shared Utilities

```python
# shared/config_manager.py
class ConfigManager:
    """Enhanced from src/config_loader.py"""
    
# shared/utils.py
"""Migrated utilities from src/utils.py"""
```text

### Step 3: API Gateway Integration

Create unified API gateway that:

- Routes requests to appropriate services
- Handles authentication and authorization
- Provides centralized logging and monitoring
- Manages service discovery

### Step 4: Backward Compatibility Bridge

Temporary compatibility layer:

- `legacy_bridge.py`: Maintains existing interfaces
- Gradual migration path for existing workflows
- Deprecation warnings for old interfaces

## Implementation Timeline

### Week 1: Core Service Migration

- [ ] Migrate CSVTransformer to report-generator service
- [ ] Migrate ExcelWriter to report-generator service  
- [ ] Update FastAPI service with business logic
- [ ] Add comprehensive API endpoints

### Week 2: Email Service & Integration

- [ ] Create dedicated email-service
- [ ] Migrate email fetching logic
- [ ] Implement Graph API integration
- [ ] Add async email processing

### Week 3: Configuration & Testing

- [ ] Migrate configuration management
- [ ] Create shared utilities package
- [ ] Implement comprehensive test suite
- [ ] Add integration tests

### Week 4: Deployment & Cleanup

- [ ] Deploy microservices architecture
- [ ] Create API gateway
- [ ] Remove deprecated src/ code
- [ ] Update documentation

## File Disposition Plan

### Files to MIGRATE (integrate into services)

- `src/transformer.py` → `services/report-generator/csv_processor.py`
- `src/excel_writer.py` → `services/report-generator/excel_generator.py`
- `src/email_fetcher.py` → `services/email-service/email_processor.py`
- `src/config_loader.py` → `shared/config_manager.py`
- `src/utils.py` → `shared/utils.py`
- `src/logger.py` → `shared/logging_utils.py`

### Files to DEPRECATE (replace with services)

- `src/main.py` → Replace with API gateway + service orchestration
- `src/archiver.py` → Integrate into file-management service

### New Service Structure

```text
services/
├── api-gateway/           # Central API routing
├── report-generator/      # CSV processing + Excel generation
├── email-service/         # Email processing + attachments
├── file-manager/          # File storage + management
├── scheduler-service/     # Task scheduling + cron jobs
└── notification-service/  # Alerts + reporting

shared/
├── config_manager.py      # Cross-service configuration
├── logging_utils.py       # Centralized logging
├── utils.py              # Common utilities
└── models/               # Shared data models
```text

## Migration Benefits

1. **Scalability**: Each service can scale independently
2. **Maintainability**: Clear separation of concerns
3. **Testability**: Isolated testing of each service
4. **Deployment**: Independent service deployments
5. **Monitoring**: Service-level monitoring and metrics
6. **Technology**: Modern async/await patterns, FastAPI
7. **Integration**: API-first design for future integrations

## Risk Mitigation

1. **Gradual Migration**: Phase-by-phase migration with testing
2. **Backward Compatibility**: Temporary bridge for existing workflows
3. **Comprehensive Testing**: Unit, integration, and end-to-end tests
4. **Rollback Plan**: Ability to revert to Phase 1 if needed
5. **Documentation**: Clear migration guides and API documentation

## Success Criteria

- [ ] All Phase 1 business logic successfully migrated
- [ ] No functionality regression
- [ ] Performance improvements in processing
- [ ] Comprehensive test coverage (>90%)
- [ ] Clean, maintainable codebase
- [ ] Zero downtime migration
- [ ] Complete deprecation of `src/` directory

This migration plan ensures we preserve all valuable business logic while modernizing the architecture for future scalability and maintainability.
