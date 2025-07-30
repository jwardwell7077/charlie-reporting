"""
CSV Transformation Service
Pure business logic for CSV data transformation - migrated from src/transformer.py
"""

from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
import pandas as pd
import os
import shutil

from ..models.csv_data import CSVFile, CSVRule, CSVTransformationResult
from ..models.report import Report, ReportSheet
from ..interfaces import ICSVTransformer
from datetime import datetime


class CSVTransformationService:
    """
    Business service for CSV transformation operations
    Pure domain logic without infrastructure dependencies
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def create_transformation_rules(self, attachment_config: Dict[str, Any]) -> List[CSVRule]:
        """
        Convert configuration to domain rules
        """
        rules = []
        for key, cfg in attachment_config.items():
            rule = CSVRule(
                file_pattern=key,
                columns=cfg.get('columns', []),
                sheet_name=key.replace('.csv', ''),
                required_columns=cfg.get('required_columns')
            )
            rules.append(rule)
        
        self.logger.debug(f"Created {len(rules)} transformation rules")
        return rules
    
    def discover_csv_files(self, raw_dir: Path, date_filter: str, hour_filter: Optional[str] = None) -> List[CSVFile]:
        """
        Business logic for discovering CSV files to process
        """
        csv_files = []
        
        if not raw_dir.exists():
            self.logger.warning(f"Raw directory does not exist: {raw_dir}")
            return csv_files
        
        for file_path in raw_dir.iterdir():
            if not file_path.suffix.lower() == '.csv':
                continue
            
            filename = file_path.name
            
            # Check date filter
            if not f"__{date_filter}" in filename:
                self.logger.debug(f"Skipping {filename}: date mismatch")
                continue
            
            # Check hour filter if specified
            if hour_filter:
                hour_pattern = f"__{date_filter}_{hour_filter}"
                if hour_pattern not in filename:
                    self.logger.debug(f"Skipping {filename}: hour mismatch") 
                    continue
            
            # Extract hour from filename
            hour_str = self._extract_hour_from_filename(filename)
            
            csv_file = CSVFile(
                filename=filename,
                file_path=str(file_path),
                date_str=date_filter,
                hour_str=hour_str,
                timestamp=datetime.now()
            )
            
            csv_files.append(csv_file)
        
        # Sort by processing priority
        csv_files.sort(key=lambda x: x.get_processing_priority(), reverse=True)
        
        self.logger.info(f"Discovered {len(csv_files)} CSV files for processing")
        return csv_files
    
    def match_files_to_rules(self, csv_files: List[CSVFile], rules: List[CSVRule]) -> List[CSVFile]:
        """
        Business logic for matching files to transformation rules
        """
        matched_files = []
        
        for csv_file in csv_files:
            matching_rule = None
            
            for rule in rules:
                if rule.matches_filename(csv_file.filename):
                    matching_rule = rule
                    break
            
            if matching_rule:
                csv_file.rule = matching_rule
                matched_files.append(csv_file)
                self.logger.debug(f"Matched {csv_file.filename} to rule {matching_rule.file_pattern}")
            else:
                self.logger.warning(f"No matching rule for: {csv_file.filename}")
        
        return matched_files
    
    def transform_csv_file(self, csv_file: CSVFile) -> CSVTransformationResult:
        """
        Transform a single CSV file according to its rule
        """
        if not csv_file.rule:
            return CSVTransformationResult(
                file=csv_file,
                dataframe=None,
                success=False,
                error_message="No transformation rule assigned"
            )
        
        try:
            # Read the CSV file
            df = pd.read_csv(csv_file.file_path)
            self.logger.debug(f"Read CSV {csv_file.filename}: {len(df)} rows, {len(df.columns)} columns")
            
            # Validate against rule
            validation = csv_file.rule.validate_dataframe(df)
            if not validation['is_valid']:
                return CSVTransformationResult(
                    file=csv_file,
                    dataframe=None,
                    success=False,
                    error_message="; ".join(validation['errors']),
                    warnings=validation['warnings']
                )
            
            # Select configured columns
            df_transformed = df[csv_file.rule.columns].copy()
            
            # Add metadata columns
            df_transformed = self._add_metadata_columns(df_transformed, csv_file)
            
            return CSVTransformationResult(
                file=csv_file,
                dataframe=df_transformed,
                success=True,
                warnings=validation['warnings']
            )
            
        except Exception as e:
            self.logger.error(f"Error transforming {csv_file.filename}: {e}", exc_info=True)
            return CSVTransformationResult(
                file=csv_file,
                dataframe=None,
                success=False,
                error_message=str(e)
            )
    
    def create_report_from_results(self, 
                                  transformation_results: List[CSVTransformationResult],
                                  date_str: str,
                                  hour_filter: Optional[str] = None) -> Report:
        """
        Business logic for creating a report from transformation results
        """
        sheets = {}
        
        # Group results by sheet name
        for result in transformation_results:
            if not result.success or result.dataframe is None:
                continue
            
            sheet_name = result.file.rule.get_safe_sheet_name() if result.file.rule else "Unknown"
            
            if sheet_name not in sheets:
                sheets[sheet_name] = ReportSheet(
                    name=sheet_name,
                    data_frames=[],
                    columns=list(result.dataframe.columns)
                )
            
            sheets[sheet_name].data_frames.append(result.dataframe)
        
        # Create report
        report = Report(
            date_str=date_str,
            report_type="csv_transformation",
            sheets=sheets,
            created_at=datetime.now(),
            hour_filter=hour_filter
        )
        
        self.logger.info(f"Created report with {len(sheets)} sheets, {report.get_total_records()} total records")
        return report
    
    def archive_processed_files(self, 
                               successful_results: List[CSVTransformationResult],
                               archive_dir: Path) -> Dict[str, str]:
        """
        Business logic for archiving successfully processed files
        """
        archived_files = {}
        
        # Ensure archive directory exists
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        for result in successful_results:
            if not result.success:
                continue
            
            try:
                source_path = Path(result.file.file_path)
                archive_path = archive_dir / result.file.filename
                
                # Move file to archive
                shutil.move(str(source_path), str(archive_path))
                
                archived_files[result.file.filename] = str(archive_path)
                self.logger.info(f"Archived file: {result.file.filename}")
                
            except Exception as e:
                self.logger.error(f"Failed to archive {result.file.filename}: {e}")
        
        return archived_files
    
    def _add_metadata_columns(self, df: pd.DataFrame, csv_file: CSVFile) -> pd.DataFrame:
        """Add metadata columns to DataFrame"""
        # Insert date column if missing
        if 'email_received_date' not in df.columns:
            df.insert(0, 'email_received_date', csv_file.date_str)
        
        # Insert timestamp column if missing  
        if 'email_received_timestamp' not in df.columns:
            timestamp_str = csv_file.extract_timestamp_from_filename(csv_file.date_str)
            df.insert(1, 'email_received_timestamp', timestamp_str)
        
        return df
    
    def _extract_hour_from_filename(self, filename: str) -> Optional[str]:
        """Extract hour from filename pattern"""
        import re
        
        # Pattern: __YYYY-MM-DD_HHMM
        pattern = r'__\d{4}-\d{2}-\d{2}_(\d{2})\d{2}'
        match = re.search(pattern, filename)
        
        if match:
            return match.group(1)
        
        return None


class CSVTransformerService(ICSVTransformer):
    """
    Implementation of ICSVTransformer interface
    Adapter for the existing CSVTransformationService
    """
    
    def __init__(self):
        self._service = CSVTransformationService()
    
    async def transform_csv(
        self, file_path: str, rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform CSV file according to rules"""
        try:
            # Convert rules dict to CSVRule objects
            transformation_rules = self._service.create_transformation_rules(
                rules
            )
            
            # Create CSV file object
            csv_file = CSVFile(
                filename=Path(file_path).name,
                file_path=file_path,
                date_str="",  # Will be extracted by service
                hour_str="",  # Will be extracted by service
                timestamp=datetime.utcnow(),
                rule=transformation_rules[0] if transformation_rules else None
            )
            
            # Perform transformation
            result = self._service.transform_csv_file(csv_file)
            
            return {
                "success": result.success,
                "file_path": csv_file.file_path,
                "dataframe": result.dataframe,
                "message": "Transformation completed" if result.success else "Transformation failed",
                "error": result.error_message,
                "warnings": result.warnings or []
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Transformation failed"
            }
    
    async def validate_csv_format(self, file_path: str) -> Dict[str, Any]:
        """Validate CSV file format"""
        try:
            # Use pandas to validate basic CSV structure
            df = pd.read_csv(file_path, nrows=1)
            
            return {
                "valid": True,
                "columns": list(df.columns),
                "column_count": len(df.columns),
                "message": "CSV format is valid"
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "message": "Invalid CSV format"
            }
