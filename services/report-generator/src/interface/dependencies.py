"""Dependency Injection Configuration for Report Generator Service
FastAPI dependency injection with interface - based design for testing
"""

from functools import lru_cache
from typing import Annotated

from business.interfaces import (
    IConfigManager,
    ICSVTransformer,
    IDirectoryProcessor,
    IExcelGenerator,
    IFileManager,
    ILogger,
    IMetricsCollector,
)
from business.services.report_processor import ReportProcessingService
from fastapi import Depends


@lru_cache
def get_directory_processor() -> IDirectoryProcessor:
    """Get directory processor implementation"""
    from infrastructure.file_system import DirectoryProcessorImpl

    return DirectoryProcessorImpl()


@lru_cache
def get_csv_transformer() -> ICSVTransformer:
    """Get CSV transformer implementation"""
    from business.services.csv_transformer import CSVTransformerService

    return CSVTransformerService()


@lru_cache
def getexcel_generator() -> IExcelGenerator:
    """Get Excel generator implementation"""
    from business.services.excel_service import ExcelGeneratorService

    return ExcelGeneratorService()


@lru_cache
def get_file_manager() -> IFileManager:
    """Get file manager implementation"""
    from infrastructure.file_system import FileManagerImpl

    return FileManagerImpl()


@lru_cache
def get_config_manager() -> IConfigManager:
    """Get configuration manager implementation"""
    from infrastructure.config import ConfigManagerImpl

    return ConfigManagerImpl()


@lru_cache
def get_logger() -> ILogger:
    """Get logger implementation"""
    from infrastructure.logging import StructuredLoggerImpl

    return StructuredLoggerImpl()


@lru_cache
def get_metrics_collector() -> IMetricsCollector:
    """Get metrics collector implementation"""
    from infrastructure.metrics import MetricsCollectorImpl

    return MetricsCollectorImpl()


@lru_cache
def get_report_processor(
    directory_processor: Annotated[IDirectoryProcessor, Depends(get_directory_processor)],
    csv_transformer: Annotated[ICSVTransformer, Depends(get_csv_transformer)],
    excel_generator: Annotated[IExcelGenerator, Depends(getexcel_generator)],
    file_manager: Annotated[IFileManager, Depends(get_file_manager)],
    config_manager: Annotated[IConfigManager, Depends(get_config_manager)],
    logger: Annotated[ILogger, Depends(get_logger)],
    metrics: Annotated[IMetricsCollector, Depends(get_metrics_collector)],
) -> ReportProcessingService:
    """Create main report processing service with all dependencies injected

    This is the main service orchestrator that coordinates all other services
    """
    return ReportProcessingService(
        directory_processor=directory_processor,
        csv_transformer=csv_transformer,
        excel_generator=excel_generator,
        file_manager=file_manager,
        config_manager=config_manager,
        logger=logger,
        metrics=metrics,
    )


# Test dependency overrides (used in testing)
test_overrides = {}


def override_dependency(interface_type, implementation):
    """Override a dependency for testing purposes"""
    test_overrides[interface_type] = implementation


def get_test_dependency(interface_type):
    """Get test override for dependency"""
    return test_overrides.get(interface_type)


def clear_test_overrides():
    """Clear all test dependency overrides"""
    test_overrides.clear()
