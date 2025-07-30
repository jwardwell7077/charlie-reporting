"""
Test Infrastructure Setup - Mock Services for Testing
Mock implementations of all business interfaces for isolated testing
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import asyncio

from business.interfaces import (
    IDirectoryProcessor,
    ICSVTransformer,
    IExcelGenerator,
    IFileManager,
    IConfigManager,
    ILogger,
    IMetricsCollector
)
from business.models.csv_file import CSVFile


class MockDirectoryProcessor(IDirectoryProcessor):
    """Mock implementation for testing directory operations"""
    
    def __init__(self):
        self.scan_calls = []
        self.validate_calls = []
        self.mock_files = []
        
    async def scan_directory(self, directory_path: Path, date_filter: str) -> List[Path]:
        self.scan_calls.append((directory_path, date_filter))
        return self.mock_files
        
    async def validate_directory(self, directory_path: Path) -> Dict[str, Any]:
        self.validate_calls.append(directory_path)
        return {"is_valid": True, "csv_count": len(self.mock_files)}


class MockCSVTransformer(ICSVTransformer):
    """Mock implementation for testing CSV transformation"""
    
    def __init__(self):
        self.transform_calls = []
        self.validate_calls = []
        self.mock_result = {"sheet_name": "Test", "data": []}
        
    async def transform_csv(self, csv_file: CSVFile, config: Dict[str, Any]) -> Dict[str, Any]:
        self.transform_calls.append((csv_file, config))
        return self.mock_result
        
    async def validate_csv_structure(self, csv_file: CSVFile) -> bool:
        self.validate_calls.append(csv_file)
        return True


class MockExcelGenerator(IExcelGenerator):
    """Mock implementation for testing Excel generation"""
    
    def __init__(self):
        self.create_calls = []
        self.format_calls = []
        self.mock_content = b"mock_excel_content"
        
    async def create_workbook(self, data: Dict[str, Any]) -> bytes:
        self.create_calls.append(data)
        return self.mock_content
        
    async def apply_formatting(self, workbook: bytes, rules: Dict[str, Any]) -> bytes:
        self.format_calls.append((workbook, rules))
        return workbook + b"_formatted"


class MockFileManager(IFileManager):
    """Mock implementation for testing file operations"""
    
    def __init__(self):
        self.save_calls = []
        self.archive_calls = []
        self.exists_calls = []
        self.mock_exists = True
        
    async def save_file(self, content: bytes, file_path: Path) -> bool:
        self.save_calls.append((content, file_path))
        return True
        
    async def archive_file(self, source_path: Path, archive_path: Path) -> bool:
        self.archive_calls.append((source_path, archive_path))
        return True
        
    async def file_exists(self, file_path: Path) -> bool:
        self.exists_calls.append(file_path)
        return self.mock_exists


class MockConfigManager(IConfigManager):
    """Mock implementation for testing configuration"""
    
    def __init__(self):
        self.get_calls = []
        self.validate_calls = []
        self.mock_config = {
            "rules": [
                {"pattern": "*.csv", "sheet_name": "Test", "columns": ["A", "B"]}
            ]
        }
        
    def get_attachment_config(self) -> Dict[str, Any]:
        self.get_calls.append("attachment_config")
        return self.mock_config
        
    def validate_config(self, config: Dict[str, Any]) -> bool:
        self.validate_calls.append(config)
        return True


class MockLogger(ILogger):
    """Mock implementation for testing logging"""
    
    def __init__(self):
        self.info_logs = []
        self.error_logs = []
        self.debug_logs = []
        
    def info(self, message: str, **kwargs) -> None:
        self.info_logs.append((message, kwargs))
        
    def error(self, message: str, **kwargs) -> None:
        self.error_logs.append((message, kwargs))
        
    def debug(self, message: str, **kwargs) -> None:
        self.debug_logs.append((message, kwargs))


class MockMetricsCollector(IMetricsCollector):
    """Mock implementation for testing metrics"""
    
    def __init__(self):
        self.counters = []
        self.timings = []
        self.gauges = []
        
    def increment_counter(self, metric_name: str, value: int = 1, tags: Optional[Dict[str, str]] = None) -> None:
        self.counters.append((metric_name, value, tags))
        
    def record_timing(self, metric_name: str, duration_seconds: float, tags: Optional[Dict[str, str]] = None) -> None:
        self.timings.append((metric_name, duration_seconds, tags))
        
    def set_gauge(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        self.gauges.append((metric_name, value, tags))
