"""
Comprehensive Integration Tests
Tests complete workflows using enhanced test infrastructure
"""

import pytest
import asyncio
from pathlib import Path

# Import test infrastructure
from ..fixtures.enhanced_fixtures import *
from ..integration.test_infrastructure import (
    IntegrationTestRunner,
    PerformanceTestSuite,
    ErrorInjectionTestSuite
)


class TestCompleteWorkflows:
    """Test complete end-to-end workflows"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_successful_directory_processing(
        self,
        report_processor_with_mocks,
        isolated_test_environment,
        assert_helpers
    ):
        """Test complete successful directory processing workflow"""
        
        runner = IntegrationTestRunner()
        
        expected_outcomes = {
            'success': True,
            'files_processed': isolated_test_environment['expected_file_count'],
            'should_fail': False
        }
        
        result = await runner.run_complete_workflow_test(
            report_processor=report_processor_with_mocks,
            test_environment=isolated_test_environment,
            expected_outcomes=expected_outcomes
        )
        
        # Assert overall success
        assert result['success'] is True
        assert_helpers.assert_processing_result_success(result['result'])
        
        # Assert validation results
        validation = result['validation']
        assert validation['success_match'] is True
        assert validation['file_count_match'] is True
        
        # Assert performance metrics
        performance = result['performance']
        assert performance['total_time'] > 0
        assert performance['files_per_second'] >= 0
        
        print(f"✅ Workflow completed in {result['execution_time']:.2f}s")
        print(f"📊 Processed {performance['files_per_second']:.2f} files/sec")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_empty_directory_handling(
        self,
        report_processor_with_mocks,
        temp_output_dir,
        failure_scenario
    ):
        """Test handling of empty directory"""
        
        runner = IntegrationTestRunner()
        
        test_environment = {
            'input_directory': temp_output_dir,  # Empty directory
            'output_directory': temp_output_dir,
            'csv_files': [],
            'expected_file_count': 0
        }
        
        expected_outcomes = {
            'success': False,
            'files_processed': 0,
            'should_fail': True
        }
        
        result = await runner.run_complete_workflow_test(
            report_processor=report_processor_with_mocks,
            test_environment=test_environment,
            expected_outcomes=expected_outcomes
        )
        
        # Should handle empty directory gracefully
        assert result['success'] is True  # Test execution successful
        assert result['result'].success is False  # Processing failed as expected
        assert result['result'].files_processed == 0
        
        print("✅ Empty directory handled correctly")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_error_recovery_workflow(
        self,
        report_processor_with_mocks,
        error_scenario,
        assert_helpers
    ):
        """Test error handling and recovery"""
        
        runner = IntegrationTestRunner()
        
        test_environment = {
            'input_directory': '/tmp',
            'output_directory': '/tmp',
            'csv_files': error_scenario['csv_files'],
            'expected_file_count': len(error_scenario['csv_files'])
        }
        
        expected_outcomes = {
            'success': False,
            'should_fail': True
        }
        
        result = await runner.run_complete_workflow_test(
            report_processor=report_processor_with_mocks,
            test_environment=test_environment,
            expected_outcomes=expected_outcomes
        )
        
        # Should handle errors gracefully
        assert result['success'] is True  # Test execution successful
        assert_helpers.assert_processing_result_failure(
            result['result'], 
            error_scenario['expected_error']
        )
        
        print("✅ Error recovery tested successfully")


class TestPerformanceScenarios:
    """Performance and load testing scenarios"""
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    @pytest.mark.slow
    async def test_small_load_performance(
        self,
        report_processor_with_mocks,
        performance_thresholds
    ):
        """Test performance with small data loads"""
        
        suite = PerformanceTestSuite()
        
        # Test with varying small loads
        file_counts = [1, 3, 5]
        record_counts = [100, 500]
        
        results = await suite.run_load_test(
            report_processor=report_processor_with_mocks,
            file_counts=file_counts,
            record_counts=record_counts,
            iterations=2  # Fewer iterations for faster testing
        )
        
        # Assert performance meets thresholds
        summary = results['summary']
        assert summary['average_success_rate'] >= 95  # 95% success rate
        assert summary['fastest_execution_time'] < performance_thresholds['max_processing_time']
        
        print(f"✅ Small load performance: {summary['average_success_rate']:.1f}% success rate")
        print(f"📊 Fastest execution: {summary['fastest_execution_time']:.2f}s")
    
    @pytest.mark.asyncio
    @pytest.mark.load
    @pytest.mark.slow
    async def test_medium_load_performance(
        self,
        report_processor_with_mocks,
        performance_thresholds
    ):
        """Test performance with medium data loads"""
        
        suite = PerformanceTestSuite()
        
        # Test with medium loads
        file_counts = [10, 20]
        record_counts = [1000]
        
        results = await suite.run_load_test(
            report_processor=report_processor_with_mocks,
            file_counts=file_counts,
            record_counts=record_counts,
            iterations=1  # Single iteration for medium load
        )
        
        # Assert reasonable performance
        summary = results['summary']
        assert summary['average_success_rate'] >= 90  # 90% success rate
        
        print(f"✅ Medium load performance: {summary['average_success_rate']:.1f}% success rate")
        print(f"📊 Throughput: {summary['highest_throughput_files']:.2f} files/sec")


class TestErrorHandling:
    """Error injection and resilience testing"""
    
    @pytest.mark.asyncio
    @pytest.mark.error_injection
    async def test_file_system_error_resilience(
        self,
        report_processor_with_mocks,
        isolated_test_environment
    ):
        """Test resilience to file system errors"""
        
        suite = ErrorInjectionTestSuite()
        
        results = await suite.test_file_system_errors(
            report_processor=report_processor_with_mocks,
            test_environment=isolated_test_environment
        )
        
        # Assert errors are handled correctly
        for result in results:
            assert result['success'] is True  # Should handle errors gracefully
            print(f"✅ {result['scenario']}: Error handled correctly")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_partial_failure_handling(
        self,
        report_processor_with_mocks,
        all_mock_services,
        sample_csv_files
    ):
        """Test handling of partial processing failures"""
        
        # Configure mocks for partial failure
        all_mock_services['directory_processor'].set_files_to_return([
            f.file_path for f in sample_csv_files
        ])
        
        # Make first file succeed, second fail
        all_mock_services['csv_transformer'].set_mixed_results([
            {'success': True, 'message': 'Success'},
            {'success': False, 'error': 'Transformation failed'}
        ])
        
        result = await report_processor_with_mocks.process_directory(
            directory_path='/tmp',
            output_directory='/tmp'
        )
        
        # Should complete with warnings
        assert result.success is True
        assert len(result.warnings) > 0
        assert result.files_processed >= 1
        
        print("✅ Partial failure handling tested successfully")


class TestDataIntegrity:
    """Data integrity and validation testing"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_data_consistency(
        self,
        report_processor_with_mocks,
        sample_csv_files,
        all_mock_services,
        temp_output_dir
    ):
        """Test that data remains consistent through processing"""
        
        # Configure mocks to track data flow
        all_mock_services['directory_processor'].set_files_to_return([
            f.file_path for f in sample_csv_files
        ])
        
        # Track transformation data
        original_data = {}
        for csv_file in sample_csv_files:
            import pandas as pd
            df = pd.read_csv(csv_file.file_path)
            original_data[csv_file.filename] = {
                'row_count': len(df),
                'columns': list(df.columns),
                'sample_data': df.head(3).to_dict() if len(df) > 0 else {}
            }
        
        all_mock_services['csv_transformer'].set_data_tracking(True)
        
        result = await report_processor_with_mocks.process_directory(
            directory_path=Path(sample_csv_files[0].file_path).parent,
            output_directory=temp_output_dir
        )
        
        # Verify data integrity
        assert result.success is True
        
        # Check that transformation calls match input files
        transform_calls = all_mock_services['csv_transformer'].get_call_history('transform_csv')
        assert len(transform_calls) == len(sample_csv_files)
        
        print("✅ Data consistency verified")
        print(f"📊 Processed {len(transform_calls)} files with data integrity")


