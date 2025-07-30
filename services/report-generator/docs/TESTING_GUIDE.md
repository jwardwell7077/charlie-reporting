# Testing Infrastructure User Guide

## 🧪 **Overview**

This guide explains how to use the comprehensive testing infrastructure created as part of the TDD refactoring project.

## 📋 **Quick Reference**

### **Running Tests**

```bash
# Run all TDD tests
cd services/report-generator
PYTHONPATH="src:tests" python -m pytest tests/unit/test_report_processor_tdd.py -v

# Run Phase C infrastructure tests
PYTHONPATH="src:tests" python -m pytest tests/test_phase_c_basic.py -v

# Run with coverage
PYTHONPATH="src:tests" python -m pytest --cov=business --cov=infrastructure tests/ -v
```

### **Test Markers**

The project uses pytest markers to categorize tests:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests  
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.smoke` - Smoke tests
- `@pytest.mark.slow` - Tests that take longer to run

## 🏗️ **Test Infrastructure Components**

### **1. Enhanced Fixtures (`tests/fixtures/enhanced_fixtures.py`)**

#### **Using Mock Services**

```python
def test_feature(all_mock_services, assert_helpers):
    """Test using all mock services"""
    
    # Configure mock behavior
    all_mock_services['directory_processor'].set_files_to_return([
        '/path/to/file1.csv',
        '/path/to/file2.csv'
    ])
    
    # Create service with mocks
    service = ReportProcessingService(**all_mock_services)
    
    # Test the feature
    result = await service.process_directory('/test/path')
    
    # Validate results
    assert_helpers.assert_processing_result_success(result)
```

#### **Using Test Data**

```python
def test_with_realistic_data(sample_csv_files, temp_output_dir):
    """Test with realistic CSV files"""
    
    # sample_csv_files provides real CSV files
    # temp_output_dir provides clean output directory
    
    for csv_file in sample_csv_files:
        # Process each file
        result = process_csv_file(csv_file.file_path)
        assert result.success
```

#### **Performance Testing**

```python
@pytest.mark.performance
def test_performance(performance_timer, performance_thresholds):
    """Test performance within thresholds"""
    
    with performance_timer:
        result = await expensive_operation()
    
    # Automatic validation against thresholds
    assert performance_timer.elapsed() < performance_thresholds['max_processing_time']
```

### **2. Test Data Factories (`tests/fixtures/test_data_factories.py`)**

#### **Creating Test Data**

```python
def test_with_generated_data(csv_data_factory):
    """Test with factory-generated data"""
    
    # Generate realistic ACQ data
    acq_data = csv_data_factory.create_acq_data(num_records=100)
    
    # Generate productivity data
    productivity_data = csv_data_factory.create_productivity_data(num_records=50)
    
    # Data is realistic and ready for testing
    assert len(acq_data) == 100
    assert 'deal_id' in acq_data.columns
```

#### **Creating Test Environments**

```python
def test_with_test_environment():
    """Test with complete test environment"""
    
    with TestEnvironmentFactory() as env:
        # Create temporary directory with files
        temp_dir, csv_files = env.create_test_directory_with_files(
            file_types=["ACQ", "Productivity"],
            num_dates=2,
            num_hours=2
        )
        
        # Use the environment for testing
        result = process_directory(temp_dir)
        assert len(result.files_processed) == len(csv_files)
    
    # Environment automatically cleaned up
```

### **3. Test Utilities (`tests/utils/test_utilities.py`)**

#### **Using TestTimer**

```python
def test_with_timing():
    """Test with automatic timing"""
    
    timer = TestTimer("Database Operation")
    
    with timer:
        # Code to time
        result = perform_database_operation()
    
    # Timer automatically reports duration
    assert timer.elapsed_seconds < 1.0
    print(f"Operation took: {timer.elapsed_seconds:.3f}s")
```

#### **Using Enhanced Assertions**

```python
def test_with_enhanced_assertions(assert_helpers):
    """Test with enhanced assertion helpers"""
    
    result = ProcessingResult(
        success=True,
        files_processed=3,
        total_records=150,
        processing_time_seconds=2.5,
        output_file="/tmp/output.xlsx",
        errors=[],
        warnings=[]
    )
    
    # Enhanced assertions provide better error messages
    assert_helpers.assert_processing_result_success(result)
    
    # Validate mock interactions
    assert_helpers.assert_mock_called(mock_service, 'process_file', times=3)
```

#### **Using Test Reporter**

```python
def test_with_reporting():
    """Test with automatic reporting"""
    
    # Record test results
    test_reporter.record_test_result(
        test_name="Integration Test",
        success=True,
        duration=1.5,
        files_processed=5
    )
    
    # Get comprehensive summary
    summary = test_reporter.get_summary()
    assert summary['total_tests'] > 0
    assert summary['success_rate'] >= 90.0
