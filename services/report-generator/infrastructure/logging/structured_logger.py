"""
Logging Implementation
Production implementation of ILogger interface with structured logging.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import json
from datetime import datetime

from business.interfaces import ILogger


class StructuredLoggerImpl(ILogger):
    """
    Production implementation of structured logging.

    Features:
    - JSON structured logging for production
    - Contextual logging with correlation IDs
    - Multiple output targets (console, file)
    - Performance - optimized logging
    """

    def __init__(self,
                 logger_name: str = "charlie - reporting",
                 log_level: str = "INFO",
                 log_file: Optional[Path] = None):
        self.logger_name = logger_name
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(getattr(logging, log_level.upper()))

        # Configure formatters
        self.setup_formatters()

        # Configure handlers
        self.setup_console_handler()
        if log_file:
            self.setup_file_handler(log_file)

        # Prevent duplicate logging
        self.logger.propagate = False

        self.context: Dict[str, Any] = {}

    def setup_formatters(self) -> None:
        """Setup JSON and console formatters."""
        # JSON formatter for structured logging
        self.json_formatter = JsonFormatter()

        # Console formatter for human readability
        console_format = (
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.console_formatter = logging.Formatter(console_format)

    def setup_console_handler(self) -> None:
        """Setup console logging handler."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.console_formatter)
        self.logger.addHandler(console_handler)

    def setup_file_handler(self, log_file: Path) -> None:
        """Setup file logging handler with JSON formatting."""
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(self.json_formatter)
        self.logger.addHandler(file_handler)

    async def log_info(self, message: str, **kwargs) -> None:
        """Log info level message with context."""
        self.log_with_context(logging.INFO, message, kwargs)

    async def log_error(self, message: str, error: Optional[Exception] = None,
                        **kwargs) -> None:
        """Log error level message with context and exception details."""
        if error:
            kwargs['error_type'] = type(error).__name__
            kwargs['error_message'] = str(error)

        self.log_with_context(logging.ERROR, message, kwargs)

    async def log_warning(self, message: str, **kwargs) -> None:
        """Log warning level message with context."""
        self.log_with_context(logging.WARNING, message, kwargs)

    async def log_debug(self, message: str, **kwargs) -> None:
        """Log debug level message with context."""
        self.log_with_context(logging.DEBUG, message, kwargs)

    def log_with_context(self, level: int, message: str,
                         extra_data: Dict[str, Any]) -> None:
        """Log message with contextual information."""
        # Combine context with extra data
        log_data = {**self.context, **extra_data}

        # Create extra dict for logger
        extra = {
            'context_data': log_data,
            'timestamp': datetime.utcnow().isoformat(),
            'logger_name': self.logger_name
        }

        self.logger.log(level, message, extra=extra)

    def add_context(self, **kwargs) -> None:
        """Add persistent context to all log messages."""
        self.context.update(kwargs)

    def clear_context(self) -> None:
        """Clear all persistent context."""
        self.context.clear()

    def set_correlation_id(self, correlation_id: str) -> None:
        """Set correlation ID for request tracking."""
        self.context['correlation_id'] = correlation_id


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.utcfromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Add context data if available
        if hasattr(record, 'context_data'):
            log_data['context'] = record.context_data

        # Add exception info if available
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data, default=str)
