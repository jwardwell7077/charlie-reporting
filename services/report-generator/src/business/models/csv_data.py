"""
CSV Data Domain Model
Represents CSV data transformation and processing rules
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import pandas as pd


@dataclass
class CSVRule:
    """Represents transformation rules for a specific CSV type"""
    file_pattern: str
    columns: List[str]
    sheet_name: str
    required_columns: Optional[List[str]] = None
    
    def matches_filename(self, filename: str) -> bool:
        """Check if filename matches this rule's pattern"""
        base_pattern = self.file_pattern.replace('.csv', '').lower()
        return base_pattern in filename.lower()
    
    def validate_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate DataFrame against rule requirements"""
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required columns
        required = self.required_columns or self.columns
        missing_cols = [col for col in required if col not in df.columns]
        if missing_cols:
            validation['errors'].append(f"Missing required columns: {missing_cols}")
            validation['is_valid'] = False
        
        # Check if selected columns exist
        missing_selected = [col for col in self.columns if col not in df.columns]
        if missing_selected:
            validation['errors'].append(f"Missing selected columns: {missing_selected}")
            validation['is_valid'] = False
        
        # Warnings for data quality
        if len(df) == 0:
            validation['warnings'].append("DataFrame is empty")
        elif len(df) < 5:
            validation['warnings'].append(f"Very few rows ({len(df)}) in DataFrame")
        
        return validation
    
    def get_safe_sheet_name(self) -> str:
        """Get Excel-safe sheet name (max 31 chars)"""
        return self.sheet_name[:31]


@dataclass
class CSVFile:
    """
    Domain model for CSV file with business logic
    """
    filename: str
    file_path: str
    date_str: str
    hour_str: Optional[str]
    timestamp: datetime
    rule: Optional[CSVRule] = None
    processed: bool = False
    
    def extract_timestamp_from_filename(self, fallback_date: str) -> str:
        """
        Business logic to extract timestamp from filename
        Migrated from transformer.py
        """
        # Try to extract hour from filename patterns like:
        # ACQ__2025-01-28_0900.csv
        # QCBS__2025-01-28_1425.csv
        
        import re
        
        # Pattern: __YYYY-MM-DD_HHMM
        pattern = r'__(\d{4}-\d{2}-\d{2})_(\d{4})'
        match = re.search(pattern, self.filename)
        
        if match:
            date_part = match.group(1)
            time_part = match.group(2)
            
            # Convert HHMM to HH:MM format
            if len(time_part) == 4:
                hour = time_part[:2]
                minute = time_part[2:]
                return f"{date_part} {hour}:{minute}:00"
        
        # Fallback to date only
        return f"{fallback_date} 00:00:00"
    
    def matches_date_filter(self, date_filter: str) -> bool:
        """Check if file matches date filter"""
        return f"__{date_filter}" in self.filename
    
    def matches_hour_filter(self, date_filter: str, hour_filter: str) -> bool:
        """Check if file matches both date and hour filters"""
        hour_pattern = f"__{date_filter}_{hour_filter}"
        return hour_pattern in self.filename
    
    def get_processing_priority(self) -> int:
        """
        Business rule: Determine processing priority
        Higher number = higher priority
        """
        # Priority based on file type
        priority_map = {
            'acq': 10,
            'qcbs': 9,
            'dials': 8,
            'productivity': 7,
            'ib_calls': 6,
            'resc': 5
        }
        
        filename_lower = self.filename.lower()
        for key, priority in priority_map.items():
            if key in filename_lower:
                return priority
        
        return 1  # Default low priority
    
    def is_critical_file(self) -> bool:
        """Business rule: Determine if file is critical for reporting"""
        critical_types = ['acq', 'qcbs', 'dials']
        filename_lower = self.filename.lower()
        return any(ctype in filename_lower for ctype in critical_types)


@dataclass
class CSVTransformationResult:
    """Result of CSV transformation process"""
    file: CSVFile
    dataframe: Optional[pd.DataFrame]
    success: bool
    error_message: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
