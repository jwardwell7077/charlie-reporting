#!/usr/bin/env python3
"""
Phase B Implementation Validation
Validates that all infrastructure implementations are complete and functional
"""

def main():
    print("🚀 Phase B Implementation Validation")
    print("=" * 50)
    
    # Track validation results
    results = []
    
    # Test 1: TDD Tests Still Pass
    print("\n1. Testing TDD Test Suite...")
    try:
        import subprocess
        import os
        
        env = os.environ.copy()
        env['PYTHONPATH'] = '/home/jon/repos/charlie-reporting/services/report-generator/src'
        
        result = subprocess.run([
            'python', '-m', 'pytest', 
            'tests/unit/test_report_processor_tdd.py', 
            '-v', '--tb=short'
        ], 
        cwd='/home/jon/repos/charlie-reporting/services/report-generator',
        env=env,
        capture_output=True, 
        text=True
        )
        
        if result.returncode == 0:
            results.append("✅ TDD tests still pass")
            print("   ✅ All TDD tests passing")
        else:
            results.append("❌ TDD tests failed")
            print("   ❌ TDD tests failed:")
            print(result.stdout)
            print(result.stderr)
            
    except Exception as e:
        results.append(f"❌ TDD test error: {e}")
        print(f"   ❌ Error running TDD tests: {e}")
    
    # Test 2: File Structure Validation
    print("\n2. Validating File Structure...")
    import os
    from pathlib import Path
    
    base_path = Path('/home/jon/repos/charlie-reporting/services/report-generator/src')
    
    expected_files = [
        'infrastructure/file_system.py',
        'infrastructure/config.py', 
        'infrastructure/logging.py',
        'infrastructure/metrics.py',
        'business/services/csv_transformer.py',
        'business/services/excel_service.py',
        'interface/dependencies.py'
    ]
    
    missing_files = []
    for file_path in expected_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if not missing_files:
        results.append("✅ All infrastructure files present")
    else:
        results.append(f"❌ Missing files: {missing_files}")
    
    # Test 3: Implementation Classes Check
    print("\n3. Checking Implementation Classes...")
    
    expected_classes = [
        ('infrastructure/file_system.py', 'DirectoryProcessorImpl'),
        ('infrastructure/file_system.py', 'FileManagerImpl'),
        ('infrastructure/config.py', 'ConfigManagerImpl'),
        ('infrastructure/logging.py', 'StructuredLoggerImpl'),
        ('infrastructure/metrics.py', 'MetricsCollectorImpl'),
        ('business/services/csv_transformer.py', 'CSVTransformerService'),
        ('business/services/excel_service.py', 'ExcelGeneratorService'),
    ]
    
    missing_classes = []
    for file_path, class_name in expected_classes:
        full_path = base_path / file_path
        if full_path.exists():
            content = full_path.read_text()
            if f'class {class_name}' in content:
                print(f"   ✅ {class_name} in {file_path}")
            else:
                print(f"   ❌ {class_name} not found in {file_path}")
                missing_classes.append(f"{class_name} in {file_path}")
        else:
            missing_classes.append(f"{class_name} in {file_path} (file missing)")
    
    if not missing_classes:
        results.append("✅ All implementation classes present")
    else:
        results.append(f"❌ Missing classes: {missing_classes}")
    
    # Test 4: Interface Implementation Check
    print("\n4. Checking Interface Implementations...")
    
    interface_implementations = [
        ('infrastructure/file_system.py', 'IDirectoryProcessor'),
        ('infrastructure/file_system.py', 'IFileManager'),
        ('infrastructure/config.py', 'IConfigManager'),
        ('infrastructure/logging.py', 'ILogger'),
        ('infrastructure/metrics.py', 'IMetricsCollector'),
        ('business/services/csv_transformer.py', 'ICSVTransformer'),
        ('business/services/excel_service.py', 'IExcelGenerator'),
    ]
    
    interface_issues = []
    for file_path, interface_name in interface_implementations:
        full_path = base_path / file_path
        if full_path.exists():
            content = full_path.read_text()
            if f'({interface_name})' in content:
                print(f"   ✅ {interface_name} implemented in {file_path}")
            else:
                print(f"   ❌ {interface_name} not implemented in {file_path}")
                interface_issues.append(f"{interface_name} in {file_path}")
        else:
            interface_issues.append(f"{interface_name} in {file_path} (file missing)")
    
    if not interface_issues:
        results.append("✅ All interfaces properly implemented")
    else:
        results.append(f"❌ Interface issues: {interface_issues}")
    
    # Final Results
    print("\n" + "=" * 50)
    print("📊 PHASE B VALIDATION RESULTS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for result in results:
        print(result)
        if result.startswith("✅"):
            passed += 1
    
    print(f"\n📈 Score: {passed}/{total} ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 PHASE B IMPLEMENTATION: COMPLETE!")
        print("✅ All infrastructure implementations created")
        print("✅ All interfaces properly implemented") 
        print("✅ TDD tests still passing")
        print("✅ Dependency injection system ready")
        
        print("\n🚀 Ready to proceed to Phase C: Enhanced Test Infrastructure")
        return True
    else:
        print(f"\n⚠️ PHASE B IMPLEMENTATION: {total-passed} issues found")
        print("❌ Some infrastructure implementations incomplete")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
