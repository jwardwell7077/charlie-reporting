"""Business layer exceptions for report generator service."""

from __future__ import annotations

from typing import Any


class BusinessException(Exception):
    """Base exception for business logic errors
    Used when business rules are violated or business operations fail
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self):
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class ValidationException(BusinessException):
    """Raised when data validation fails."""

    def __init__(self, message: str, validation_errors: list[str] | None = None, field: str | None = None):
        super().__init__(message)
        self.validation_errors = validation_errors or []
        self.field = field


class DataTransformationException(BusinessException):
    """Raised when data transformation operations fail."""

    def __init__(self, message: str, source_data: str | None = None, transformation_step: str | None = None):
        super().__init__(message)
        self.source_data = source_data
        self.transformation_step = transformation_step


class ReportGenerationException(BusinessException):
    """Raised when report generation fails."""

    def __init__(self, message: str, report_type: str | None = None, sheet_name: str | None = None):
        super().__init__(message)
        self.report_type = report_type
        self.sheet_name = sheet_name


class ConfigurationException(BusinessException):
    """Raised when configuration is invalid or missing."""

    def __init__(self, message: str, config_key: str | None = None, config_value: str | None = None):
        super().__init__(message)
        self.config_key = config_key
        self.config_value = config_value


class FileProcessingException(BusinessException):
    """Raised when file processing operations fail."""

    def __init__(self, message: str, file_path: str | None = None, operation: str | None = None):
        super().__init__(message)
        self.file_path = file_path
        self.operation = operation


class DirectoryException(BusinessException):
    """Raised when directory operations fail (scan/validate)."""

    def __init__(self, message: str, directory_path: str | None = None):
        super().__init__(message)
        self.directory_path = directory_path


class FileException(BusinessException):
    """Raised when low-level file operations fail."""

    def __init__(self, message: str, file_path: str | None = None):
        super().__init__(message)
        self.file_path = file_path
