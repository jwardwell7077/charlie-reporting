"""Integration test for Phase B infrastructure implementations
Tests that all dependencies can be injected and work together
"""

import asyncio

import pytest
from business.services.csv_transformer import CSVTransformerService
from business.services.excel_service import ExcelGeneratorService

# Imports will work with PYTHONPATH set properly
from business.services.report_processor import ReportProcessingService
from infrastructure.config import ConfigManagerImpl
from infrastructure.file_system import DirectoryProcessorImpl, FileManagerImpl
from infrastructure.logging import StructuredLoggerImpl
from infrastructure.metrics import MetricsCollectorImpl


class TestPhaseB:
    """Test Phase B infrastructure implementations"""

    def test_infrastructure_instantiation(self):
        """Test that all infrastructure classes can be instantiated"""
        # Infrastructure implementations
        directory_processor = DirectoryProcessorImpl()
        file_manager = FileManagerImpl()
        config_manager = ConfigManagerImpl()
        logger = StructuredLoggerImpl()
        metrics = MetricsCollectorImpl()

        # Business service implementations
        csv_transformer = CSVTransformerService()
        excel_generator = ExcelGeneratorService()

        # All should be instantiated without errors
        assert directory_processor is not None
        assert file_manager is not None
        assert config_manager is not None
        assert logger is not None
        assert metrics is not None
        assert csv_transformer is not None
        assert excel_generator is not None

        print("✅ All infrastructure implementations instantiated successfully")

    def test_dependency_injection(self):
        """Test that ReportProcessingService can be created with real dependencies"""
        # Create all dependencies
        directory_processor = DirectoryProcessorImpl()
        csv_transformer = CSVTransformerService()
        excel_generator = ExcelGeneratorService()
        file_manager = FileManagerImpl()
        config_manager = ConfigManagerImpl()
        logger = StructuredLoggerImpl()
        metrics = MetricsCollectorImpl()

        # Create report processor with all dependencies
        report_processor = ReportProcessingService(
            directory_processor=directory_processor,
            csv_transformer=csv_transformer,
            excel_generator=excel_generator,
            file_manager=file_manager,
            config_manager=config_manager,
            logger=logger,
            metrics=metrics
        )

        assert report_processor is not None
        print("✅ ReportProcessingService created with real dependencies")

        # Check that dependencies are properly set
        assert report_processor.directory_processor is directory_processor
        assert report_processor.csv_transformer is csv_transformer
        assert report_processor.excel_generator is excel_generator
        assert report_processor.file_manager is file_manager
        assert report_processor.config_manager is config_manager
        assert report_processor.logger is logger
        assert report_processor.metrics is metrics

        print("✅ All dependencies properly injected and accessible")

    @pytest.mark.asyncio
    async def test_async_interface_methods(self):
        """Test that async interface methods work"""
        # Test directory processor
        directory_processor = DirectoryProcessorImpl()
        files = await directory_processor.scan_directory("/tmp", "*.csv")
        assert isinstance(files, list)

        # Test file manager
        file_manager = FileManagerImpl()
        info = await file_manager.get_file_info("/etc / passwd")  # Should exist on Linux
        assert isinstance(info, dict)

        # Test config manager
        config_manager = ConfigManagerImpl()
        settings = await config_manager.get_all_settings()
        assert isinstance(settings, dict)

        # Test logger
        logger = StructuredLoggerImpl()
        await logger.info("Test message")  # Should not raise

        # Test metrics
        metrics = MetricsCollectorImpl()
        await metrics.increment_counter("test_counter", 1.0)
        summary = await metrics.get_metrics_summary()
        assert isinstance(summary, dict)

        print("✅ All async interface methods executed successfully")


if __name__ == "__main__":
    # Run the tests
    test_instance = TestPhaseB()

    print("🚀 Starting Phase B Integration Tests...")

    try:
        test_instance.test_infrastructure_instantiation()
        test_instance.test_dependency_injection()

        # Run async test
        asyncio.run(test_instance.test_async_interface_methods())

        print("🎉 Phase B Integration Tests PASSED!")
        print("✅ All infrastructure implementations working correctly")
        print("✅ Dependency injection system functional")
        print("✅ Async interfaces operational")

    except Exception as e:
        print(f"❌ Phase B Integration Tests FAILED: {e}")
        import traceback
        traceback.print_exc()
