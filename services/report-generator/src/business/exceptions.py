"""Business Layer Exceptions
Custom exceptions for business logic layer
"""



class BusinessException(Exception):
    """Base exception for business logic errors
    Used when business rules are violated or business operations fail
    """

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self):
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class ValidationException(BusinessException):
    """Exception raised when data validation fails
    """

    def __init__(self, message: str, validation_errors: List | None = None, field: str | None = None):
        super().__init__(message)
        self.validationerrors = validation_errors or []
        self.field = field


class DataTransformationException(BusinessException):
    """Exception raised when data transformation operations fail
    """

    def __init__(self, message: str, source_data: str | None = None, transformation_step: str | None = None):
        super().__init__(message)
        self.sourcedata = source_data
        self.transformationstep = transformation_step


class ReportGenerationException(BusinessException):
    """Exception raised when report generation fails
    """

    def __init__(self, message: str, report_type: str | None = None, sheet_name: str | None = None):
        super().__init__(message)
        self.reporttype = report_type
        self.sheetname = sheet_name


class ConfigurationException(BusinessException):
    """Exception raised when configuration is invalid or missing
    """

    def __init__(self, message: str, config_key: str | None = None, config_value: str | None = None):
        super().__init__(message)
        self.configkey = config_key
        self.config_value = config_value


class FileProcessingException(BusinessException):
    """Exception raised when file processing operations fail
    """

    def __init__(self, message: str, file_path: str | None = None, operation: str | None = None):
        super().__init__(message)
        self.file_path = file_path
        self.operation = operation
