"""
CSV Processing Module for Report Generator Service
Migrated and enhanced from src/transformer.py
"""
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any
import os
from datetime import datetime

import sys
import os
from pathlib import Path

# Add shared directory to path
shared_path = Path(__file__).parent.parent.parent / 'shared'
sys.path.append(str(shared_path))

from logging_utils import LoggerFactory

class CSVProcessor:
    """
    Enhanced CSV processing with config-driven transformations.
    Migrated from src/transformer.py with improvements for microservices architecture.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = LoggerFactory.get_logger('csv_processor')
        self.attachment_rules = config.get('attachment_rules', {})
    
    async def process_csv_files(self, file_paths: List[str], date_filter: Optional[str] = None, 
                               hour_filter: Optional[str] = None) -> Dict[str, List[pd.DataFrame]]:
        """
        Process multiple CSV files with optional date/hour filtering.
        
        Args:
            file_paths: List of CSV file paths to process
            date_filter: Optional date string (YYYY-MM-DD) for filtering
            hour_filter: Optional hour string (HH) for filtering
            
        Returns:
            Dictionary mapping sheet names to lists of DataFrames
        """
        self.logger.info(f"Processing {len(file_paths)} CSV files")
        result_data = {}
        
        for file_path in file_paths:
            try:
                # Apply date/hour filtering if specified
                if self._should_process_file(file_path, date_filter, hour_filter):
                    processed_data = await self._process_single_file(file_path)
                    
                    # Merge results
                    for sheet_name, df_list in processed_data.items():
                        if sheet_name not in result_data:
                            result_data[sheet_name] = []
                        result_data[sheet_name].extend(df_list)
                        
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {str(e)}")
                continue
        
        return result_data
    
    async def _process_single_file(self, file_path: str) -> Dict[str, List[pd.DataFrame]]:
        """Process a single CSV file according to configuration rules."""
        filename = Path(file_path).name
        self.logger.info(f"Processing file: {filename}")
        
        # Find matching configuration rule
        rule_config = self._find_matching_rule(filename)
        if not rule_config:
            self.logger.warning(f"No configuration rule found for {filename}")
            return {}
        
        # Read and process CSV
        try:
            df = pd.read_csv(file_path)
            
            # Apply transformations
            processed_df = await self._apply_transformations(df, rule_config, filename)
            
            # Determine sheet name
            sheet_name = rule_config.get('sheet_name', self._extract_sheet_name(filename))
            
            return {sheet_name: [processed_df]}
            
        except Exception as e:
            self.logger.error(f"Error reading CSV {file_path}: {str(e)}")
            return {}
    
    async def _apply_transformations(self, df: pd.DataFrame, rule_config: Dict[str, Any], 
                                   filename: str) -> pd.DataFrame:
        """Apply configuration-driven transformations to DataFrame."""
        
        # Select columns based on configuration
        columns = rule_config.get('columns', [])
        if columns:
            # Filter to only existing columns
            available_columns = [col for col in columns if col in df.columns]
            if available_columns:
                df = df[available_columns]
                self.logger.debug(f"Selected {len(available_columns)} columns for {filename}")
        
        # Add email received date
        df = self._add_email_date(df, filename)
        
        # Apply data cleaning
        df = self._clean_data(df)
        
        # Apply custom transformations if specified
        transformations = rule_config.get('transformations', [])
        for transform in transformations:
            df = await self._apply_custom_transformation(df, transform)
        
        return df
    
    def _add_email_date(self, df: pd.DataFrame, filename: str) -> pd.DataFrame:
        """Add email_received_date column based on filename."""
        try:
            # Extract date from filename (format: NAME__YYYY-MM-DD_HHMM.csv)
            if '__' in filename:
                date_part = filename.split('__')[1].split('.')[0]
                if '_' in date_part:
                    date_str = date_part.split('_')[0]
                    # Validate and parse date
                    email_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    df['email_received_date'] = email_date
                    self.logger.debug(f"Added email_received_date: {email_date}")
                    
        except Exception as e:
            self.logger.warning(f"Could not extract date from filename {filename}: {str(e)}")
            # Fallback to current date
            df['email_received_date'] = datetime.now().date()
        
        return df
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply standard data cleaning operations."""
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Strip whitespace from string columns
        string_columns = df.select_dtypes(include=['object']).columns
        for col in string_columns:
            df[col] = df[col].astype(str).str.strip()
        
        # Replace empty strings with NaN
        df = df.replace('', pd.NA)
        
        self.logger.debug(f"Data cleaning completed. Rows: {len(df)}")
        return df
    
    async def _apply_custom_transformation(self, df: pd.DataFrame, 
                                         transform_config: Dict[str, Any]) -> pd.DataFrame:
        """Apply custom transformation based on configuration."""
        transform_type = transform_config.get('type')
        
        if transform_type == 'aggregate':
            return self._apply_aggregation(df, transform_config)
        elif transform_type == 'filter':
            return self._apply_filter(df, transform_config)
        elif transform_type == 'calculate':
            return self._apply_calculation(df, transform_config)
        else:
            self.logger.warning(f"Unknown transformation type: {transform_type}")
            return df
    
    def _apply_aggregation(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Apply aggregation transformation."""
        group_by = config.get('group_by', [])
        agg_functions = config.get('aggregations', {})
        
        if group_by and agg_functions:
            df = df.groupby(group_by).agg(agg_functions).reset_index()
            self.logger.debug(f"Applied aggregation: grouped by {group_by}")
        
        return df
    
    def _apply_filter(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Apply filter transformation."""
        filters = config.get('filters', {})
        
        for column, criteria in filters.items():
            if column in df.columns:
                if isinstance(criteria, dict):
                    operator = criteria.get('operator', '==')
                    value = criteria.get('value')
                    
                    if operator == '==':
                        df = df[df[column] == value]
                    elif operator == '!=':
                        df = df[df[column] != value]
                    elif operator == '>':
                        df = df[df[column] > value]
                    elif operator == '<':
                        df = df[df[column] < value]
                    elif operator == 'in':
                        df = df[df[column].isin(value)]
                    
                    self.logger.debug(f"Applied filter: {column} {operator} {value}")
        
        return df
    
    def _apply_calculation(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Apply calculation transformation."""
        calculations = config.get('calculations', [])
        
        for calc in calculations:
            new_column = calc.get('column')
            expression = calc.get('expression')
            
            if new_column and expression:
                try:
                    # Simple expression evaluation (extend as needed)
                    df[new_column] = df.eval(expression)
                    self.logger.debug(f"Added calculated column: {new_column}")
                except Exception as e:
                    self.logger.error(f"Error in calculation {expression}: {str(e)}")
        
        return df
    
    def _find_matching_rule(self, filename: str) -> Optional[Dict[str, Any]]:
        """Find configuration rule that matches the filename."""
        filename_lower = filename.lower()
        
        for rule_key, rule_config in self.attachment_rules.items():
            # Extract base name from rule key
            base_rule_name = rule_key.replace('.csv', '').lower()
            if base_rule_name in filename_lower:
                return rule_config
        
        return None
    
    def _extract_sheet_name(self, filename: str) -> str:
        """Extract sheet name from filename."""
        # Remove timestamp and extension to get base name
        base_name = filename.split('__')[0] if '__' in filename else filename
        base_name = base_name.replace('.csv', '')
        return base_name.upper()
    
    def _should_process_file(self, file_path: str, date_filter: Optional[str], 
                           hour_filter: Optional[str]) -> bool:
        """Check if file should be processed based on date/hour filters."""
        filename = Path(file_path).name
        
        # Check date filter
        if date_filter and f"__{date_filter}" not in filename:
            return False
        
        # Check hour filter
        if hour_filter and date_filter:
            hour_pattern = f"__{date_filter}_{hour_filter}"
            if hour_pattern not in filename:
                return False
        
        return True
    
    async def validate_csv_structure(self, file_path: str) -> Dict[str, Any]:
        """Validate CSV file structure and return metadata."""
        try:
            df = pd.read_csv(file_path, nrows=5)  # Read just first few rows
            
            return {
                'valid': True,
                'columns': list(df.columns),
                'row_count_sample': len(df),
                'data_types': df.dtypes.to_dict(),
                'has_header': True,
                'issues': []
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'issues': [f"Failed to read CSV: {str(e)}"]
            }
    
    async def get_processing_stats(self, file_paths: List[str]) -> Dict[str, Any]:
        """Get statistics about files to be processed."""
        stats = {
            'total_files': len(file_paths),
            'valid_files': 0,
            'invalid_files': 0,
            'total_size_mb': 0,
            'file_types': {},
            'estimated_processing_time': 0
        }
        
        for file_path in file_paths:
            file_size = Path(file_path).stat().st_size / (1024 * 1024)  # MB
            stats['total_size_mb'] += file_size
            
            # Validate file
            validation = await self.validate_csv_structure(file_path)
            if validation['valid']:
                stats['valid_files'] += 1
            else:
                stats['invalid_files'] += 1
            
            # Track file types by rule matching
            rule = self._find_matching_rule(Path(file_path).name)
            rule_name = rule.get('sheet_name', 'unknown') if rule else 'unknown'
            stats['file_types'][rule_name] = stats['file_types'].get(rule_name, 0) + 1
        
        # Estimate processing time (rough calculation)
        stats['estimated_processing_time'] = stats['total_size_mb'] * 2  # 2 seconds per MB
        
        return stats
