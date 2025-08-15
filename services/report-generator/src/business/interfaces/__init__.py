"""Business Layer Interface Contracts
Abstract interfaces for dependency injection and testing
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..models.csv_file import CSVFile


class IDirectoryProcessor(ABC):
    """Interface for directory processing operations"""

    @abstractmethod
    async def scan_directory(self, directory_path: Path, date_filter: str) -> list[Path]:
        """Scan directory for CSV files matching date filter"""
        pass

    @abstractmethod
    async def validate_directory(self, directory_path: Path) -> dict[str, Any]:
        """Validate directory exists and is accessible"""
        pass


class ICSVTransformer(ABC):
    """Interface for CSV transformation operations"""

    @abstractmethod
    async def transform_csv(self, csv_file: CSVFile, config: dict[str, Any]) -> dict[str, Any]:
        """Transform CSV file according to configuration rules"""
        pass

    @abstractmethod
    async def validate_csv_structure(self, csv_file: CSVFile) -> bool:
        """Validate CSV file has required structure"""
        pass


class IExcelGenerator(ABC):
    """Interface for Excel file generation"""

    @abstractmethod
    async def create_workbook(self, data: dict[str, Any]) -> bytes:
        """Create Excel workbook from transformed data"""
        pass

    @abstractmethod
    async def apply_formatting(self, workbook: bytes, rules: dict[str, Any]) -> bytes:
        """Apply formatting rules to Excel workbook"""
        pass


class IFileManager(ABC):
    """Interface for file system operations"""

    @abstractmethod
    async def save_file(self, content: bytes, file_path: Path) -> bool:
        """Save file to specified path"""
        pass

    @abstractmethod
    async def archive_file(self, source_path: Path, archive_path: Path) -> bool:
        """Archive file by moving to archive directory"""
        pass

    @abstractmethod
    async def file_exists(self, file_path: Path) -> bool:
        """Check if file exists"""
        pass


class IConfigManager(ABC):
    """Interface for configuration management"""

    @abstractmethod
    def get_attachment_config(self) -> dict[str, Any]:
        """Get attachment processing configuration"""
        pass

    @abstractmethod
    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate configuration structure and values"""
        pass


class ILogger(ABC):
    """Interface for logging operations"""

    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        """Log info message with optional context"""
        pass

    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        """Log error message with optional context"""
        pass

    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with optional context"""
        pass


class IMetricsCollector(ABC):
    """Interface for metrics collection"""

    @abstractmethod
    def increment_counter(self, metric_name: str, value: int = 1, tags: dict[str, str] | None = None) -> None:
        """Increment counter metric"""
        pass

    @abstractmethod
    def record_timing(self, metric_name: str, duration_seconds: float, tags: dict[str, str] | None = None) -> None:
        """Record timing metric"""
        pass

    @abstractmethod
    def set_gauge(self, metric_name: str, value: float, tags: dict[str, str] | None = None) -> None:
        """Set gauge metric value"""
        pass
