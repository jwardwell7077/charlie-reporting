# TDD-Optimized Architecture Design

**Document Version**: 1.0  
**Date**: July 29, 2025  
**Purpose**: Architectural improvements to fully support Test-Driven Development practices

---

## 🎯 **Architecture Principles**

### **1. Plan and Architect Before Implement**

- All architectural changes must be documented before implementation
- Design decisions require written justification and alternatives analysis
- Implementation follows approved architectural blueprints

### **2. Test-First Design**

- Every component designed with testability as primary concern
- Clear separation between testable business logic and infrastructure
- Dependency injection enables easy mocking and isolation

### **3. Interface-Driven Development**

- All external dependencies accessed through abstract interfaces
- Contracts defined before implementations
- Multiple implementations supported (production, test, mock)

---

## 🏗️ **Current Architecture Issues**

### **❌ Problems Identified**

1. **Hard-to-Test Global Dependencies**

   ```python
   # Current problematic pattern in app.py
   report_processor = ReportProcessingService()  # Global instance
   metrics_collector = MetricsCollector()        # Hard to mock
   structured_logger = StructuredLogger()        # Tightly coupled
   ```

2. **Inconsistent Directory Structure**
   - Both `interface/` and `interfaces/` directories exist
   - Doesn't match documented project structure
   - Confuses test organization

3. **Tight Service Coupling**
   - Services directly instantiate dependencies
   - No abstraction for external systems
   - Difficult to test in isolation

4. **Missing Test Infrastructure**
   - No shared test utilities
   - No mock implementations
   - No test data factories

---

## ✅ **TDD-Optimized Architecture Solution**

### **1. Dependency Injection Pattern**

#### **Abstract Interfaces**

```python
# business/interfaces/repositories.py
from abc import ABC, abstractmethod
from typing import List, Optional
from ..models.csv_data import CSVFile

class CSVFileRepository(ABC):
    @abstractmethod
    async def save_processed_file(self, csv_file: CSVFile) -> None: ...
    
    @abstractmethod
    async def get_files_by_date(self, date: str) -> List[CSVFile]: ...
    
    @abstractmethod
    async def archive_file(self, file_path: str) -> bool: ...

# business/interfaces/excel_service.py
class ExcelService(ABC):
    @abstractmethod
    async def generate_workbook(self, data: Dict[str, Any]) -> bytes: ...
    
    @abstractmethod
    async def apply_formatting(self, workbook: bytes, rules: Dict) -> bytes: ...

# business/interfaces/file_storage.py
class FileStorageService(ABC):
    @abstractmethod
    async def save_file(self, content: bytes, path: str) -> str: ...
    
    @abstractmethod
    async def get_file(self, path: str) -> bytes: ...
```

#### **Dependency Injection Configuration**

```python
# interface/dependencies.py
from functools import lru_cache
from typing import Annotated
from fastapi import Depends

from business.services.report_processor import ReportProcessingService
from business.interfaces.repositories import CSVFileRepository
from business.interfaces.excel_service import ExcelService
from infrastructure.persistence.csv_repository import SQLiteCSVRepository
from infrastructure.excel.excel_service_impl import OpenpyxlExcelService

@lru_cache()
def get_csv_repository() -> CSVFileRepository:
    return SQLiteCSVRepository()

@lru_cache()
def get_excel_service() -> ExcelService:
    return OpenpyxlExcelService()

@lru_cache()  
def get_report_processor(
    csv_repo: Annotated[CSVFileRepository, Depends(get_csv_repository)],
    excel_service: Annotated[ExcelService, Depends(get_excel_service)]
) -> ReportProcessingService:
    return ReportProcessingService(
        csv_repository=csv_repo,
        excel_service=excel_service
    )
```

### **2. Standardized Directory Structure**

#### **Production Code Structure**

