"""Structured logging infrastructure.

Provides JSON-based logging utilities for consistent observability.

Notes:
    The dynamic nature of structured logging context (arbitrary key/value pairs)
    makes it impractical to precisely type ``**kwargs`` for every logging helper.
    We intentionally allow dynamic keys; Ruff ANN401 is suppressed at module
    level for these flexible contexts.
"""

# ruff: noqa: ANN401

import json
import logging
import sys
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from ..business.interfaces import ILogger


class LogLevel(str, Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass(slots=True)
class LogEntry:
    """Structured log entry."""
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

    def __post_init__(self) -> None:
        """Ensure optional containers are initialized."""
        if self.metadata is None:
            self.metadata = {}


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""

    def __init__(self, service_name: str = "report-generator") -> None:
        """Create the formatter for a specific service."""
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        """Format log record as structured JSON."""
        # Base log entry
        log_entry = LogEntry(
            # Using UTC timezone for consistency
            timestamp=datetime.now(timezone.utc).isoformat(),  # noqa: UP017 (compatibility for older Python)
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
            log_entry.stack_trace = self.formatException(record.exc_info)
            log_entry.error_type = record.exc_info[0].__name__ if record.exc_info[0] else None

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
    """Structured logger providing a higher-level logging API."""

    def __init__(
        self,
        service_name: str = "report-generator",
        log_level: str = "INFO",
        log_file: str | Path | None = None,
        enable_console: bool = True,
    ) -> None:
        """Configure handlers and base metadata for the structured logger."""
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        self.logger.propagate = False

        # Clear existing handlers (avoid duplication on re-init)
        self.logger.handlers.clear()

        formatter = StructuredFormatter(service_name)

        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_path, encoding="utf-8")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        # Instance health/status metadata
        self.healthy = True
        self.start_time = datetime.now(timezone.utc)  # noqa: UP017

    def is_healthy(self) -> bool:
        """Return True if logger has handlers and no internal failure recorded."""
        return self.healthy and bool(self.logger.handlers)

    def log_debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message with structured data."""
        self.log(LogLevel.DEBUG, message, **kwargs)

    def log_info(self, message: str, **kwargs: Any) -> None:
        """Log info message with structured data."""
        self.log(LogLevel.INFO, message, **kwargs)

    def log_warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message with structured data."""
        self.log(LogLevel.WARNING, message, **kwargs)

    def log_error(self, message: str, **kwargs: Any) -> None:
        """Log error message with structured data."""
        self.log(LogLevel.ERROR, message, **kwargs)

    def log_critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message with structured data."""
        self.log(LogLevel.CRITICAL, message, **kwargs)

    # Convenience aliases (common logging interface style)
    def debug(self, message: str, **kwargs: Any) -> None:  # alias
        """Alias for :meth:`log_debug`."""
        self.log_debug(message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:  # alias
        """Alias for :meth:`log_info`."""
        self.log_info(message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:  # alias
        """Alias for :meth:`log_warning`."""
        self.log_warning(message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:  # alias
        """Alias for :meth:`log_error`."""
        self.log_error(message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:  # alias
        """Alias for :meth:`log_critical`."""
        self.log_critical(message, **kwargs)

    def log_request_start(self, request_id: str, method: str, path: str, **kwargs: Any) -> None:
        """Log REST request start."""
        self.log_info(
            f"Request started: {method} {path}",
            request_id=request_id,
            operation="request_start",
            http_method=method,
            http_path=path,
            **kwargs
        )

    def log_request_end(self, request_id: str, method: str, path: str,
                        status_code: int, duration_ms: float, **kwargs: Any) -> None:
        """Log REST request completion."""
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

    def log_processing_start(self, operation: str, request_id: str | None = None, **kwargs: Any) -> None:
        """Log processing operation start."""
        self.log_info(
            f"Processing started: {operation}",
            request_id=request_id,
            operation=f"{operation}start",
            **kwargs
        )

    def log_processing_end(self, operation: str, success: bool, duration_ms: float,
                           request_id: str | None = None, **kwargs: Any) -> None:
        """Log processing operation completion."""
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

    def log_business_event(self, event_type: str, details: dict[str, Any], **kwargs: Any) -> None:
        """Log business-specific events."""
        self.log_info(
            f"Business event: {event_type}",
            operation="business_event",
            event_type=event_type,
            event_details=details,
            **kwargs
        )

    def log_security_event(self, event_type: str, severity: str, details: dict[str, Any], **kwargs: Any) -> None:
        """Log security-related events."""
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

    def log_performance_metric(self, metric_name: str, value: float, unit: str, **kwargs: Any) -> None:
        """Log performance metrics."""
        self.log_info(
            f"Performance metric: {metric_name} = {value} {unit}",
            operation="performance_metric",
            metric_name=metric_name,
            metric_value=value,
            metric_unit=unit,
            **kwargs
        )

    def log_exception(self, exception: Exception, operation: str | None = None, **kwargs: Any) -> None:
        """Log exception with full context."""
        self.log_error(
            f"Exception in {operation or 'unknown operation'}: {str(exception)}",
            operation=operation,
            error_type=type(exception).__name__,
            error_message=str(exception),
            stack_trace=traceback.format_exc(),
            **kwargs
        )

    def create_child_logger(self, component: str) -> 'ComponentLogger':
        """Create a child logger for a specific component."""
        return ComponentLogger(self, component)

    def log(self, level: LogLevel, message: str, **kwargs: Any) -> None:
        """Internal logging method."""
        try:
            log_level_int = getattr(logging, level.value, logging.INFO)
            self.logger.log(log_level_int, message, extra=kwargs)
        except Exception as e:  # noqa: BLE001
            fallback_message = f"[LOGGING_ERROR] {message} | Original error: {e}"
            logging.getLogger().error(fallback_message)
            self.healthy = False

    def get_logger_stats(self) -> dict[str, Any]:
        """Get logger statistics."""
        return {
            "service_name": self.service_name,
            "healthy": self.healthy,
            "handlers_count": len(self.logger.handlers),
            "log_level": self.logger.level,
            "uptime_seconds": (datetime.now(timezone.utc) - self.start_time).total_seconds(),  # noqa: UP017
        }


class ComponentLogger:
    """Component-specific logger that injects component context automatically."""

    def __init__(self, parent_logger: StructuredLogger, component: str) -> None:
        """Create a component logger that enriches every entry with the component name."""
        self.parent = parent_logger
        self.component = component

    def log_debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message with component context."""
        self.parent.log_debug(message, component=self.component, **kwargs)

    def log_info(self, message: str, **kwargs: Any) -> None:
        """Log info message with component context."""
        self.parent.log_info(message, component=self.component, **kwargs)

    def log_warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message with component context."""
        self.parent.log_warning(message, component=self.component, **kwargs)

    def log_error(self, message: str, **kwargs: Any) -> None:
        """Log error message with component context."""
        self.parent.log_error(message, component=self.component, **kwargs)

    def log_critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message with component context."""
        self.parent.log_critical(message, component=self.component, **kwargs)

    # Convenience aliases aligning with logging module naming
    def debug(self, message: str, **kwargs: Any) -> None:  # alias
        """Alias for :meth:`log_debug` with component context."""
        self.log_debug(message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:  # alias
        """Alias for :meth:`log_info` with component context."""
        self.log_info(message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:  # alias
        """Alias for :meth:`log_warning` with component context."""
        self.log_warning(message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:  # alias
        """Alias for :meth:`log_error` with component context."""
        self.log_error(message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:  # alias
        """Alias for :meth:`log_critical` with component context."""
        self.log_critical(message, **kwargs)

    def log_exception(self, exception: Exception, operation: str | None = None, **kwargs: Any) -> None:
        """Log exception with component context."""
        self.parent.log_exception(
            exception,
            operation=operation,
            component=self.component,
            **kwargs
        )


# Global logger instance
global_logger: StructuredLogger | None = None


def get_logger(component: str | None = None) -> StructuredLogger | ComponentLogger:
    """Get the global structured logger or a component-specific logger."""
    global global_logger  # noqa: PLW0603

    if global_logger is None:
        global_logger = StructuredLogger()

    if component:
        return global_logger.create_child_logger(component)

    return global_logger


def initialize_logging(
    service_name: str = "report-generator",
    log_level: str = "INFO",
    log_file: str | Path | None = None,
    enable_console: bool = True,
) -> StructuredLogger:
    """Initialize global structured logging."""
    global global_logger  # noqa: PLW0603

    global_logger = StructuredLogger(
        service_name=service_name,
        log_level=log_level,
        log_file=log_file,
        enable_console=enable_console
    )

    return global_logger


class StructuredLoggerImpl(ILogger):
    """Concrete implementation of :class:`ILogger` using :class:`StructuredLogger`."""

    def __init__(self, component: str | None = None) -> None:
        """Create logger implementation optionally scoped to a component."""
        logger_obj = get_logger(component)
        # If component was provided we get a ComponentLogger with log_info etc.
        self._logger = logger_obj

    # ILogger contract
    def info(self, message: str, **kwargs: Any) -> None:  # type: ignore[override]
        """Log an informational message."""
        if isinstance(self._logger, StructuredLogger):
            self._logger.log_info(message, **kwargs)
        else:
            self._logger.log_info(message, **kwargs)  # ComponentLogger

    def error(self, message: str, **kwargs: Any) -> None:  # type: ignore[override]
        """Log an error message."""
        if isinstance(self._logger, StructuredLogger):
            self._logger.log_error(message, **kwargs)
        else:
            self._logger.log_error(message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:  # type: ignore[override]
        """Log a debug message."""
        if isinstance(self._logger, StructuredLogger):
            self._logger.log_debug(message, **kwargs)
        else:
            self._logger.log_debug(message, **kwargs)

    # Extra helpers (not in interface but useful)
    def log_exception(self, exception: Exception, operation: str | None = None, **kwargs: Any) -> None:
        """Log an exception with optional operation context."""
        if isinstance(self._logger, StructuredLogger):
            self._logger.log_exception(exception, operation=operation, **kwargs)
        else:
            self._logger.parent.log_exception(exception, operation=operation, **kwargs)  # type: ignore[attr-defined]

    def log_operation(self, operation: str, result: str, duration_ms: float | None = None, **kwargs: Any) -> None:
        """Log an operation summary with optional duration."""
        self.info(
            f"Operation {operation}: {result}",
            operation=operation,
            result=result,
            duration_ms=duration_ms,
            **kwargs,
        )
