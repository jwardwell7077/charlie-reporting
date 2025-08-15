"""CSV data domain models and transformation rule artifacts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pandas as pd


@dataclass(slots=True)
class CSVRule:
    """Transformation rule for a CSV file pattern."""

    file_pattern: str
    columns: list[str]
    sheet_name: str
    required_columns: list[str] | None = None

    def matches_filename(self, file_name: str) -> bool:
        pattern = self.file_pattern.replace(".csv", "").lower()
        return pattern in file_name.lower()

    def validate_dataframe(self, df: pd.DataFrame) -> dict[str, Any]:
        result: dict[str, Any] = {"is_valid": True, "errors": [], "warnings": []}
        required = self.required_columns or self.columns
        missing_required = [c for c in required if c not in df.columns]
        if missing_required:
            result["errors"].append(f"Missing required columns: {missing_required}")
            result["is_valid"] = False
        missing_selected = [c for c in self.columns if c not in df.columns]
        if missing_selected:
            result["errors"].append(f"Missing selected columns: {missing_selected}")
            result["is_valid"] = False
        if df.empty:
            result["warnings"].append("DataFrame is empty")
        elif len(df.index) < 5:
            result["warnings"].append(f"Very few rows ({len(df.index)}) in DataFrame")
        return result

    def get_safe_sheet_name(self) -> str:
        return self.sheet_name[:31]


@dataclass(slots=True)
class CSVFile:
    """Represents a CSV file with metadata and rule association."""

    file_name: str
    file_path: str
    date_str: str
    hour_str: str | None
    timestamp: datetime
    rule: CSVRule | None = None
    processed: bool = False

    def extract_timestamp_from_filename(self, fallback_date: str) -> str:
        pattern = r"__(\d{4}-\d{2}-\d{2})_(\d{4})"
        match = re.search(pattern, self.file_name)
        if match:
            date_part, time_part = match.group(1), match.group(2)
            hour, minute = time_part[:2], time_part[2:]
            return f"{date_part} {hour}:{minute}:00"
        return f"{fallback_date} 00:00:00"

    def matches_date_filter(self, date_filter: str) -> bool:
        return f"__{date_filter}" in self.file_name

    def matches_hour_filter(self, date_filter: str, hour_filter: str) -> bool:
        return f"__{date_filter}_{hour_filter}" in self.file_name

    def get_processing_priority(self) -> int:
        priority_map = {"acq": 10, "qcbs": 9, "dials": 8, "productivity": 7, "ib_calls": 6, "resc": 5}
        lower = self.file_name.lower()
        for key, val in priority_map.items():
            if key in lower:
                return val
        return 1

    def is_critical_file(self) -> bool:
        return any(t in self.file_name.lower() for t in ["acq", "qcbs", "dials"])


@dataclass(slots=True)
class CSVTransformationResult:
    file: CSVFile
    dataframe: pd.DataFrame | None
    success: bool
    error_message: str | None = None
    warnings: list[str] | None = None

    def __post_init__(self) -> None:
        if self.warnings is None:
            self.warnings = []
