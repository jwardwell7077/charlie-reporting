"""
Excel Report Generation Service
Pure business logic for Excel report creation - migrated from src/excel_writer.py
"""

from typing import Dict, List, Optional, Any
import logging
from pathlib import Path
import pandas as pd
from datetime import datetime

from ..models.report import Report, ReportSheet


class ExcelReportService:
    """
    Business service for Excel report generation
    Pure domain logic without infrastructure dependencies
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def validate_report_for_excel(self, report: Report) -> Dict[str, Any]:
        """
        Business rules for Excel report validation
        """
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Check if report has data
        if not report.has_data():
            validation['errors'].append("Report contains no data")
            validation['is_valid'] = False
            return validation
        
        # Validate individual sheets
        for sheet_name, sheet in report.sheets.items():
            # Check sheet name length (Excel limit)
            if len(sheet_name) > 31:
                validation['warnings'].append(f"Sheet name '{sheet_name}' exceeds Excel limit (31 chars)")
            
            # Check for empty sheets
            if sheet.row_count == 0:
                validation['warnings'].append(f"Sheet '{sheet_name}' is empty")
            
            # Check for very large sheets (Excel performance)
            if sheet.row_count > 100000:
                validation['warnings'].append(f"Sheet '{sheet_name}' has {sheet.row_count} rows - may cause performance issues")
            
            # Validate data consistency within sheet
            if len(sheet.data_frames) > 1:
                combined_data = sheet.get_combined_data()
                if combined_data.empty:
                    validation['warnings'].append(f"Sheet '{sheet_name}' failed to combine data frames")
        
        # Recommendations
        if len(report.sheets) > 10:
            validation['recommendations'].append("Consider splitting large reports into multiple files")
        
        return validation
    
    def prepare_excel_data(self, report: Report) -> Dict[str, pd.DataFrame]:
        """
        Prepare report data for Excel writing
        Combines multiple DataFrames per sheet and applies Excel-specific formatting
        """
        excel_data = {}
        
        for sheet_name, sheet in report.sheets.items():
            try:
                # Get safe sheet name for Excel
                safe_name = self._get_safe_sheet_name(sheet_name)
                
                # Combine all DataFrames for this sheet
                combined_df = sheet.get_combined_data()
                
                if not combined_df.empty:
                    # Apply Excel-specific data cleaning
                    cleaned_df = self._clean_dataframe_for_excel(combined_df)
                    excel_data[safe_name] = cleaned_df
                    
                    self.logger.debug(f"Prepared sheet '{safe_name}' with {len(cleaned_df)} rows")
                else:
                    self.logger.warning(f"Sheet '{sheet_name}' has no data after combining")
                    
            except Exception as e:
                self.logger.error(f"Error preparing sheet '{sheet_name}': {e}")
        
        return excel_data
    
    def generate_filename(self, report: Report, prefix: str = "report", suffix: str = "") -> str:
        """
        Business logic for generating Excel filenames
        """
        # Base filename from report
        base_name = report.get_filename_suggestion(prefix)
        
        # Add suffix if provided
        if suffix:
            name_parts = base_name.rsplit('.', 1)
            if len(name_parts) == 2:
                base_name = f"{name_parts[0]}_{suffix}.{name_parts[1]}"
            else:
                base_name = f"{base_name}_{suffix}"
        
        # Ensure .xlsx extension
        if not base_name.lower().endswith('.xlsx'):
            base_name = base_name.replace('.xls', '.xlsx')
            if not base_name.lower().endswith('.xlsx'):
                base_name += '.xlsx'
        
        return base_name
    
    def create_incremental_update_strategy(self, 
                                         existing_file: Optional[Path],
                                         new_report: Report) -> Dict[str, Any]:
        """
        Business logic for incremental Excel updates
        """
        strategy = {
            'update_type': 'full_replace',  # default
            'target_sheets': [],
            'backup_needed': False,
            'merge_strategy': {}
        }
        
        if not existing_file or not existing_file.exists():
            strategy['update_type'] = 'create_new'
            return strategy
        
        # If existing file exists, determine update strategy
        strategy['backup_needed'] = True
        
        # For hourly updates, append to existing sheets
        if new_report.hour_filter:
            strategy['update_type'] = 'append_data'
            strategy['target_sheets'] = list(new_report.sheets.keys())
            
            # Define merge strategy for each sheet
            for sheet_name in strategy['target_sheets']:
                strategy['merge_strategy'][sheet_name] = {
                    'method': 'append',
                    'sort_columns': ['email_received_timestamp'],
                    'deduplicate': True
                }
        else:
            # Full day report - replace everything
            strategy['update_type'] = 'full_replace'
        
        return strategy
    
    def calculate_report_size_estimate(self, report: Report) -> Dict[str, Any]:
        """
        Estimate Excel file size and complexity
        """
        total_cells = 0
        total_rows = 0
        
        for sheet in report.sheets.values():
            sheet_data = sheet.get_combined_data()
            if not sheet_data.empty:
                rows, cols = sheet_data.shape
                total_cells += rows * cols
                total_rows += rows
        
        # Rough size estimation (bytes)
        estimated_size_mb = total_cells * 10 / (1024 * 1024)  # Very rough estimate
        
        return {
            'total_sheets': len(report.sheets),
            'total_rows': total_rows,
            'total_cells': total_cells,
            'estimated_size_mb': round(estimated_size_mb, 2),
            'complexity_level': self._assess_complexity(report),
            'performance_warnings': self._get_performance_warnings(total_rows, total_cells)
        }
    
    def _get_safe_sheet_name(self, sheet_name: str) -> str:
        """Convert sheet name to Excel-safe format"""
        # Excel sheet name limitations
        invalid_chars = ['[', ']', '*', '?', ':', '/', '\\']
        safe_name = sheet_name
        
        for char in invalid_chars:
            safe_name = safe_name.replace(char, '_')
        
        # Limit to 31 characters
        if len(safe_name) > 31:
            safe_name = safe_name[:31]
        
        # Ensure not empty
        if not safe_name:
            safe_name = "Sheet"
        
        return safe_name
    
    def _clean_dataframe_for_excel(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean DataFrame for Excel compatibility
        """
        df_clean = df.copy()
        
        # Handle None/NaN values
        df_clean = df_clean.fillna('')
        
        # Convert datetime columns to string for Excel compatibility
        for col in df_clean.columns:
            if df_clean[col].dtype == 'datetime64[ns]':
                df_clean[col] = df_clean[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Ensure string columns don't have problematic characters
        string_cols = df_clean.select_dtypes(include=['object']).columns
        for col in string_cols:
            df_clean[col] = df_clean[col].astype(str)
            # Remove problematic characters that can break Excel
            df_clean[col] = df_clean[col].str.replace('\x00', '')  # Null bytes
        
        return df_clean
    
    def _assess_complexity(self, report: Report) -> str:
        """Assess report complexity level"""
        total_records = report.get_total_records()
        sheet_count = len(report.sheets)
        
        if total_records > 50000 or sheet_count > 10:
            return 'high'
        elif total_records > 10000 or sheet_count > 5:
            return 'medium'
        else:
            return 'low'
    
    def _get_performance_warnings(self, total_rows: int, total_cells: int) -> List[str]:
        """Generate performance warnings based on data size"""
        warnings = []
        
        if total_rows > 100000:
            warnings.append(f"Large dataset ({total_rows:,} rows) may cause slow Excel performance")
        
        if total_cells > 1000000:
            warnings.append(f"Very large number of cells ({total_cells:,}) may cause memory issues")
        
        return warnings
