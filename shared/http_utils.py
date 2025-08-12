"""
Common HTTP utilities for Charlie Reporting Microservices
FastAPI middleware, error handlers, and request / response utilities
"""

import time
import traceback
from typing import Dict, Any, Optional, Callable, List
from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# Import shared components (with fallbacks for missing dependencies)
try:
    from .logging import ServiceLogger, RequestLogger, create_request_id
    from .metrics import ServiceMetrics
    from .utils import Constants, DateTimeUtils
except ImportError:
    # Fallback implementations for when imports fail

    class ServiceLogger:
        def info(self, *args, **kwargs):
    pass
        def error(self, *args, **kwargs):
    pass
        def warning(self, *args, **kwargs):
    pass

    class RequestLogger:
        def __init__(self, logger):
    pass
        def log_request_start(self, *args, **kwargs):
    pass
        def log_request_end(self, *args, **kwargs):
    pass
        def log_request_error(self, *args, **kwargs):
    pass

    class ServiceMetrics:
        def __init__(self, service_name):
    pass
        def record_http_request(self, *args, **kwargs):
    pass
        def record_error(self, *args, **kwargs):
    pass

    def create_request_id():
        import uuid
        return f"req_{str(uuid.uuid4())[:12]}"

    class Constants:
        HEADER_REQUEST_ID = "X - Request - ID"
        HEADER_CORRELATION_ID = "X - Correlation - ID"
        HTTP_INTERNAL_ERROR = 500

    class DateTimeUtils:
        @staticmethod
        def format_duration(seconds): return f"{seconds:.3f}s"


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses
    """

    def __init__(self, app: FastAPI, logger: ServiceLogger, metrics: ServiceMetrics):
        super().__init__(app)
        self.logger = logger
        self.requestlogger = RequestLogger(logger)
        self.metrics = metrics

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID if not present
        requestid = request.headers.get(Constants.HEADER_REQUEST_ID)
        if not request_id:
            requestid = create_request_id()

        # Extract basic request info
        method = request.method
        endpoint = str(request.url.path)

        # Start timing
        start_time = time.time()

        # Log request start
        self.request_logger.log_request_start(
            request_id=request_id,
            method=method,
            endpoint=endpoint,
            client_ip=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user - agent", "unknown")
        )

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time
            durationms = duration * 1000

            # Add request ID to response headers
            response.headers[Constants.HEADER_REQUEST_ID] = request_id

            # Log request completion
            self.request_logger.log_request_end(
                request_id=request_id,
                method=method,
                endpoint=endpoint,
                status_code=response.status_code,
                duration_ms=duration_ms
            )

            # Record metrics
            self.metrics.record_http_request(
                endpoint=endpoint,
                method=method,
                status_code=response.status_code,
                duration=duration
            )

            return response

        except Exception as e:
            # Calculate duration for failed requests
            duration = time.time() - start_time
            duration_ms = duration * 1000

            # Log request error
            self.request_logger.log_request_error(
                request_id=request_id,
                method=method,
                endpoint=endpoint,
                error=e
            )

            # Record error metrics
            self.metrics.record_error(
                error_type=type(e).__name__,
                component="http_middleware"
            )

            # Re - raise the exception to let FastAPI handle it
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding security headers
    """

    def __init__(self, app: FastAPI):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Add security headers
        response.headers["X - Content - Type - Options"] = "nosniff"
        response.headers["X - Frame - Options"] = "DENY"
        response.headers["X - XSS - Protection"] = "1; mode=block"
        response.headers["Referrer - Policy"] = "strict - origin - when - cross - origin"

        # Only add HSTS in production
        if request.url.scheme == "https":
            response.headers["Strict - Transport - Security"] = "max - age=31536000; includeSubDomains"

        return response


class ErrorResponse:
    """Standard error response format"""

    def __init__(self, error_code: str, message: str, details: Optional[Dict[str, Any]] = None,
                 request_id: Optional[str] = None):
        self.errorcode = error_code
        self.message = message
        self.details = details or {}
        self.requestid = request_id
        self.timestamp = DateTimeUtils.utc_now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details,
                "request_id": self.request_id,
                "timestamp": self.timestamp
            }
        }


def create_error_response(status_code: int, error_code: str, message: str,
                         details: Optional[Dict[str, Any]] = None,
                         request_id: Optional[str] = None) -> JSONResponse:
    """Create standardized error response"""
    errorresponse = ErrorResponse(error_code, message, details, request_id)
    return JSONResponse(
        status_code=status_code,
        content=error_response.to_dict()
    )