```text
src/
├── business/                    # Pure domain logic (90%+ test coverage)
│   ├── interfaces/             # Abstract dependency contracts
│   │   ├── repositories.py     # Data persistence contracts
│   │   ├── excel_service.py    # Excel generation contracts
│   │   └── file_storage.py     # File storage contracts
│   ├── models/                 # Domain entities and value objects
│   │   ├── csv_data.py         # CSV file domain models
│   │   ├── report.py           # Report domain models
│   │   └── processing_result.py # Processing outcome models
│   ├── services/               # Business logic services
│   │   ├── report_processor.py # Main orchestration service
│   │   ├── csv_transformer.py  # CSV transformation logic
│   │   └── validation_service.py # Business rule validation
│   └── exceptions.py           # Business domain exceptions
├── interface/                  # External communication layer
│   ├── rest/                   # REST API endpoints
│   │   ├── routes.py           # FastAPI route definitions
│   │   └── middleware.py       # Custom middleware
│   ├── schemas.py              # Pydantic request/response models
│   ├── dependencies.py         # FastAPI dependency injection
│   └── app.py                  # FastAPI application factory
├── infrastructure/             # External system implementations
│   ├── persistence/            # Data storage implementations
│   │   ├── csv_repository.py   # SQLite CSV repository impl
│   │   └── file_system.py      # File system operations
│   ├── excel/                  # Excel service implementations
│   │   └── excel_service_impl.py # openpyxl implementation
│   ├── monitoring/             # Observability implementations
│   │   ├── metrics.py          # Prometheus metrics
│   │   ├── logging.py          # Structured logging
│   │   └── health.py           # Health check implementations
│   └── external/               # External service clients
│       └── email_client.py     # Email service client
└── config/                     # Configuration management
    ├── settings.py             # Pydantic settings models
    └── environments/           # Environment-specific configs
```

#### **Test Structure**

```text
tests/
├── unit/                       # Pure business logic tests
│   └── business/               # Test business layer in isolation
│       ├── test_models.py      # Domain entity behavior tests
│       ├── test_services.py    # Business service logic tests
│       └── test_validation.py  # Business rule validation tests
├── integration/                # Component interaction tests
│   ├── interface/              # API endpoint tests
│   │   ├── test_rest_api.py    # FastAPI endpoint tests
│   │   └── test_schemas.py     # Pydantic validation tests
│   └── infrastructure/         # External dependency tests
│       ├── test_repositories.py # Database operation tests
│       └── test_excel_service.py # Excel generation tests
├── e2e/                        # End-to-end workflow tests
│   ├── test_complete_workflows.py # Full processing pipelines
│   └── test_error_scenarios.py    # Error handling workflows
├── fixtures/                   # Test data and utilities
│   ├── factories.py            # Test data factory functions
│   ├── mock_services.py        # Mock service implementations
│   └── test_data/              # Sample CSV files and data
│       ├── sample_csvs/        # Test CSV files
│       └── expected_outputs/   # Expected Excel outputs
└── conftest.py                 # Shared pytest configuration
```

### **3. Test Infrastructure Design**

#### **Mock Service Implementations**

```python
# tests/fixtures/mock_services.py
from typing import List, Dict, Any
from business.interfaces.repositories import CSVFileRepository
from business.interfaces.excel_service import ExcelService
from business.models.csv_data import CSVFile

class MockCSVRepository(CSVFileRepository):
    def __init__(self):
        self._files: Dict[str, CSVFile] = {}
        self._archived: List[str] = []
    
    async def save_processed_file(self, csv_file: CSVFile) -> None:
        self._files[csv_file.filename] = csv_file
    
    async def get_files_by_date(self, date: str) -> List[CSVFile]:
        return [f for f in self._files.values() if f.date_str == date]
    
    async def archive_file(self, file_path: str) -> bool:
        self._archived.append(file_path)
        return True

class MockExcelService(ExcelService):
    async def generate_workbook(self, data: Dict[str, Any]) -> bytes:
        # Return mock Excel content
        return b"mock_excel_content"
    
    async def apply_formatting(self, workbook: bytes, rules: Dict) -> bytes:
        return workbook + b"_formatted"
```

#### **Test Data Factories**

```python
# tests/fixtures/factories.py
from datetime import datetime
from pathlib import Path
from business.models.csv_data import CSVFile, CSVRule

class CSVFileFactory:
    @staticmethod
    def create_sample_csv(
        filename: str = "test_file.csv",
        date_str: str = "2025-07-29",
        record_count: int = 100
    ) -> CSVFile:
        return CSVFile(
            filename=filename,
            file_path=f"/test/data/{filename}",
            date_str=date_str,
            hour_str="09",
            timestamp=datetime.utcnow(),
            rule=CSVRuleFactory.create_sample_rule(),
            record_count=record_count
        )

class CSVRuleFactory:
    @staticmethod
    def create_sample_rule() -> CSVRule:
        return CSVRule(
            pattern="*.csv",
            columns=["Column1", "Column2", "Column3"],
            sheet_name="Test Sheet",
            required_columns=["Column1"]
        )
```

