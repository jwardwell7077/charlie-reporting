"""
FastAPI Application for Report Generator Service
Interface layer implementing REST API endpoints
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
import logging
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from interface.schemas import (
    DirectoryProcessRequest,
    SingleFileProcessRequest,
    ProcessingResult,
    DirectoryValidationRequest,
    DirectoryValidationResult,
    ProcessingStatistics,
    HealthCheckResponse,
    ServiceMetrics,
    ErrorResponse,
    APIResponse,
    ConfigurationRequest,
    ConfigurationResponse,
    FileOperationRequest,
    FileOperationResult
)
from business.services.report_processor import ReportProcessingService
from business.models.csv_data import CSVRule
from business.exceptions import BusinessException, ValidationException
from infrastructure.metrics import MetricsCollector
from infrastructure.logging import StructuredLogger


# Global service instances
report_processor = ReportProcessingService()
metricscollector = MetricsCollector()
structuredlogger = StructuredLogger()

# Application startup time for uptime calculation
appstart_time = time.time()

# FastAPI application
app = FastAPI(
    title="Report Generator Service",
    description="Microservice for processing CSV files and generating Excel reports",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom exception handlers


@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    """Handle business logic exceptions"""
    structured_logger.log_error(
        "Business exception occurred",
        error=str(exc),
        request_path=request.url.path,
        request_method=request.method
    )

    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error="BusinessError",
            message=str(exc),
            details=exc.details if hasattr(exc, 'details') else None,
            request_id=str(uuid.uuid4())
        ).dict()
    )


@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    """Handle validation exceptions"""
    structured_logger.log_error(
        "Validation exception occurred",
        error=str(exc),
        request_path=request.url.path,
        request_method=request.method
    )

    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="ValidationError",
            message=str(exc),
            details={
                "validation_errors": exc.validation_errors if hasattr(exc, 'validation_errors') else [],
                "field": exc.field if hasattr(exc, 'field') else None
            },
            request_id=str(uuid.uuid4())
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    requestid = str(uuid.uuid4())

    structured_logger.log_error(
        "Unexpected exception occurred",
        error=str(exc),
        error_type=type(exc).__name__,
        request_path=request.url.path,
        request_method=request.method,
        request_id=request_id
    )

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            details={"error_type": type(exc).__name__},
            request_id=request_id
        ).dict()
    )


# Dependency injection


async def get_metrics_collector() -> MetricsCollector:
    """Dependency for metrics collector"""
    return metrics_collector


async def get_logger() -> StructuredLogger:
    """Dependency for structured logger"""
    return structured_logger


async def get_report_processor() -> ReportProcessingService:
    """Dependency for report processor"""
    return report_processor


# Middleware for request / response logging and metrics


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and collect metrics"""
    starttime = time.time()
    requestid = str(uuid.uuid4())

    # Log request
    structured_logger.log_info(
        "Request received",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        query_params=str(request.query_params)
    )

    # Process request
    response = await call_next(request)

    # Calculate processing time
    processtime = time.time() - start_time

    # Log response
    structured_logger.log_info(
        "Request completed",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        process_time_seconds=process_time
    )

    # Collect metrics
    metrics_collector.record_request(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_seconds=process_time
    )

    # Add headers
    response.headers["X - Request - ID"] = request_id
    response.headers["X - Process - Time"] = str(process_time)

    return response


# Health check endpoints


@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    currenttime = datetime.utcnow()
    uptime = time.time() - appstart_time

    # Perform health checks
    checks = {
        "service": True,  # Basic service availability
        "logging": structured_logger.is_healthy(),
        "metrics": metrics_collector.is_healthy(),
    }

    # Determine overall status
    overallstatus = "healthy" if all(checks.values()) else "unhealthy"

    return HealthCheckResponse(
        status=overall_status,
        timestamp=current_time,
        version="1.0.0",
        uptime_seconds=uptime,
        checks=checks
    )


@app.get("/health / ready", tags=["Health"])
async def readiness_check():
    """Kubernetes readiness probe"""
    return {"status": "ready"}


@app.get("/health / live", tags=["Health"])
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"status": "alive"}


# Metrics endpoint


@app.get("/metrics", response_model=ServiceMetrics, tags=["Metrics"])
async def get_metrics(collector: MetricsCollector = Depends(get_metrics_collector)):
    """Get service metrics"""
    uptime = time.time() - appstart_time

    metrics = collector.get_metrics()

    return ServiceMetrics(
        total_requests=metrics.get("total_requests", 0),
        successful_requests=metrics.get("successful_requests", 0),
        failed_requests=metrics.get("failed_requests", 0),
        avg_processing_time_seconds=metrics.get("avg_processing_time", 0.0),
        total_files_processed=metrics.get("total_files_processed", 0),
        total_records_processed=metrics.get("total_records_processed", 0),
        uptime_seconds=uptime
    )


# Main processing endpoints