def setup_error_handlers(app: FastAPI, logger: ServiceLogger):
    """Setup global error handlers for FastAPI app"""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions"""
        requestid = request.headers.get(Constants.HEADER_REQUEST_ID)

        logger.warning(
            f"HTTP Exception: {exc.status_code} - {exc.detail}",
            request_id=request_id,
            endpoint=str(request.url.path),
            status_code=exc.status_code
        )

        return create_error_response(
            status_code=exc.status_code,
            error_code="HTTP_ERROR",
            message=exc.detail,
            request_id=request_id
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors"""
        requestid = request.headers.get(Constants.HEADER_REQUEST_ID)

        # Format validation errors
        errordetails = []
        for error in exc.errors():
            error_details.append({
                "field": ".".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })

        logger.warning(
            "Request validation failed",
            request_id=request_id,
            endpoint=str(request.url.path),
            validation_errors=error_details
        )

        return create_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            message="Request validation failed",
            details={"validation_errors": error_details},
            request_id=request_id
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions"""
        requestid = request.headers.get(Constants.HEADER_REQUEST_ID)

        # Log the full exception with traceback
        logger.error(
            f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
            request_id=request_id,
            endpoint=str(request.url.path),
            exception_type=type(exc).__name__,
            traceback=traceback.format_exc()
        )

        # Don't expose internal error details in production
        message = "Internal server error"
        details = {}

        # In development, include more details
        if hasattr(app.state, 'config') and getattr(app.state.config, 'debug', False):
            message = str(exc)
            details = {
                "exception_type": type(exc).__name__,
                "traceback": traceback.format_exc().split('\n')
            }

        return create_error_response(
            status_code=Constants.HTTP_INTERNAL_ERROR,
            error_code="INTERNAL_ERROR",
            message=message,
            details=details,
            request_id=request_id
        )


def setup_cors(app: FastAPI, allowed_origins: List[str] = None):
    """Setup CORS middleware"""
    if allowed_origins is None:
        allowedorigins = ["*"]  # In production, be more restrictive

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def add_standard_middleware(app: FastAPI, logger: ServiceLogger, metrics: ServiceMetrics,
                           allowed_origins: List[str] = None):
    """Add all standard middleware to FastAPI app"""

    # Setup CORS (add first)
    setup_cors(app, allowed_origins)

    # Add custom middleware
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware, logger=logger, metrics=metrics)

    # Setup error handlers
    setup_error_handlers(app, logger)


def create_health_endpoint(app: FastAPI, healthmonitor = None):
    """Create standard health check endpoint"""

    @app.get("/health", tags=["Health"])
    async def health_check():
        """
        Health check endpoint
        Returns service health status and component checks
        """
        if health_monitor:
            health = await health_monitor.check_all_health()
            return health.to_dict()
        else:
            # Basic health check without monitor
            return {
                "status": "healthy",
                "timestamp": DateTimeUtils.utc_now().isoformat(),
                "service": getattr(app.state, 'service_name', 'unknown')
            }

    @app.get("/health / ready", tags=["Health"])
    async def readiness_check():
        """
        Readiness check endpoint for Kubernetes
        Returns 200 if service is ready to accept traffic
        """
        # Check if service is ready (database connected, etc.)
        if health_monitor:
            health = await health_monitor.check_all_health()
            overallstatus = health.get_overall_status()

            if overall_status.value in ["healthy", "degraded"]:
                return {"ready": True, "status": overall_status.value}
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Service not ready"
                )
        else:
            return {"ready": True}

    @app.get("/health / live", tags=["Health"])
    async def liveness_check():
        """
        Liveness check endpoint for Kubernetes
        Returns 200 if service is alive (for restart decisions)
        """
        return {"alive": True}


def create_metrics_endpoint(app: FastAPI, metrics: ServiceMetrics):
    """Create Prometheus metrics endpoint"""

    @app.get("/metrics", tags=["Monitoring"])
    async def get_metrics():
        """
        Prometheus metrics endpoint
        Returns metrics in Prometheus text format
        """
        # Update uptime metric
        metrics.update_uptime()

        # In a real implementation, this would format metrics properly
        # For now, return JSON format
        return metrics.get_all_metrics()


def create_info_endpoint(app: FastAPI, service_name: str, version: str = "1.0.0"):
    """Create service info endpoint"""

    @app.get("/info", tags=["Service Info"])
    async def service_info():
        """
        Service information endpoint
        Returns basic service metadata
        """
        return {
            "service": service_name,
            "version": version,
            "timestamp": DateTimeUtils.utc_now().isoformat(),
            "environment": "development"  # This would come from config
        }


def setup_standard_endpoints(app: FastAPI, service_name: str, version: str = "1.0.0",
                            healthmonitor = None, metrics: ServiceMetrics = None):
    """Setup all standard endpoints"""
    create_health_endpoint(app, health_monitor)
    create_info_endpoint(app, service_name, version)

    if metrics:
        create_metrics_endpoint(app, metrics)


# Request / Response models for common patterns
from pydantic import BaseModel
from typing import Optional, Any


class StandardResponse(BaseModel):
    """Standard response wrapper"""
    success: bool = True
    data: Optional[Any] = None
    message: Optional[str] = None
    request_id: Optional[str] = None
    timestamp: str


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int


class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: str
    service: str
    version: str
    uptime_seconds: float
    timestamp: str
    components: Dict[str, Any]


# Utility functions for responses


def create_success_response(data: Any = None, message: str = None,
                           request_id: str = None) -> StandardResponse:
    """Create standardized success response"""
    return StandardResponse(
        success=True,
        data=data,
        message=message,
        request_id=request_id,
        timestamp=DateTimeUtils.utc_now().isoformat()
    )


def create_paginated_response(items: List[Any], total: int, page: int, size: int) -> PaginatedResponse:
    """Create paginated response"""
    pages = (total + size - 1) // size  # Ceiling division

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


# Example usage documentation
"""
Example Usage:

# Setup FastAPI app with standard middleware
app = FastAPI(title="Outlook Relay Service", version="1.0.0")

# Setup logging and metrics
logger = ServiceLogger("outlook - relay")
metrics = ServiceMetrics("outlook - relay")

# Add middleware and endpoints
add_standard_middleware(app, logger, metrics)
setup_standard_endpoints(app, "outlook - relay", "1.0.0", metrics=metrics)

# Custom endpoint using standard response


@app.get("/api / v1 / emails")
async def get_emails():
    try:
        emails = await fetch_emails()
        return create_success_response(emails)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""