### **4. Configuration-Driven Testing**

#### **Test Settings**

```python
# config/test_settings.py
from pydantic import BaseSettings
from pathlib import Path

class TestSettings(BaseSettings):
    # Database
    database_url: str = "sqlite:///:memory:"
    
    # File paths
    test_data_dir: Path = Path(__file__).parent.parent / "tests/fixtures/test_data"
    temp_output_dir: Path = Path("/tmp/charlie-test-output")
    
    # External services
    mock_external_services: bool = True
    api_timeout_seconds: int = 5
    
    # Test behavior
    cleanup_temp_files: bool = True
    log_level: str = "DEBUG"
    
    class Config:
        env_prefix = "TEST_"
```

#### **Test Configuration**

```python
# tests/conftest.py
import pytest
import asyncio
from fastapi.testclient import TestClient
from pathlib import Path

from config.test_settings import TestSettings
from interface.app import create_app
from tests.fixtures.mock_services import MockCSVRepository, MockExcelService

@pytest.fixture(scope="session")
def test_settings():
    return TestSettings()

@pytest.fixture(scope="session") 
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_app(test_settings):
    """Create FastAPI test application with test dependencies"""
    app = create_app(test_mode=True, settings=test_settings)
    return app

@pytest.fixture
def test_client(test_app):
    """Create test client for API testing"""
    return TestClient(test_app)

@pytest.fixture
def mock_csv_repository():
    """Mock CSV repository for testing"""
    return MockCSVRepository()

@pytest.fixture
def mock_excel_service():
    """Mock Excel service for testing"""  
    return MockExcelService()

@pytest.fixture
def sample_csv_files(test_settings):
    """Create sample CSV files for testing"""
    test_data_dir = test_settings.test_data_dir / "sample_csvs"
    test_data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample CSV files
    sample_files = []
    for i in range(3):
        csv_path = test_data_dir / f"test_file_{i}.csv"
        csv_path.write_text(f"Column1,Column2,Column3\nValue{i}A,Value{i}B,Value{i}C\n")
        sample_files.append(csv_path)
    
    yield sample_files
    
    # Cleanup
    if test_settings.cleanup_temp_files:
        for file_path in sample_files:
            file_path.unlink(missing_ok=True)
```

---

## 🚀 **Implementation Phases**

### **Phase A: Clean Directory Structure (15 min)**

1. Remove duplicate `interfaces/` directory
2. Organize existing code into proper layers
3. Update import statements

### **Phase B: Implement Dependency Injection (30 min)**

1. Create abstract interfaces in `business/interfaces/`
2. Implement dependency injection in `interface/dependencies.py`
3. Refactor services to use constructor injection

### **Phase C: Test Infrastructure (30 min)**

1. Create mock service implementations
2. Set up test data factories
3. Configure pytest with shared fixtures

### **Phase D: Validation (15 min)**

1. Run existing tests to ensure no regressions
2. Implement one complete TDD cycle as proof of concept
3. Measure test coverage to establish baseline

---

## 📊 **Success Metrics**

### **Technical Quality**

- **Test Coverage**: 90%+ business layer, 80%+ overall
- **Test Speed**: Unit tests < 1s, integration tests < 10s
- **Test Isolation**: No shared state between tests
- **Mock Coverage**: All external dependencies mockable

### **Developer Experience**

- **Fast Feedback**: Tests run quickly during development
- **Clear Failures**: Test failures clearly indicate problem location
- **Easy Setup**: New developers can run tests immediately
- **Comprehensive**: Tests cover happy path, edge cases, and error conditions

### **Architecture Quality**

- **Loose Coupling**: Business logic independent of infrastructure
- **High Cohesion**: Related functionality grouped together
- **Clear Interfaces**: All dependencies accessed through abstractions
- **Testable Design**: All components easily testable in isolation

---

## 🎯 **Portfolio Value**

This TDD-optimized architecture demonstrates:

- **Enterprise Architecture Skills**: Proper layering and separation of concerns
- **Test-Driven Development**: Complete TDD implementation with supporting infrastructure
- **Dependency Injection**: Modern software design patterns
- **Interface Design**: Abstract thinking and contract-based development
- **Quality Engineering**: Comprehensive testing strategy and metrics

**Ready for implementation following the "Plan and Architect Before Implement" principle.**

---

*Architecture document completed: July 29, 2025*  
*Ready for systematic implementation with full TDD support*