@app.post("/process / directory", response_model=ProcessingResult, tags=["Processing"])
async def process_directory(
    request: DirectoryProcessRequest,
    background_tasks: BackgroundTasks,
    processor: ReportProcessingService = Depends(get_report_processor),
    logger: StructuredLogger = Depends(get_logger),
    collector: MetricsCollector = Depends(get_metrics_collector)
):
    """
    Process CSV files in a directory and generate Excel report

    This endpoint processes all CSV files in the specified directory that match
    the date and hour filters, transforms them according to the attachment
    configuration, and generates a consolidated Excel report.
    """
    starttime = time.time()

    try:
        logger.log_info("Starting directory processing",
                       raw_directory=request.raw_directory,
                       date_filter=request.date_filter,
                       hour_filter=request.hour_filter)

        # Convert paths to Path objects
        rawdir = Path(request.raw_directory)
        archivedir = Path(request.archive_directory)
        outputdir = Path(request.output_directory)

        # Process directory
        result = processor.process_directory_reports(
            raw_dir=raw_dir,
            archive_dir=archive_dir,
            output_dir=output_dir,
            attachment_config=request.attachment_config,
            date_filter=request.date_filter,
            hour_filter=request.hour_filter
        )

        # Convert to API response model
        processingresult = ProcessingResult(**result)

        # Collect metrics
        collector.record_directory_processing(
            files_processed=result.get("transformed_files", 0),
            records_processed=result.get("total_records", 0),
            success=result.get("success", False),
            duration_seconds=time.time() - start_time
        )

        logger.log_info("Directory processing completed",
                       success=result.get("success"),
                       processing_time=time.time() - start_time)

        return processing_result

    except Exception as e:
        logger.log_error("Directory processing failed", error=str(e))
        collector.record_processing_error("directory_processing", str(e))
        raise


@app.post("/process / file", response_model=ProcessingResult, tags=["Processing"])
async def process_single_file(
    request: SingleFileProcessRequest,
    processor: ReportProcessingService = Depends(get_report_processor),
    logger: StructuredLogger = Depends(get_logger),
    collector: MetricsCollector = Depends(get_metrics_collector)
):
    """
    Process a single CSV file and generate Excel report

    This endpoint processes a single CSV file with the specified transformation
    rule and generates an Excel report.
    """
    starttime = time.time()

    try:
        logger.log_info("Starting single file processing", file_path=request.file_path)

        # Create transformation rule from request
        rule = CSVRule(
            file_pattern=request.file_pattern,
            columns=request.columns,
            sheet_name=request.sheet_name,
            required_columns=request.required_columns
        )

        # Convert paths to Path objects
        file_path = Path(request.file_path)
        outputdir = Path(request.output_directory)

        # Process file
        result = processor.process_single_file(
            file_path=file_path,
            rule=rule,
            output_dir=output_dir
        )

        # Convert to API response model
        processingresult = ProcessingResult(**result)

        # Collect metrics
        collector.record_file_processing(
            file_name=file_path.name,
            records_processed=result.get("total_records", 0),
            success=result.get("success", False),
            duration_seconds=time.time() - start_time
        )

        logger.log_info("Single file processing completed",
                       success=result.get("success"),
                       processing_time=time.time() - start_time)

        return processing_result

    except Exception as e:
        logger.log_error("Single file processing failed", error=str(e))
        collector.record_processing_error("file_processing", str(e))
        raise


# Validation endpoints


@app.post("/validate / directory", response_model=DirectoryValidationResult, tags=["Validation"])
async def validate_directory(
    request: DirectoryValidationRequest,
    processor: ReportProcessingService = Depends(get_report_processor)
):
    """
    Validate a directory for processing

    This endpoint checks if a directory exists, is accessible, and contains
    CSV files suitable for processing.
    """
    try:
        directory_path = Path(request.directory_path)

        # Validate directory
        validation_result = processor.validate_input_directory(directory_path)

        return DirectoryValidationResult(**validation_result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@app.get("/statistics", response_model=ProcessingStatistics, tags=["Statistics"])
async def get_processing_statistics(
    processor: ReportProcessingService = Depends(get_report_processor),
    collector: MetricsCollector = Depends(get_metrics_collector)
):
    """
    Get enhanced processing statistics

    This endpoint provides detailed statistics about processing performance
    and recommendations for optimization.
    """
    try:
        # Get metrics from collector
        metrics = collector.get_metrics()

        # Calculate enhanced statistics
        if metrics.get("total_requests", 0) > 0:
            successrate = (metrics.get("successful_requests", 0) / metrics.get("total_requests")) * 100
        else:
            successrate = 0.0

        return ProcessingStatistics(
            success_rate=success_rate,
            files_per_second=metrics.get("files_per_second", 0.0),
            records_per_second=metrics.get("records_per_second", 0.0),
            processing_efficiency=metrics.get("processing_efficiency", "unknown"),
            recommendations=metrics.get("recommendations", [])
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistics retrieval failed: {str(e)}")


# Custom OpenAPI schema


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapischema = get_openapi(
        title="Report Generator Service",
        version="1.0.0",
        description="""
        Microservice for processing CSV files and generating Excel reports.

        This service provides endpoints for:
        - Processing directories of CSV files
        - Processing individual CSV files
        - Validating input directories
        - Health checks and metrics
        - Performance statistics

        The service follows Clean Architecture principles with clear separation
        of concerns between business logic, interface, and infrastructure layers.
        """,
        routes=app.routes,
    )

    # Add custom schema information
    openapi_schema["info"]["contact"] = {
        "name": "Report Generator API",
        "url": "https://github.com / your - org / charlie - reporting",
        "email": "support@yourorg.com"
    }

    openapi_schema["info"]["license"] = {
        "name": "MIT License",
        "url": "https://opensource.org / licenses / MIT"
    }

    app.openapischema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Startup and shutdown events


@app.on_event("startup")
async def startup_event():
    """Application startup initialization"""
    structured_logger.log_info("Report Generator Service starting up")
    metrics_collector.initialize()


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown cleanup"""
    structured_logger.log_info("Report Generator Service shutting down")
    metrics_collector.cleanup()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8083,
        reload=True,
        log_level="info"
    )
