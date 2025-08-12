"""
Business domain models for processing results and operations
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class ProcessingResult:
    """Result of processing operations"""
    success: bool
    files_processed: int
    total_records: int
    processing_time_seconds: float
    output_file: Optional[str] = None
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.timestamp is None:
            self.timestamp = datetime.now()

    @property
    def has_errors(self) -> bool:
        """Check if result has any errors"""
        return len(self.errors or []) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if result has any warnings"""
        return len(self.warnings or []) > 0

    def add_error(self, error: str):
        """Add an error to the result"""
        if self.errors is None:
            self.errors = []
        self.errors.append(error)
        self.success = False

    def add_warning(self, warning: str):
        """Add a warning to the result"""
        if self.warnings is None:
            self.warnings = []
        self.warnings.append(warning)


@dataclass
class FileInfo:
    """Information about a file being processed"""
    file_name: str
    file_path: str
    file_type: str
    date_str: str
    hour_str: str
    rule: str
    record_count: int = 0
    file_size_bytes: int = 0

    @property
    def display_name(self) -> str:
        """Human readable display name"""
        return f"{self.file_type}_{self.date_str}_{self.hour_str}.csv"


@dataclass
class ProcessingConfig:
    """Configuration for processing operations"""
    input_directory: str
    output_directory: str
    num_records: int = 50
    file_pattern: str = "*.csv"
    max_processing_time_seconds: float = 30.0
    enable_logging: bool = True
    enable_metrics: bool = True
