"""Report business domain models.

Defines the core reporting entities and related business validation logic.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pandas as pd

# Domain constants
MIN_VALID_SHEET_RECORDS = 10
QUALITY_SCORE_WARNING_THRESHOLD = 0.5


@dataclass(slots=True)
class QualityReport:
    """Structured quality evaluation result for a report."""
    is_valid: bool
    errors: list[str]
    warnings: list[str]
    quality_score: float


@dataclass
class ReportSheet:
    """Represents a single sheet in a report."""
    name: str
    data_frames: list[pd.DataFrame]
    columns: list[str]
    row_count: int = 0

    def __post_init__(self) -> None:
        """Calculate row count after initialization."""
        self.row_count = sum(len(df) for df in self.data_frames)

    def get_combined_data(self) -> pd.DataFrame:
        """Combine all data frames for this sheet."""
        if not self.data_frames:
            return pd.DataFrame()

        if len(self.data_frames) == 1:
            return self.data_frames[0]

        return pd.concat(self.data_frames, ignore_index=True)

    def validate_columns(self, required_columns: list[str]) -> bool:
        """Validate that all required columns are present."""
        if not self.data_frames:
            return False
        first_df = self.data_frames[0]
        return all(col in first_df.columns for col in required_columns)


@dataclass(slots=True)
class Report:
    """Core domain model for reports.

    Encapsulates business logic for report aggregation and quality evaluation.
    """
    date_str: str
    report_type: str
    sheets: dict[str, ReportSheet]
    created_at: datetime
    hour_filter: str | None = None
    output_path: str | None = None

    def get_total_records(self) -> int:
        """Get total number of records across all sheets."""
        return sum(sheet.row_count for sheet in self.sheets.values())

    def get_sheet_names(self) -> list[str]:
        """Get list of all sheet names."""
        return list(self.sheets.keys())

    def has_data(self) -> bool:
        """Check if the report has any data."""
        return bool(self.sheets) and self.get_total_records() > 0

    def get_report_summary(self) -> dict[str, Any]:
        """Generate summary statistics for the report."""
        return {
            'date': self.date_str,
            'hour_filter': self.hour_filter,
            'report_type': self.report_type,
            'total_sheets': len(self.sheets),
            'total_records': self.get_total_records(),
            'sheets': {
                name: {
                    'records': sheet.row_count,
                    'columns': len(sheet.columns)
                }
                for name, sheet in self.sheets.items()
            },
            'created_at': self.created_at.isoformat()
        }

    def validate_report_quality(self) -> QualityReport:
        """Evaluate report quality and return a structured result."""
        # Empty report case
        if not self.has_data():
            return QualityReport(
                is_valid=False,
                errors=["Report contains no data"],
                warnings=[],
                quality_score=0.0,
            )

        valid_sheets = 0
        warnings: list[str] = []

        for name, sheet in self.sheets.items():
            if sheet.row_count == 0:
                warnings.append(f"Sheet '{name}' is empty")
            elif sheet.row_count < MIN_VALID_SHEET_RECORDS:
                warnings.append(
                    f"Sheet '{name}' has very few records ({sheet.row_count})"
                )
            else:
                valid_sheets += 1

        quality_score = valid_sheets / len(self.sheets) if self.sheets else 0.0

        if quality_score < QUALITY_SCORE_WARNING_THRESHOLD:
            warnings.append("More than half of sheets have quality issues")

        return QualityReport(
            is_valid=quality_score > 0,
            errors=[],
            warnings=warnings,
            quality_score=quality_score,
        )

    def get_filename_suggestion(self, prefix: str = "report") -> str:
        """Generate suggested filename for the report."""
        if self.hour_filter:
            return f"{prefix}_{self.date_str}_{self.hour_filter}.xlsx"
        return f"{prefix}_{self.date_str}.xlsx"
