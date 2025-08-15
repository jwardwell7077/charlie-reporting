"""
Business Layer Exceptions
Custom exceptions for business logic layer
"""

from typing import Dict, List, Optional

class BusinessException(Exception):
    """
    Base exception for business logic errors
    Used when business rules are violated or business operations fail
    """
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self):
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class ValidationException(BusinessException):
    """
    Exception raised when data validation fails
    """
    
    def __init__(self, message: str, validation_errors: Optional[List] = None, field: Optional[str] = None):
        super().__init__(message)
        self.validation_errors = validation_errors or []
        self.field = field


class DataTransformationException(BusinessException):
    """
    Exception raised when data transformation operations fail
    """
    
    def __init__(self, message: str, source_data: Optional[str] = None, transformation_step: Optional[str] = None):
        super().__init__(message)
        self.source_data = source_data
        self.transformation_step = transformation_step


class ReportGenerationException(BusinessException):
    """
    Exception raised when report generation fails
    """
    
    def __init__(self, message: str, report_type: Optional[str] = None, sheet_name: Optional[str] = None):
        super().__init__(message)
        self.report_type = report_type
        self.sheet_name = sheet_name


class ConfigurationException(BusinessException):
    """
    Exception raised when configuration is invalid or missing
    """
    
    def __init__(self, message: str, config_key: Optional[str] = None, config_value: Optional[str] = None):
        super().__init__(message)
        self.config_key = config_key
        self.config_value = config_value


class FileProcessingException(BusinessException):
    """
    Exception raised when file processing operations fail
    """
    
    def __init__(self, message: str, file_path: Optional[str] = None, operation: Optional[str] = None):
        super().__init__(message)
        self.file_path = file_path
        self.operation = operation