```

## 🎯 **Testing Patterns**

### **1. Unit Testing Pattern**

```python
@pytest.mark.unit
def test_unit_feature(all_mock_services):
    """Unit test with all dependencies mocked"""
    
    # Arrange: Configure mocks
    all_mock_services['csv_transformer'].set_transform_result({
        'success': True,
        'dataframe': mock_dataframe
    })
    
    # Act: Execute unit
    service = ReportProcessingService(**all_mock_services)
    result = await service.transform_csv('/test/file.csv')
    
    # Assert: Validate behavior
    assert result['success'] is True
    assert all_mock_services['csv_transformer'].get_call_count('transform_csv') == 1
```

### **2. Integration Testing Pattern**

```python
@pytest.mark.integration
def test_integration_workflow(isolated_test_environment, assert_helpers):
    """Integration test with realistic environment"""
    
    # Use isolated environment
    input_dir = isolated_test_environment['input_directory']
    output_dir = isolated_test_environment['output_directory']
    
    # Execute full workflow
    result = await full_processing_workflow(input_dir, output_dir)
    
    # Validate end-to-end results
    assert_helpers.assert_processing_result_success(result)
    assert_helpers.assert_files_created(output_dir, expected_count=1)
```

### **3. Performance Testing Pattern**

```python
@pytest.mark.performance
@pytest.mark.slow
def test_performance_under_load(large_test_directory, performance_thresholds):
    """Performance test with large data sets"""
    
    temp_dir, csv_files = large_test_directory
    
    start_time = time.time()
    result = await process_large_dataset(temp_dir)
    duration = time.time() - start_time
    
    # Validate performance
    assert duration < performance_thresholds['max_processing_time']
    assert result.files_processed == len(csv_files)
```

### **4. Error Testing Pattern**

```python
@pytest.mark.unit
def test_error_handling(error_scenario, assert_helpers):
    """Test error handling scenarios"""
    
    # Use pre-configured error scenario
    services = error_scenario['services']
    expected_error = error_scenario['expected_error']
    
    # Execute with expected error
    result = await service_with_mocks.process_directory('/test/path')
    
    # Validate error handling
    assert_helpers.assert_processing_result_failure(result, expected_error)
    assert_helpers.assert_mock_called(services['logger'], 'error')
```

## 🛠️ **Creating New Tests**

### **Step 1: Choose Test Type**

- **Unit Test**: Testing single function/method in isolation
- **Integration Test**: Testing service interactions
- **Performance Test**: Testing speed/resource usage

### **Step 2: Select Fixtures**

```python
# For unit tests
def test_unit(all_mock_services, assert_helpers):

# For integration tests  
def test_integration(isolated_test_environment, sample_csv_files):

# For performance tests
def test_performance(performance_timer, large_test_directory):
```

### **Step 3: Follow TDD Pattern**

1. **Red**: Write failing test first
2. **Green**: Implement minimal code to pass
3. **Refactor**: Improve while keeping tests green

### **Step 4: Use Enhanced Assertions**

```python
# Instead of basic asserts
assert result.success == True

# Use enhanced assertions
assert_helpers.assert_processing_result_success(result)
```

## 🎯 **Best Practices**

### **Test Organization**

- **Unit tests**: `tests/unit/`
- **Integration tests**: `tests/integration/`
- **Test fixtures**: `tests/fixtures/`
- **Test utilities**: `tests/utils/`

### **Naming Conventions**

- Test files: `test_*.py`
- Test methods: `test_*`
- Fixtures: Descriptive names without `test_` prefix

### **Mock Usage**

- Mock all external dependencies
- Use provided mock services
- Reset mocks between tests (automatic with fixtures)

### **Performance Testing**

- Use `@pytest.mark.performance` for performance tests
- Set realistic thresholds
- Test with varying data sizes

### **Error Testing**

- Test all error conditions
- Validate error messages
- Ensure proper error propagation

## 📊 **Test Execution**

### **Running Specific Test Types**

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Performance tests only
pytest -m performance

# Exclude slow tests
pytest -m "not slow"
```

### **Coverage Reporting**

```bash
# Generate coverage report
pytest --cov=business --cov=infrastructure --cov-report=html tests/

# View coverage in browser
open htmlcov/index.html
```

### **Parallel Execution**

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto tests/
```

## 🚀 **Advanced Usage**

### **Custom Test Scenarios**

```python
@pytest.fixture
def custom_scenario(all_mock_services):
    """Create custom test scenario"""
    
    # Configure specific behavior
    all_mock_services['directory_processor'].set_files_to_return([
        '/custom/file1.csv',
        '/custom/file2.csv'  
    ])
    
    return {
        'services': all_mock_services,
        'expected_files': 2,
        'scenario_type': 'custom'
    }
```

### **Parameterized Tests**

```python
@pytest.mark.parametrize("file_count,expected_result", [
    (0, False),      # No files should fail
    (1, True),       # One file should succeed  
    (5, True),       # Multiple files should succeed
])
def test_various_file_counts(file_count, expected_result, all_mock_services):
    """Test with different file counts"""
    
    files = [f'/test/file{i}.csv' for i in range(file_count)]
    all_mock_services['directory_processor'].set_files_to_return(files)
    
    result = await service.process_directory('/test')
    assert result.success == expected_result
```

This testing infrastructure provides everything needed for comprehensive, maintainable, and efficient testing of the report-generator service and can be extended for the DB service integration.
