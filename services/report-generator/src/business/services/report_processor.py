"""
Main Report Processing Service
Orchestrates the complete report generation workflow
"""

from typing import List, Dict, Any, Optional, Tuple
import logging
from pathlib import Path
from datetime import datetime

from ..models.csv_data import CSVFile, CSVRule, CSVTransformationResult
from ..models.report import Report
from .csv_transformer import CSVTransformationService
from .excel_service import ExcelReportService
from ..exceptions import BusinessException


class ReportProcessingService:
    """
    Main business service that orchestrates the complete report generation workflow
    Coordinates CSV transformation, report building, and Excel generation
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.csv_transformer = CSVTransformationService(logger)
        self.excel_service = ExcelReportService(logger)
    
    def process_directory_reports(self, 
                                 raw_dir: Path,
                                 archive_dir: Path,
                                 output_dir: Path,
                                 attachment_config: Dict[str, Any],
                                 date_filter: str,
                                 hour_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete workflow for processing CSV files in a directory
        
        Args:
            raw_dir: Directory containing raw CSV files
            archive_dir: Directory to archive processed files
            output_dir: Directory for Excel output files
            attachment_config: Configuration for file processing rules
            date_filter: Date filter for file selection (YYYY-MM-DD)
            hour_filter: Optional hour filter for file selection
            
        Returns:
            Dictionary with processing results and statistics
        """
        processing_start = datetime.utcnow()
        
        try:
            # Step 1: Create transformation rules from configuration
            self.logger.info("Creating transformation rules from configuration")
            rules = self.csv_transformer.create_transformation_rules(attachment_config)
            
            # Step 2: Discover CSV files in directory
            self.logger.info(f"Discovering CSV files in {raw_dir} for date {date_filter}")
            discovered_files = self.csv_transformer.discover_csv_files(raw_dir, date_filter, hour_filter)
            
            # Step 3: Match files to transformation rules
            self.logger.info("Matching files to transformation rules")
            matched_files = self.csv_transformer.match_files_to_rules(discovered_files, rules)
            
            # Step 4: Transform each CSV file
            self.logger.info(f"Transforming {len(matched_files)} CSV files")
            transformation_results = []
            for csv_file in matched_files:
                result = self.csv_transformer.transform_csv_file(csv_file)
                transformation_results.append(result)
                
                if result.success:
                    self.logger.debug(f"Successfully transformed: {csv_file.filename}")
                else:
                    self.logger.error(f"Failed to transform {csv_file.filename}: {result.error_message}")
            
            # Step 5: Create report from successful transformations
            successful_results = [r for r in transformation_results if r.success]
            if not successful_results:
                raise BusinessException("No files were successfully transformed")
            
            self.logger.info(f"Creating report from {len(successful_results)} successful transformations")
            report = self.csv_transformer.create_report_from_results(
                successful_results, date_filter, hour_filter
            )
            
            # Step 6: Validate report for Excel generation
            self.logger.info("Validating report for Excel generation")
            excel_validation = self.excel_service.validate_report_for_excel(report)
            if not excel_validation['is_valid']:
                error_msg = "; ".join(excel_validation['errors'])
                raise BusinessException(f"Report validation failed: {error_msg}")
            
            # Step 7: Generate Excel file
            self.logger.info("Generating Excel file")
            excel_filename = self.excel_service.generate_filename(
                report, 
                prefix="charlie_report", 
                suffix=hour_filter if hour_filter else ""
            )
            
            # Step 8: Archive processed files
            self.logger.info("Archiving successfully processed files")
            archived_files = self.csv_transformer.archive_processed_files(
                successful_results, archive_dir
            )
            
            # Calculate processing statistics
            processing_end = datetime.utcnow()
            processing_time = (processing_end - processing_start).total_seconds()
            
            results = {
                "success": True,
                "processing_time_seconds": processing_time,
                "discovered_files": len(discovered_files),
                "matched_files": len(matched_files),
                "transformed_files": len(successful_results),
                "failed_files": len(transformation_results) - len(successful_results),
                "report_sheets": len(report.sheets),
                "total_records": report.get_total_records(),
                "excel_filename": excel_filename,
                "archived_files": list(archived_files.keys()),
                "warnings": [],
                "errors": []
            }
            
            # Collect warnings from transformations and Excel validation
            for result in transformation_results:
                if result.warnings:
                    results["warnings"].extend(result.warnings)
            
            if excel_validation.get('warnings'):
                results["warnings"].extend(excel_validation['warnings'])
            
            # Log failed transformations as errors
            failed_results = [r for r in transformation_results if not r.success]
            for failed in failed_results:
                error_msg = f"Failed to process {failed.file.filename}: {failed.error_message}"
                results["errors"].append(error_msg)
            
            self.logger.info(f"Report processing completed successfully in {processing_time:.2f}s")
            self.logger.info(f"Generated report with {len(report.sheets)} sheets and {report.get_total_records()} total records")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Report processing failed: {str(e)}", exc_info=True)
            processing_end = datetime.utcnow()
            processing_time = (processing_end - processing_start).total_seconds()
            
            return {
                "success": False,
                "error_message": str(e),
                "processing_time_seconds": processing_time,
                "discovered_files": 0,
                "matched_files": 0,
                "transformed_files": 0,
                "failed_files": 0,
                "report_sheets": 0,
                "total_records": 0,
                "excel_filename": None,
                "archived_files": [],
                "warnings": [],
                "errors": [str(e)]
            }
    
    def process_single_file(self, 
                           file_path: Path,
                           rule: CSVRule,
                           output_dir: Path) -> Dict[str, Any]:
        """
        Process a single CSV file with specific rule
        
        Args:
            file_path: Path to the CSV file
            rule: Transformation rule to apply
            output_dir: Directory for output files
            
        Returns:
            Dictionary with processing results
        """
        processing_start = datetime.utcnow()
        
        try:
            # Create CSV file object
            csv_file = CSVFile(
                filename=file_path.name,
                file_path=str(file_path),
                date_str=datetime.now().strftime("%Y-%m-%d"),
                hour_str=None,
                timestamp=datetime.now(),
                rule=rule
            )
            
            # Transform the file
            self.logger.info(f"Transforming single file: {file_path.name}")
            result = self.csv_transformer.transform_csv_file(csv_file)
            
            if not result.success:
                raise BusinessException(f"Transformation failed: {result.error_message}")
            
            # Create report from single result
            report = self.csv_transformer.create_report_from_results(
                [result], 
                csv_file.date_str
            )
            
            # Validate and prepare for Excel
            excel_validation = self.excel_service.validate_report_for_excel(report)
            if not excel_validation['is_valid']:
                error_msg = "; ".join(excel_validation['errors'])
                raise BusinessException(f"Report validation failed: {error_msg}")
            
            # Generate Excel filename
            excel_filename = self.excel_service.generate_filename(
                report, 
                prefix=file_path.stem
            )
            
            processing_end = datetime.utcnow()
            processing_time = (processing_end - processing_start).total_seconds()
            
            return {
                "success": True,
                "processing_time_seconds": processing_time,
                "source_file": file_path.name,
                "excel_filename": excel_filename,
                "report_sheets": len(report.sheets),
                "total_records": report.get_total_records(),
                "warnings": result.warnings or [],
                "errors": []
            }
            
        except Exception as e:
            self.logger.error(f"Single file processing failed: {str(e)}", exc_info=True)
            processing_end = datetime.utcnow()
            processing_time = (processing_end - processing_start).total_seconds()
            
            return {
                "success": False,
                "error_message": str(e),
                "processing_time_seconds": processing_time,
                "source_file": file_path.name if file_path else "unknown",
                "excel_filename": None,
                "report_sheets": 0,
                "total_records": 0,
                "warnings": [],
                "errors": [str(e)]
            }
    
    def validate_input_directory(self, raw_dir: Path) -> Dict[str, Any]:
        """
        Validate input directory for processing
        
        Args:
            raw_dir: Directory to validate
            
        Returns:
            Validation results
        """
        validation = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "csv_file_count": 0,
            "directory_exists": False
        }
        
        try:
            # Check if directory exists
            if not raw_dir.exists():
                validation["errors"].append(f"Directory does not exist: {raw_dir}")
                validation["is_valid"] = False
                return validation
            
            validation["directory_exists"] = True
            
            # Check if it's actually a directory
            if not raw_dir.is_dir():
                validation["errors"].append(f"Path is not a directory: {raw_dir}")
                validation["is_valid"] = False
                return validation
            
            # Count CSV files
            csv_files = list(raw_dir.glob("*.csv"))
            validation["csv_file_count"] = len(csv_files)
            
            if len(csv_files) == 0:
                validation["warnings"].append("No CSV files found in directory")
            
            # Check directory permissions
            if not raw_dir.stat().st_mode & 0o444:  # Read permission
                validation["errors"].append("Directory is not readable")
                validation["is_valid"] = False
            
        except PermissionError:
            validation["errors"].append("Permission denied accessing directory")
            validation["is_valid"] = False
        except Exception as e:
            validation["errors"].append(f"Unexpected error validating directory: {str(e)}")
            validation["is_valid"] = False
        
        return validation
    
    def get_processing_statistics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate detailed processing statistics
        
        Args:
            results: Processing results from process_directory_reports or process_single_file
            
        Returns:
            Enhanced statistics
        """
        stats = {
            "success_rate": 0.0,
            "files_per_second": 0.0,
            "records_per_second": 0.0,
            "processing_efficiency": "unknown",
            "recommendations": []
        }
        
        if results.get("processing_time_seconds", 0) > 0:
            # Calculate rates
            total_files = results.get("discovered_files", 0)
            successful_files = results.get("transformed_files", 0)
            total_records = results.get("total_records", 0)
            processing_time = results["processing_time_seconds"]
            
            if total_files > 0:
                stats["success_rate"] = (successful_files / total_files) * 100
                stats["files_per_second"] = total_files / processing_time
            
            if total_records > 0:
                stats["records_per_second"] = total_records / processing_time
            
            # Assess efficiency
            if processing_time < 10:
                stats["processing_efficiency"] = "excellent"
            elif processing_time < 30:
                stats["processing_efficiency"] = "good"
            elif processing_time < 60:
                stats["processing_efficiency"] = "moderate"
            else:
                stats["processing_efficiency"] = "slow"
                stats["recommendations"].append("Consider optimizing data processing or reducing file sizes")
            
            # Additional recommendations
            if stats["success_rate"] < 100:
                stats["recommendations"].append("Review failed file transformations for data quality issues")
            
            if len(results.get("warnings", [])) > 0:
                stats["recommendations"].append("Review processing warnings to improve data quality")
        
        return stats
    
    def create_processing_summary(self, results: Dict[str, Any]) -> str:
        """
        Create a human-readable processing summary
        
        Args:
            results: Processing results
            
        Returns:
            Formatted summary string
        """
        if results.get("success"):
            summary = f"""Report Processing Summary:
✅ Successfully processed {results.get('transformed_files', 0)} of {results.get('discovered_files', 0)} files
📊 Generated {results.get('report_sheets', 0)} sheets with {results.get('total_records', 0):,} total records
⏱️  Processing completed in {results.get('processing_time_seconds', 0):.2f} seconds
📁 Excel file: {results.get('excel_filename', 'unknown')}
🗃️  Archived {len(results.get('archived_files', []))} files"""
            
            if results.get('warnings'):
                summary += f"\n⚠️  {len(results['warnings'])} warnings generated"
            
            if results.get('failed_files', 0) > 0:
                summary += f"\n❌ {results['failed_files']} files failed to process"
        else:
            summary = f"""Report Processing Failed:
❌ Error: {results.get('error_message', 'Unknown error')}
⏱️  Failed after {results.get('processing_time_seconds', 0):.2f} seconds"""
        
        return summary
