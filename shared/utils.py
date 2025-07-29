"""
Shared Utilities for Charlie Reporting Microservices
Common helper functions and utilities used across all services
"""

import asyncio
import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, Generic
from functools import wraps
import time
import re


# Type variable for generic functions
T = TypeVar('T')


class DateTimeUtils:
    """Utilities for date and time handling"""
    
    @staticmethod
    def utc_now() -> datetime:
        """Get current UTC datetime"""
        return datetime.now(timezone.utc)
    
    @staticmethod
    def to_iso_string(dt: datetime) -> str:
        """Convert datetime to ISO string"""
        return dt.isoformat()
    
    @staticmethod
    def from_iso_string(iso_string: str) -> datetime:
        """Parse datetime from ISO string"""
        return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in seconds to human readable format"""
        if seconds < 1:
            return f"{seconds * 1000:.1f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"


class IDGenerator:
    """Utilities for generating unique identifiers"""
    
    @staticmethod
    def generate_uuid() -> str:
        """Generate a UUID4 string"""
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_short_id(length: int = 8) -> str:
        """Generate a short alphanumeric ID"""
        return str(uuid.uuid4()).replace('-', '')[:length]
    
    @staticmethod
    def generate_request_id() -> str:
        """Generate a request ID for tracking"""
        return f"req_{IDGenerator.generate_short_id(12)}"
    
    @staticmethod
    def generate_operation_id() -> str:
        """Generate an operation ID for tracking"""
        return f"op_{IDGenerator.generate_short_id(12)}"


class FileUtils:
    """Utilities for file operations"""
    
    @staticmethod
    def ensure_directory(path: Union[str, Path]) -> Path:
        """Ensure directory exists, create if it doesn't"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def get_file_hash(file_path: Union[str, Path], algorithm: str = "sha256") -> str:
        """Get hash of file contents"""
        file_path = Path(file_path)
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    @staticmethod
    def get_file_size_mb(file_path: Union[str, Path]) -> float:
        """Get file size in megabytes"""
        file_path = Path(file_path)
        size_bytes = file_path.stat().st_size
        return size_bytes / (1024 * 1024)
    
    @staticmethod
    def is_file_older_than(file_path: Union[str, Path], hours: float) -> bool:
        """Check if file is older than specified hours"""
        file_path = Path(file_path)
        if not file_path.exists():
            return True
        
        file_time = datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc)
        current_time = DateTimeUtils.utc_now()
        age_hours = (current_time - file_time).total_seconds() / 3600
        
        return age_hours > hours
    
    @staticmethod
    def clean_filename(filename: str) -> str:
        """Clean filename for safe file system usage"""
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remove control characters
        filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        return filename.strip()


class ValidationUtils:
    """Utilities for data validation"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Basic email validation"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Basic URL validation"""
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return re.match(pattern, url) is not None
    
    @staticmethod
    def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
        """Sanitize string for safe processing"""
        if not isinstance(text, str):
            text = str(text)
        
        # Remove control characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        
        # Trim whitespace
        text = text.strip()
        
        # Limit length
        if max_length and len(text) > max_length:
            text = text[:max_length]
        
        return text


class RetryUtils:
    """Utilities for retry logic"""
    
    @staticmethod
    def calculate_backoff_delay(attempt: int, base_delay: float = 1.0, 
                               max_delay: float = 60.0, exponential: bool = True) -> float:
        """Calculate backoff delay for retry attempts"""
        if exponential:
            delay = base_delay * (2 ** (attempt - 1))
        else:
            delay = base_delay * attempt
        
        return min(delay, max_delay)
    
    @staticmethod
    def should_retry_exception(exception: Exception, 
                              retryable_exceptions: List[type] = None) -> bool:
        """Determine if exception should trigger a retry"""
        if retryable_exceptions is None:
            retryable_exceptions = [ConnectionError, TimeoutError]
        
        return any(isinstance(exception, exc_type) for exc_type in retryable_exceptions)


def retry_async(max_attempts: int = 3, base_delay: float = 1.0, 
               exponential_backoff: bool = True,
               retryable_exceptions: List[type] = None):
    """
    Decorator for async functions with retry logic
    
    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
        exponential_backoff: Whether to use exponential backoff
        retryable_exceptions: List of exceptions that should trigger retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        raise
                    
                    if not RetryUtils.should_retry_exception(e, retryable_exceptions):
                        raise
                    
                    delay = RetryUtils.calculate_backoff_delay(
                        attempt, base_delay, exponential=exponential_backoff
                    )
                    await asyncio.sleep(delay)
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


def time_async_operation(operation_name: str = None):
    """
    Decorator to time async operations and log the duration
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            operation = operation_name or func.__name__
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                # In a real implementation, this would use the logging system
                print(f"Operation '{operation}' completed in {DateTimeUtils.format_duration(duration)}")
                return result
            except Exception as e:
                duration = time.time() - start_time
                print(f"Operation '{operation}' failed after {DateTimeUtils.format_duration(duration)}: {e}")
                raise
        
        return wrapper
    return decorator


