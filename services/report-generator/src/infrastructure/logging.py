"""Structured Logging Infrastructure
JSON - based logging for better observability and log analysis
"""

import json
import logging
import sys
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from ..business.interfaces import ILogger


class LogLevel(str, Enum):
    """Log level enumeration"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass


class LogEntry:
    """Structured log entry"""
    timestamp: str
    level: str
    message: str
    service: str = "report - generator"
    component: str | None = None
    request_id: str | None = None
    user_id: str | None = None
    operation: str | None = None
    duration_ms: float | None = None
    error_type: str | None = None
    stack_trace: str | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""

    def __init__(self, service_name: str = "report - generator"):
        super().__init__()
        self.servicename = service_name

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON"""
        # Base log entry
        logentry = LogEntry(
            timestamp=datetime.utcnow().isoformat() + "Z",
            level=record.levelname,
            message=record.getMessage(),
            service=self.service_name,
            component=getattr(record, 'component', record.name)
        )

        # Add optional fields if present
        for field in ['request_id', 'user_id', 'operation', 'duration_ms', 'error_type']:
            if hasattr(record, field):
                setattr(log_entry, field, getattr(record, field))

        # Add stack trace for errors
        if record.exc_info:
            log_entry.stacktrace = self.formatException(record.exc_info)
            log_entry.errortype = record.exc_info[0].__name__ if record.exc_info[0] else None

        # Add metadata from extra fields
        metadata = {}
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'file_name', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'stack_info', 'exc_info', 'exc_text',
                          'component', 'request_id', 'user_id', 'operation', 'duration_ms', 'error_type']:
                # Convert non - serializable objects to strings
                try:
                    json.dumps(value)
                    metadata[key] = value
                except (TypeError, ValueError):
                    metadata[key] = str(value)

        if metadata:
            log_entry.metadata = metadata

        # Convert to dict and serialize to JSON
        try:
            return json.dumps(asdict(log_entry), ensure_ascii=False, separators=(',', ':'))
        except (TypeError, ValueError) as e:
            # Fallback to simple format if JSON serialization fails
            return f"{log_entry.timestamp} {log_entry.level} {log_entry.message} [JSON_ERROR: {str(e)}]"


class StructuredLogger:
    """Infrastructure service for structured logging
    Provides consistent logging interface across the application
    """

    def __init__(self,
                 service_name: str = "report - generator",
                 log_level: str = "INFO",
                 log_file: str | Path | None = None,
                 enable_console: bool = True):

        self.servicename = service_name
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(getattr(logging, log_level.upper()))

        # Clear existing handlers
        self.logger.handlers.clear()

        # Create formatter
        formatter = StructuredFormatter(service_name)

        # Console handler
        if enable_console:
            consolehandler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        # File handler if specified
        if log_file:
            logpath = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            filehandler = logging.FileHandler(log_path)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        self.healthy = True
        self.start_time = datetime.utcnow()

    def is_healthy(self) -> bool:
        """Check if logger is healthy"""
        return self.healthy and len(self.logger.handlers) > 0

    def log_debug(self, message: str, **kwargs):
        """Log debug message with structured data"""
        self.log(LogLevel.DEBUG, message, **kwargs)

    def log_info(self, message: str, **kwargs):
        """Log info message with structured data"""
        self.log(LogLevel.INFO, message, **kwargs)

    def log_warning(self, message: str, **kwargs):
        """Log warning message with structured data"""
        self.log(LogLevel.WARNING, message, **kwargs)

    def log_error(self, message: str, **kwargs):
        """Log error message with structured data"""
        self.log(LogLevel.ERROR, message, **kwargs)

    def log_critical(self, message: str, **kwargs):
        """Log critical message with structured data"""
        self.log(LogLevel.CRITICAL, message, **kwargs)

    def log_request_start(self, request_id: str, method: str, path: str, **kwargs):
        """Log request start"""
        self.log_info(
            f"Request started: {method} {path}",
            request_id=request_id,
            operation="request_start",
            http_method=method,
            http_path=path,
            **kwargs
        )

    def log_request_end(self, request_id: str, method: str, path: str,
                       status_code: int, duration_ms: float, **kwargs):
        """Log request completion"""
        self.log_info(
            f"Request completed: {method} {path} [{status_code}]",
            request_id=request_id,
            operation="request_end",
            http_method=method,
            http_path=path,
            http_status_code=status_code,
            duration_ms=duration_ms,
            **kwargs
        )

    def log_processing_start(self, operation: str, request_id: str | None = None, **kwargs):
        """Log processing operation start"""
        self.log_info(
            f"Processing started: {operation}",
            request_id=request_id,
            operation=f"{operation}start",
            **kwargs
        )

    def log_processing_end(self, operation: str, success: bool, duration_ms: float,
                          request_id: str | None = None, **kwargs):
        """Log processing operation completion"""
        level = LogLevel.INFO if success else LogLevel.ERROR
        message = f"Processing {'completed' if success else 'failed'}: {operation}"

        self.log(
            level,
            message,
            request_id=request_id,
            operation=f"{operation}end",
            duration_ms=duration_ms,
            success=success,
            **kwargs
        )

    def log_business_event(self, event_type: str, details: dict[str, Any], **kwargs):
        """Log business - specific events"""
        self.log_info(
            f"Business event: {event_type}",
            operation="business_event",
            event_type=event_type,
            event_details=details,
            **kwargs
        )

    def log_security_event(self, event_type: str, severity: str, details: dict[str, Any], **kwargs):
        """Log security - related events"""
        level = LogLevel.WARNING if severity.lower() in ['medium', 'high'] else LogLevel.INFO

        self.log(
            level,
            f"Security event: {event_type}",
            operation="security_event",
            event_type=event_type,
            severity=severity,
            security_details=details,
            **kwargs
        )

    def log_performance_metric(self, metric_name: str, value: float, unit: str, **kwargs):
        """Log performance metrics"""
        self.log_info(
            f"Performance metric: {metric_name} = {value} {unit}",
            operation="performance_metric",
            metric_name=metric_name,
            metric_value=value,
            metric_unit=unit,
            **kwargs
        )

    def log_exception(self, exception: Exception, operation: str | None = None, **kwargs):
        """Log exception with full context"""
        self.log_error(
            f"Exception in {operation or 'unknown operation'}: {str(exception)}",
            operation=operation,
            error_type=type(exception).__name__,
            error_message=str(exception),
            stack_trace=traceback.format_exc(),
            **kwargs
        )

    def create_child_logger(self, component: str) -> 'ComponentLogger':
        """Create a child logger for a specific component"""
        return ComponentLogger(self, component)

    def log(self, level: LogLevel, message: str, **kwargs):
        """Internal logging method"""
        try:
            # Convert LogLevel enum to logging level
            loglevel = getattr(logging, level.value)

            # Create log record with extra data
            self.logger.log(log_level, message, extra=kwargs)

        except Exception as e:
            # Fallback logging if structured logging fails
            fallbackmessage = f"[LOGGING_ERROR] {message} | Original error: {str(e)}"
            logging.getLogger().error(fallback_message)
            self.healthy = False

    def get_logger_stats(self) -> dict[str, Any]:
        """Get logger statistics"""
        return {
            "service_name": self.service_name,
            "healthy": self.healthy,
            "handlers_count": len(self.logger.handlers),
            "log_level": self.logger.level,
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds()
        }


