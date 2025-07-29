"""
run_integration_tests.py
-----------------------
Integration test runner with safety checks and comprehensive reporting.

Author: Jonathan Wardwell, Copilot, GPT-4o
License: MIT
"""

import os
import sys
import logging
import unittest
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def get_python_executable():
    """Get the correct Python executable path for this environment."""
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # We're in a virtual environment, use current executable
        return sys.executable
    
    # Check for .venv in project root
    venv_python = project_root / '.venv' / 'Scripts' / 'python.exe'
    if venv_python.exists():
        return str(venv_python)
    
    # Fallback to current executable
    return sys.executable

def setup_logging():
    """Set up comprehensive logging for integration test run."""
    log_dir = os.path.join(project_root, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'integration_test_run_{timestamp}.log')
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Console handler (INFO level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (DEBUG level)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    return log_file

def check_prerequisites():
    """Check all prerequisites before running integration tests."""
    logger = logging.getLogger('integration_runner')
    logger.info("Checking integration test prerequisites...")
    
    # Check for integration config file
    config_path = os.path.join(project_root, 'tests', 'config', 'integration-config.toml')
    if not os.path.exists(config_path):
        logger.error(f"Integration config file not found: {config_path}")
        return False
    
    # Check for required environment variables
    required_env_vars = [
        'INTEGRATION_TEST_EMAIL_PASSWORD',
        'INTEGRATION_TEST_APP_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please set these environment variables before running integration tests:")
        for var in missing_vars:
            logger.error(f"  set {var}=your_password_here")
        return False
    
    # Check if integration tests are enabled
    try:
        from tests.config_loader_enhanced import EnhancedConfigLoader
        config_loader = EnhancedConfigLoader()
        config = config_loader.load_integration_config()
        
        if not config.get('integration_tests', {}).get('enabled', False):
            logger.error("Integration tests are disabled in configuration")
            logger.error("To enable, set integration_tests.enabled = true in integration-config.toml")
            logger.error("or set environment variable: INTEGRATION_TESTS_ENABLED=true")
            return False
        
    except Exception as e:
        logger.error(f"Failed to load integration config: {e}")
        return False
    
    logger.info("✓ All prerequisites checked successfully")
    return True

def run_integration_tests():
    """Run the complete integration test suite."""
    logger = logging.getLogger('integration_runner')
    
    # Set up test discovery
    test_dir = os.path.join(project_root, 'tests')
    
    # Create test suite
    loader = unittest.TestLoader()
    
    # Load specific integration test module
    try:
        suite = loader.loadTestsFromName('test_integration_complete.TestCompleteIntegration', module=None)
    except Exception as e:
        logger.error(f"Failed to load integration tests: {e}")
        return False
    
    # Set up test runner with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        buffer=False,
        failfast=False
    )
    
    # Run tests
    logger.info("Starting integration test execution...")
    start_time = time.time()
    
    result = runner.run(suite)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Report results
    logger.info(f"Integration test execution completed in {duration:.2f} seconds")
    logger.info(f"Tests run: {result.testsRun}")
    logger.info(f"Failures: {len(result.failures)}")
    logger.info(f"Errors: {len(result.errors)}")
    logger.info(f"Skipped: {len(result.skipped)}")
    
    # Detailed failure/error reporting
    if result.failures:
        logger.error("=== TEST FAILURES ===")
        for test, traceback in result.failures:
            logger.error(f"FAILED: {test}")
            logger.error(traceback)
    
    if result.errors:
        logger.error("=== TEST ERRORS ===")
        for test, traceback in result.errors:
            logger.error(f"ERROR: {test}")
            logger.error(traceback)
    
    # Return success status
    return len(result.failures) == 0 and len(result.errors) == 0

def print_banner():
    """Print test runner banner."""
    print("=" * 70)
    print("Charlie Reporting - Integration Test Suite")
    print("=" * 70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project Root: {project_root}")
    print("=" * 70)

def print_summary(success, log_file):
    """Print test run summary."""
    print("\n" + "=" * 70)
    print("Integration Test Run Summary")
    print("=" * 70)
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Status: {'SUCCESS' if success else 'FAILED'}")
    print(f"Log File: {log_file}")
    print("=" * 70)

def main():
    """Main entry point for integration test runner."""
    print_banner()
    
    # Set up logging
    log_file = setup_logging()
    logger = logging.getLogger('integration_runner')
    
    try:
        # Check prerequisites
        if not check_prerequisites():
            print("\n❌ Prerequisites check failed. See log for details.")
            return 1
        
        # Run integration tests
        success = run_integration_tests()
        
        # Print summary
        print_summary(success, log_file)
        
        if success:
            print("\n✅ All integration tests passed!")
            return 0
        else:
            print("\n❌ Some integration tests failed. See log for details.")
            return 1
    
    except KeyboardInterrupt:
        logger.warning("Integration test run interrupted by user")
        print("\n⚠️ Integration test run interrupted by user")
        return 130
    
    except Exception as e:
        logger.error(f"Unexpected error during test run: {e}")
        print(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
