"""
API Schema Models for Report Generator Service
Pydantic models for request/response validation and API documentation
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class ProcessingStatus(str, Enum):
    """Processing status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportType(str, Enum):
    """Report type enumeration"""
    CSV_TRANSFORMATION = "csv_transformation"
    EXCEL_REPORT = "excel_report"
    CUSTOM = "custom"


class DirectoryProcessRequest(BaseModel):
    """Request model for directory-based report processing"""
    raw_directory: str = Field(..., description="Path to directory containing raw CSV files")
    archive_directory: str = Field(..., description="Path to directory for archiving processed files")
    output_directory: str = Field(..., description="Path to directory for output Excel files")
    date_filter: str = Field(..., description="Date filter in YYYY-MM-DD format", pattern=r"^\d{4}-\d{2}-\d{2}$")
    hour_filter: Optional[str] = Field(None, description="Optional hour filter in HH format", pattern=r"^\d{2}$")
    attachment_config: Dict[str, Any] = Field(..., description="Configuration for file processing rules")
    
    @validator('date_filter')
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')
    
    @validator('hour_filter')
    def validate_hour_format(cls, v):
        if v is not None:
            try:
                hour = int(v)
                if not 0 <= hour <= 23:
                    raise ValueError('Hour must be between 00 and 23')
            except ValueError:
                raise ValueError('Hour must be a valid integer between 00 and 23')
        return v


class SingleFileProcessRequest(BaseModel):
    """Request model for single file processing"""
    file_path: str = Field(..., description="Path to the CSV file to process")
    output_directory: str = Field(..., description="Path to directory for output Excel file")
    file_pattern: str = Field(..., description="File pattern for transformation rule")
    columns: List[str] = Field(..., description="Columns to extract from CSV")
    sheet_name: str = Field(..., description="Name for Excel sheet")
    required_columns: Optional[List[str]] = Field(None, description="Required columns for validation")


class ProcessingResult(BaseModel):
    """Response model for processing results"""
    success: bool = Field(..., description="Whether processing was successful")
    processing_time_seconds: float = Field(..., description="Time taken for processing")
    message: Optional[str] = Field(None, description="Human-readable status message")
    
    # File statistics
    discovered_files: Optional[int] = Field(None, description="Number of files discovered")
    matched_files: Optional[int] = Field(None, description="Number of files matched to rules")
    transformed_files: Optional[int] = Field(None, description="Number of successfully transformed files")
    failed_files: Optional[int] = Field(None, description="Number of files that failed processing")
    
    # Report statistics
    report_sheets: Optional[int] = Field(None, description="Number of sheets in generated report")
    total_records: Optional[int] = Field(None, description="Total number of records processed")
    excel_filename: Optional[str] = Field(None, description="Name of generated Excel file")
    
    # Processing details
    archived_files: List[str] = Field(default_factory=list, description="List of archived file names")
    warnings: List[str] = Field(default_factory=list, description="Processing warnings")
    errors: List[str] = Field(default_factory=list, description="Processing errors")
    error_message: Optional[str] = Field(None, description="Primary error message if processing failed")


class DirectoryValidationRequest(BaseModel):
    """Request model for directory validation"""
    directory_path: str = Field(..., description="Path to directory to validate")


class DirectoryValidationResult(BaseModel):
    """Response model for directory validation"""
    is_valid: bool = Field(..., description="Whether directory is valid for processing")
    directory_exists: bool = Field(..., description="Whether directory exists")
    csv_file_count: int = Field(..., description="Number of CSV files found")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")


class ProcessingStatistics(BaseModel):
    """Enhanced processing statistics"""
    success_rate: float = Field(..., description="Success rate as percentage (0-100)")
    files_per_second: float = Field(..., description="Files processed per second")
    records_per_second: float = Field(..., description="Records processed per second")
    processing_efficiency: str = Field(..., description="Efficiency rating: excellent, good, moderate, slow")
    recommendations: List[str] = Field(default_factory=list, description="Performance recommendations")


class ReportInfo(BaseModel):
    """Information about a generated report"""
    report_id: str = Field(..., description="Unique identifier for the report")
    report_type: ReportType = Field(..., description="Type of report generated")
    created_at: datetime = Field(..., description="When the report was created")
    file_path: Optional[str] = Field(None, description="Path to the generated file")
    sheet_count: int = Field(..., description="Number of sheets in the report")
    total_records: int = Field(..., description="Total number of records in the report")
    processing_time_seconds: float = Field(..., description="Time taken to generate the report")


class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Current timestamp")
    version: str = Field(..., description="Service version")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")
    checks: Dict[str, bool] = Field(..., description="Individual health check results")


class ServiceMetrics(BaseModel):
    """Service metrics response model"""
    total_requests: int = Field(..., description="Total number of requests processed")
    successful_requests: int = Field(..., description="Number of successful requests")
    failed_requests: int = Field(..., description="Number of failed requests")
    avg_processing_time_seconds: float = Field(..., description="Average processing time")
    total_files_processed: int = Field(..., description="Total files processed")
    total_records_processed: int = Field(..., description="Total records processed")
    uptime_seconds: float = Field(..., description="Service uptime")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request ID for tracing")


class ConfigurationRequest(BaseModel):
    """Request model for configuration updates"""
    attachment_config: Dict[str, Any] = Field(..., description="New attachment configuration")
    validate_only: bool = Field(False, description="Whether to only validate without applying")


class ConfigurationResponse(BaseModel):
    """Response model for configuration operations"""
    success: bool = Field(..., description="Whether configuration operation was successful")
    message: str = Field(..., description="Status message")
    validation_errors: List[str] = Field(default_factory=list, description="Configuration validation errors")
    current_config: Optional[Dict[str, Any]] = Field(None, description="Current configuration")


class FileOperationRequest(BaseModel):
    """Request model for file operations"""
    operation: str = Field(..., description="Operation to perform: validate, check, analyze")
    file_path: str = Field(..., description="Path to file to operate on")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Additional operation parameters")


class FileOperationResult(BaseModel):
    """Response model for file operations"""
    success: bool = Field(..., description="Whether operation was successful")
    operation: str = Field(..., description="Operation that was performed")
    file_path: str = Field(..., description="Path to file that was operated on")
    results: Dict[str, Any] = Field(..., description="Operation results")
    errors: List[str] = Field(default_factory=list, description="Operation errors")
    warnings: List[str] = Field(default_factory=list, description="Operation warnings")


# API Response wrappers
class APIResponse(BaseModel):
    """Generic API response wrapper"""
    success: bool = Field(..., description="Whether the API call was successful")
    data: Optional[Any] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if success is False")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class PaginatedResponse(BaseModel):
    """Paginated response model"""
    items: List[Any] = Field(..., description="Items in current page")
    total_count: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number (1-based)")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")