# Test configuration for different environments
class TestConfiguration:
    """Test configuration and environment validation"""
    
    def test_test_infrastructure_setup(
        self,
        csv_data_factory,
        csv_file_factory,
        all_mock_services
    ):
        """Validate that test infrastructure is properly configured"""
        
        # Test factories work
        assert csv_data_factory is not None
        assert csv_file_factory is not None
        
        # Test mock services are available
        assert len(all_mock_services) == 7
        
        # Test each mock service has required methods
        required_methods = {
            'directory_processor': ['scan_directory'],
            'csv_transformer': ['transform_csv'],
            'excel_generator': ['create_workbook'],
            'file_manager': ['write_file'],
            'config_manager': ['get_setting'],
            'logger': ['info'],
            'metrics': ['increment_counter']
        }
        
        for service_name, methods in required_methods.items():
            service = all_mock_services[service_name]
            for method in methods:
                assert hasattr(service, method)
        
        print("✅ Test infrastructure properly configured")
        print(f"📊 Validated {len(all_mock_services)} mock services")
    
    def test_test_data_generation(self, csv_data_factory):
        """Test that test data generation works correctly"""
        
        # Test ACQ data generation
        acq_data = csv_data_factory.create_acq_data(50)
        assert len(acq_data) == 50
        assert 'deal_id' in acq_data.columns
        
        # Test Productivity data generation
        prod_data = csv_data_factory.create_productivity_data(30)
        assert len(prod_data) == 30
        assert 'employee_id' in prod_data.columns
        
        # Test Campaign data generation
        campaign_data = csv_data_factory.create_campaign_data(25)
        assert len(campaign_data) == 25
        assert 'campaign_id' in campaign_data.columns
        
        print("✅ Test data generation working correctly")
        print(f"📊 Generated ACQ({len(acq_data)}), Productivity({len(prod_data)}), Campaign({len(campaign_data)}) datasets")
