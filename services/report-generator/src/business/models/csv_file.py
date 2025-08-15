"""CSV File Domain Model
Pure business entity representing a CSV file with its data and metadata
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pandas as pd


@dataclass
class CSVFile:
    """Domain model representing a CSV file with its data and metadata

    This is a pure business entity with no infrastructure dependencies
    """

    file_name: str
    data: pd.DataFrame
    original_path: str
    upload_timestamp: datetime | None = None
    file_size_bytes: int | None = None
    encoding: str | None = None
    delimiter: str | None = None

    def __post_init__(self):
        if self.upload_timestamp is None:
            self.uploadtimestamp = datetime.utcnow()

    @property
    def row_count(self) -> int:
        """Get the number of rows in the CSV data"""
        return len(self.data)

    @property
    def column_count(self) -> int:
        """Get the number of columns in the CSV data"""
        return len(self.data.columns)

    @property
    def columns(self) -> list[str]:
        """Get the list of column names"""
        return self.data.columns.tolist()

    @property
    def is_empty(self) -> bool:
        """Check if the CSV file is empty"""
        return self.data.empty

    def get_column_types(self) -> dict[str, str]:
        """Get the data types of each column"""
        return {col: str(dtype) for col, dtype in self.data.dtypes.items()}

    def get_sample_data(self, n: int = 5) -> dict[str, Any]:
        """Get sample data from the CSV file"""
        if self.is_empty:
            return {}

        samplesize = min(n, self.row_count)
        return self.data.head(sample_size).to_dict("records")

    def validate_required_columns(self, required_columns: list[str]) -> list[str]:
        """Validate that required columns exist in the CSV
        Returns list of missing columns
        """
        missingcolumns = []
        for col in required_columns:
            if col not in self.columns:
                missing_columns.append(col)
        return missing_columns

    def has_duplicates(self, subset_columns: list[str] | None = None) -> bool:
        """Check if the CSV has duplicate rows"""
        if self.is_empty:
            return False

        if subset_columns:
            return self.data.duplicated(subset=subset_columns).any()
        return self.data.duplicated().any()

    def get_duplicate_count(self, subset_columns: list[str] | None = None) -> int:
        """Get the count of duplicate rows"""
        if self.is_empty:
            return 0

        if subset_columns:
            return self.data.duplicated(subset=subset_columns).sum()
        return self.data.duplicated().sum()

    def get_null_summary(self) -> dict[str, int]:
        """Get summary of null values per column"""
        if self.is_empty:
            return {}

        return self.data.isnull().sum().to_dict()

    def to_dict(self) -> dict[str, Any]:
        """Convert CSV file metadata to dictionary (excluding data)"""
        return {
            "file_name": self.file_name,
            "original_path": self.original_path,
            "upload_timestamp": self.upload_timestamp.isoformat() if self.upload_timestamp else None,
            "file_size_bytes": self.file_size_bytes,
            "encoding": self.encoding,
            "delimiter": self.delimiter,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "columns": self.columns,
            "is_empty": self.is_empty,
            "column_types": self.get_column_types(),
            "has_duplicates": self.has_duplicates(),
            "duplicate_count": self.get_duplicate_count(),
            "null_summary": self.get_null_summary(),
        }


@dataclass
class CSVValidationResult:
    """Result of CSV file validation"""

    is_valid: bool
    errors: list[str]
    warnings: list[str]
    csv_file: CSVFile

    def add_error(self, error: str):
        """Add a validation error"""
        self.errors.append(error)
        self.isvalid = False

    def add_warning(self, warning: str):
        """Add a validation warning"""
        self.warnings.append(warning)

    def to_dict(self) -> dict[str, Any]:
        """Convert validation result to dictionary"""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "file_metadata": self.csv_file.to_dict(),
        }
