"""
Centralized Logging System for Charlie Reporting Services
Provides structured logging with service-aware context
"""

import json
import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union
import threading
from enum import Enum

# Logging levels that map to Python logging
class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StructuredFormatter(logging.Formatter):
    """
    Structured JSON formatter for consistent log output
    """
    
    def __init__(self, service_name: str, include_extra: bool = True):
        super().__init__()
        self.service_name = service_name
        self.include_extra = include_extra
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": self.service_name,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info)
            }
        
        # Add extra fields from the log call
        if self.include_extra and hasattr(record, 'extra'):
            log_entry.update(record.extra)
        
        # Add any additional attributes that were set on the record
        reserved_attrs = {
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
            'module', 'exc_info', 'exc_text', 'stack_info', 'lineno', 'funcName',
            'created', 'msecs', 'relativeCreated', 'thread', 'threadName',
            'processName', 'process', 'getMessage', 'extra'
        }
        
        for key, value in record.__dict__.items():
            if key not in reserved_attrs and not key.startswith('_'):
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)


class ServiceLogger:
    """
    Service-aware logger that provides structured logging capabilities
    """
    
    def __init__(self, service_name: str, log_level: LogLevel = LogLevel.INFO):
        self.service_name = service_name
        self.log_level = log_level
        self._logger = logging.getLogger(service_name)
        self._logger.setLevel(getattr(logging, log_level.value))
        self._local = threading.local()
        
        # Remove any existing handlers to avoid duplicates
        self._logger.handlers.clear()
        
        # Setup structured formatter
        self._formatter = StructuredFormatter(service_name)
        
        # Setup console handler
        self._setup_console_handler()
    
    def _setup_console_handler(self):
        """Setup console logging handler"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self._formatter)
        self._logger.addHandler(console_handler)
    
    def add_file_handler(self, log_file_path: Union[str, Path], 
                        max_bytes: int = 10 * 1024 * 1024,  # 10MB
                        backup_count: int = 5):
        """Add rotating file handler"""
        log_file_path = Path(log_file_path)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setFormatter(self._formatter)
        self._logger.addHandler(file_handler)
    
    def with_context(self, **context) -> 'LoggerContext':
        """Create a logger context with additional fields"""
        return LoggerContext(self, context)
    
    def debug(self, message: str, **extra):
        """Log debug message"""
        self._logger.debug(message, extra=extra)
    
    def info(self, message: str, **extra):
        """Log info message"""
        self._logger.info(message, extra=extra)
    
    def warning(self, message: str, **extra):
        """Log warning message"""
        self._logger.warning(message, extra=extra)
    
    def error(self, message: str, **extra):
        """Log error message"""
        self._logger.error(message, extra=extra)
    
    def critical(self, message: str, **extra):
        """Log critical message"""
        self._logger.critical(message, extra=extra)
    
    def exception(self, message: str, **extra):
        """Log exception with traceback"""
        self._logger.exception(message, extra=extra)


class LoggerContext:
    """
    Context manager for logger that automatically includes context fields
    """
    
    def __init__(self, logger: ServiceLogger, context: Dict[str, Any]):
        self.logger = logger
        self.context = context
    
    def debug(self, message: str, **extra):
        """Log debug with context"""
        combined_extra = {**self.context, **extra}
        self.logger.debug(message, **combined_extra)
    
    def info(self, message: str, **extra):
        """Log info with context"""
        combined_extra = {**self.context, **extra}
        self.logger.info(message, **combined_extra)
    
    def warning(self, message: str, **extra):
        """Log warning with context"""
        combined_extra = {**self.context, **extra}
        self.logger.warning(message, **combined_extra)
    
    def error(self, message: str, **extra):
        """Log error with context"""
        combined_extra = {**self.context, **extra}
        self.logger.error(message, **combined_extra)
    
    def critical(self, message: str, **extra):
        """Log critical with context"""
        combined_extra = {**self.context, **extra}
        self.logger.critical(message, **combined_extra)
    
    def exception(self, message: str, **extra):
        """Log exception with context"""
        combined_extra = {**self.context, **extra}
        self.logger.exception(message, **combined_extra)


class RequestLogger:
    """
    HTTP request-specific logger with automatic request context
    """
    
    def __init__(self, logger: ServiceLogger):
        self.logger = logger
    
    def log_request_start(self, request_id: str, method: str, endpoint: str, **extra):
        """Log request start"""
        self.logger.info(
            "Request started",
            request_id=request_id,
            method=method,
            endpoint=endpoint,
            event_type="request_start",
            **extra
        )
    
    def log_request_end(self, request_id: str, method: str, endpoint: str, 
                       status_code: int, duration_ms: float, **extra):
        """Log request completion"""
        level = "info" if 200 <= status_code < 400 else "error"
        getattr(self.logger, level)(
            "Request completed",
            request_id=request_id,
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            duration_ms=duration_ms,
            event_type="request_end",
            **extra
        )
    
    def log_request_error(self, request_id: str, method: str, endpoint: str, 
                         error: Exception, **extra):
        """Log request error"""
        self.logger.error(
            "Request error",
            request_id=request_id,
            method=method,
            endpoint=endpoint,
            error_type=type(error).__name__,
            error_message=str(error),
            event_type="request_error",
            **extra
        )


class BusinessOperationLogger:
    """
    Business operation-specific logger for tracking operations
    """
    
    def __init__(self, logger: ServiceLogger):
        self.logger = logger
    
    def log_operation_start(self, operation_id: str, operation_type: str, **extra):
        """Log business operation start"""
        self.logger.info(
            "Operation started",
            operation_id=operation_id,
            operation_type=operation_type,
            event_type="operation_start",
            **extra
        )
    
    def log_operation_end(self, operation_id: str, operation_type: str, 
                         status: str, duration_ms: float, **extra):
        """Log business operation completion"""
        level = "info" if status == "success" else "error"
        getattr(self.logger, level)(
            "Operation completed",
            operation_id=operation_id,
            operation_type=operation_type,
            status=status,
            duration_ms=duration_ms,
            event_type="operation_end",
            **extra
        )
    
    def log_operation_progress(self, operation_id: str, operation_type: str, 
                              progress_percent: float, message: str, **extra):
        """Log operation progress"""
        self.logger.info(
            message,
            operation_id=operation_id,
            operation_type=operation_type,
            progress_percent=progress_percent,
            event_type="operation_progress",
            **extra
        )


def setup_service_logging(service_name: str, 
                         log_level: LogLevel = LogLevel.INFO,
                         log_file: Optional[Union[str, Path]] = None) -> ServiceLogger:
    """
    Setup logging for a service with consistent configuration
    
    Args:
        service_name: Name of the service
        log_level: Logging level
        log_file: Optional log file path
    
    Returns:
        Configured ServiceLogger instance
    """
    logger = ServiceLogger(service_name, log_level)
    
    if log_file:
        logger.add_file_handler(log_file)
    
    return logger


def create_operation_id() -> str:
    """Create a unique operation ID for tracking"""
    from uuid import uuid4
    return str(uuid4())


def create_request_id() -> str:
    """Create a unique request ID for tracking"""
    from uuid import uuid4
    return str(uuid4())


# Example usage patterns for documentation
"""
Example Usage:

# Basic service logging
logger = setup_service_logging("outlook-relay", LogLevel.INFO)
logger.info("Service starting", version="1.0.0")

# With context
with logger.with_context(user_id="12345", session_id="abc123") as ctx_logger:
    ctx_logger.info("Processing user request")

# Request logging
request_logger = RequestLogger(logger)
request_id = create_request_id()
request_logger.log_request_start(request_id, "GET", "/health")
# ... process request ...
request_logger.log_request_end(request_id, "GET", "/health", 200, 45.2)

# Business operation logging
op_logger = BusinessOperationLogger(logger)
op_id = create_operation_id()
op_logger.log_operation_start(op_id, "email_fetch")
# ... process operation ...
op_logger.log_operation_end(op_id, "email_fetch", "success", 1250.5)

# Error logging with exception
try:
    # some operation
    pass
except Exception as e:
    logger.exception("Operation failed", operation="data_processing")
"""