class ComponentLogger:
    """Component - specific logger that automatically adds component context
    """

    def __init__(self, parent_logger: StructuredLogger, component: str):
        self.parent = parent_logger
        self.component = component

    def log_debug(self, message: str, **kwargs):
        """Log debug message with component context"""
        self.parent.log_debug(message, component=self.component, **kwargs)

    def log_info(self, message: str, **kwargs):
        """Log info message with component context"""
        self.parent.log_info(message, component=self.component, **kwargs)

    def log_warning(self, message: str, **kwargs):
        """Log warning message with component context"""
        self.parent.log_warning(message, component=self.component, **kwargs)

    def log_error(self, message: str, **kwargs):
        """Log error message with component context"""
        self.parent.log_error(message, component=self.component, **kwargs)

    def log_critical(self, message: str, **kwargs):
        """Log critical message with component context"""
        self.parent.log_critical(message, component=self.component, **kwargs)

    def log_exception(self, exception: Exception, operation: str | None = None, **kwargs):
        """Log exception with component context"""
        self.parent.log_exception(
            exception,
            operation=operation,
            component=self.component,
            **kwargs
        )


# Global logger instance
global_logger: StructuredLogger | None = None


def get_logger(component: str | None = None) -> StructuredLogger | ComponentLogger:
    """Get the global structured logger or a component - specific logger"""
    global global_logger

    if global_logger is None:
        global_logger = StructuredLogger()

    if component:
        return global_logger.create_child_logger(component)

    return global_logger


def initialize_logging(service_name: str = "report - generator",
                      log_level: str = "INFO",
                      log_file: str | Path | None = None,
                      enable_console: bool = True) -> StructuredLogger:
    """Initialize global structured logging"""
    global global_logger

    global_logger = StructuredLogger(
        service_name=service_name,
        log_level=log_level,
        log_file=log_file,
        enable_console=enable_console
    )

    return global_logger


class StructuredLoggerImpl(ILogger):
    """Implementation of ILogger interface
    Adapter for the existing StructuredLogger
    """

    def __init__(self, component: str | None = None):
        self.logger = get_logger(component)

    async def info(self, message: str, **kwargs) -> None:
        """Log info message"""
        self.logger.info(message, **kwargs)

    async def warning(self, message: str, **kwargs) -> None:
        """Log warning message"""
        self.logger.warning(message, **kwargs)

    async def error(self, message: str, **kwargs) -> None:
        """Log error message"""
        self.logger.error(message, **kwargs)

    async def debug(self, message: str, **kwargs) -> None:
        """Log debug message"""
        self.logger.debug(message, **kwargs)

    async def log_operation(self, operation: str, result: str, duration_ms: float = None, **kwargs) -> None:
        """Log operation with result and timing"""
        metadata = {
            "operation": operation,
            "result": result,
            "duration_ms": duration_ms,
            **kwargs
        }
        self.logger.info(f"Operation {operation}: {result}", **metadata)

    async def log_exception(self, exception: Exception, operation: str = None, **kwargs) -> None:
        """Log exception with context"""
        self.logger.log_exception(exception, operation=operation, **kwargs)
