"""
Report Business Domain Model
Represents a report entity with its data and metadata
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
import pandas as pd


@dataclass
class ReportSheet:
    """Represents a single sheet in a report"""
    name: str
    data_frames: List[pd.DataFrame]
    columns: List[str]
    row_count: int = 0
    
    def __post_init__(self):
        """Calculate row count after initialization"""
        self.row_count = sum(len(df) for df in self.data_frames)
    
    def get_combined_data(self) -> pd.DataFrame:
        """Combine all data frames for this sheet"""
        if not self.data_frames:
            return pd.DataFrame()
        
        if len(self.data_frames) == 1:
            return self.data_frames[0]
        
        return pd.concat(self.data_frames, ignore_index=True)
    
    def validate_columns(self, required_columns: List[str]) -> bool:
        """Validate that all required columns are present"""
        if not self.data_frames:
            return False
        
        first_df = self.data_frames[0]
        return all(col in first_df.columns for col in required_columns)


@dataclass 
class Report:
    """
    Core domain model for reports
    Business logic for report operations
    """
    date_str: str
    report_type: str
    sheets: Dict[str, ReportSheet]
    created_at: datetime
    hour_filter: Optional[str] = None
    output_path: Optional[str] = None
    
    def get_total_records(self) -> int:
        """Get total number of records across all sheets"""
        return sum(sheet.row_count for sheet in self.sheets.values())
    
    def get_sheet_names(self) -> List[str]:
        """Get list of all sheet names"""
        return list(self.sheets.keys())
    
    def has_data(self) -> bool:
        """Check if report has any data"""
        return bool(self.sheets) and self.get_total_records() > 0
    
    def get_report_summary(self) -> Dict[str, Any]:
        """Generate summary statistics for the report"""
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
    
    def validate_report_quality(self) -> Dict[str, Any]:
        """Business rules for report quality validation"""
        quality_report = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'quality_score': 0.0
        }
        
        # Check for empty report
        if not self.has_data():
            quality_report['errors'].append("Report contains no data")
            quality_report['is_valid'] = False
            return quality_report
        
        # Check individual sheets
        valid_sheets = 0
        for name, sheet in self.sheets.items():
            if sheet.row_count == 0:
                quality_report['warnings'].append(f"Sheet '{name}' is empty")
            elif sheet.row_count < 10:
                quality_report['warnings'].append(f"Sheet '{name}' has very few records ({sheet.row_count})")
            else:
                valid_sheets += 1
        
        # Calculate quality score
        if len(self.sheets) > 0:
            quality_report['quality_score'] = valid_sheets / len(self.sheets)
        
        # Additional validations
        if quality_report['quality_score'] < 0.5:
            quality_report['warnings'].append("More than half of sheets have quality issues")
        
        return quality_report
    
    def get_filename_suggestion(self, prefix: str = "report") -> str:
        """Generate suggested filename for report"""
        if self.hour_filter:
            return f"{prefix}_{self.date_str}_{self.hour_filter}.xlsx"
        else:
            return f"{prefix}_{self.date_str}.xlsx"