class ConfigurationError(Exception):
    """Exception for configuration-related errors"""
    pass


class ValidationError(Exception):
    """Exception for validation errors"""
    pass


class BusinessLogicError(Exception):
    """Exception for business logic errors"""
    pass


class ExternalServiceError(Exception):
    """Exception for external service communication errors"""
    pass


class DataUtils:
    """Utilities for data manipulation"""
    
    @staticmethod
    def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = DataUtils.deep_merge_dicts(result[key], value)
            else:
                result[key] = value
        
        return result
    
    @staticmethod
    def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """Flatten a nested dictionary"""
        items = []
        
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(DataUtils.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        
        return dict(items)
    
    @staticmethod
    def filter_dict_by_keys(d: Dict[str, Any], keys: List[str], 
                           include: bool = True) -> Dict[str, Any]:
        """Filter dictionary by including or excluding specific keys"""
        if include:
            return {k: v for k, v in d.items() if k in keys}
        else:
            return {k: v for k, v in d.items() if k not in keys}
    
    @staticmethod
    def remove_none_values(d: Dict[str, Any], recursive: bool = True) -> Dict[str, Any]:
        """Remove None values from dictionary"""
        result = {}
        
        for k, v in d.items():
            if v is None:
                continue
            elif recursive and isinstance(v, dict):
                nested = DataUtils.remove_none_values(v, recursive)
                if nested:  # Only add if the nested dict is not empty
                    result[k] = nested
            else:
                result[k] = v
        
        return result


class AsyncContextManager:
    """
    Generic async context manager for resource management
    """
    
    def __init__(self, setup_func: Callable = None, cleanup_func: Callable = None):
        self.setup_func = setup_func
        self.cleanup_func = cleanup_func
        self.resource = None
    
    async def __aenter__(self):
        if self.setup_func:
            if asyncio.iscoroutinefunction(self.setup_func):
                self.resource = await self.setup_func()
            else:
                self.resource = self.setup_func()
        return self.resource
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.cleanup_func and self.resource:
            if asyncio.iscoroutinefunction(self.cleanup_func):
                await self.cleanup_func(self.resource)
            else:
                self.cleanup_func(self.resource)


class CircuitBreaker:
    """
    Simple circuit breaker pattern for external service calls
    """
    
    def __init__(self, failure_threshold: int = 5, timeout_seconds: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def can_execute(self) -> bool:
        """Check if operation can be executed"""
        if self.state == "closed":
            return True
        elif self.state == "open":
            if self.last_failure_time and \
               time.time() - self.last_failure_time > self.timeout_seconds:
                self.state = "half-open"
                return True
            return False
        else:  # half-open
            return True
    
    def record_success(self):
        """Record successful operation"""
        self.failure_count = 0
        self.state = "closed"
    
    def record_failure(self):
        """Record failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"


# Environment detection utilities
def is_development() -> bool:
    """Check if running in development environment"""
    return os.getenv("ENVIRONMENT", "development").lower() in ["dev", "development"]


def is_production() -> bool:
    """Check if running in production environment"""
    return os.getenv("ENVIRONMENT", "development").lower() in ["prod", "production"]


def get_environment() -> str:
    """Get current environment name"""
    return os.getenv("ENVIRONMENT", "development").lower()


# Common constants
class Constants:
    """Common constants used across services"""
    
    # HTTP Status Codes
    HTTP_OK = 200
    HTTP_CREATED = 201
    HTTP_BAD_REQUEST = 400
    HTTP_UNAUTHORIZED = 401
    HTTP_FORBIDDEN = 403
    HTTP_NOT_FOUND = 404
    HTTP_CONFLICT = 409
    HTTP_INTERNAL_ERROR = 500
    HTTP_SERVICE_UNAVAILABLE = 503
    
    # Common headers
    HEADER_REQUEST_ID = "X-Request-ID"
    HEADER_CORRELATION_ID = "X-Correlation-ID"
    HEADER_USER_AGENT = "User-Agent"
    HEADER_CONTENT_TYPE = "Content-Type"
    
    # Content types
    CONTENT_TYPE_JSON = "application/json"
    CONTENT_TYPE_TEXT = "text/plain"
    CONTENT_TYPE_HTML = "text/html"
    
    # Date formats
    ISO_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    SIMPLE_DATE_FORMAT = "%Y-%m-%d"
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
