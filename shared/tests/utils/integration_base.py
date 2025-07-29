"""
integration_base.py
------------------
Base class for integration tests with safety checks and cleanup.

Author: Jonathan Wardwell, Copilot, GPT-4o
License: MIT
"""

import os
import unittest
import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime

from .temp_manager import IntegrationTempManager
from .email_manager import IntegrationEmailManager
from .outlook_checker import OutlookChecker
from .data_generator import IntegrationDataGenerator
from tests.config_loader_enhanced import EnhancedConfigLoader

class IntegrationTestBase(unittest.TestCase):
    """
    Base class for integration tests with comprehensive safety checks and cleanup.
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level resources."""
        cls.logger = logging.getLogger('integration_test_base')
        cls.config_loader = EnhancedConfigLoader()
        cls.config = None
        cls.temp_manager = None
        cls.email_manager = None
        cls.outlook_checker = None
        cls.data_generator = None
        cls.test_start_time = datetime.now()
        cls.test_id = f"test_{int(time.time())}"
        
        # Load integration config
        try:
            cls.config = cls.config_loader.load_integration_config()
            cls.logger.info(f"Loaded integration config for test ID: {cls.test_id}")
        except Exception as e:
            cls.logger.error(f"Failed to load integration config: {e}")
            raise
        
        # Safety check
        cls._verify_safety_requirements()
        
    @classmethod
    def _verify_safety_requirements(cls):
        """Verify all safety requirements before running tests."""
        cls.logger.info("Verifying safety requirements...")
        
        # Check if integration tests are enabled
        if not cls.config.get('integration_tests', {}).get('enabled', False):
            raise unittest.SkipTest("Integration tests are disabled in config")
        
        # Verify test email configuration
        email_config = cls.config.get('email', {})
        if not email_config.get('test_sender_address'):
            raise ValueError("Test sender email address not configured")
        
        if not email_config.get('test_receiver_address'):
            raise ValueError("Test receiver email address not configured")
        
        # Verify SMTP configuration
        smtp_config = cls.config.get('smtp', {})
        if not smtp_config.get('server'):
            raise ValueError("SMTP server not configured")
        
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
            raise ValueError(f"Missing required environment variables: {missing_vars}")
        
        cls.logger.info("Safety requirements verified")
    
    def setUp(self):
        """Set up test-specific resources."""
        self.logger.info(f"Setting up test: {self._testMethodName}")
        
        # Initialize managers
        self.temp_manager = IntegrationTempManager(self.config)
        self.email_manager = IntegrationEmailManager(self.config)
        self.outlook_checker = OutlookChecker(self.config)
        self.data_generator = IntegrationDataGenerator(self.config)
        
        # Set up temporary environment
        self.temp_dirs = self.temp_manager.setup_temp_environment()
        self.logger.info(f"Created temp environment: {self.temp_dirs}")
        
        # Test SMTP connection
        if not self.email_manager.test_smtp_connection():
            self.skipTest("SMTP connection failed")
        
        # Verify Outlook availability
        if not self.outlook_checker.verify_outlook_available():
            self.skipTest("Outlook not available")
        
        self.logger.info(f"Test setup completed: {self._testMethodName}")
    
    def tearDown(self):
        """Clean up test-specific resources."""
        self.logger.info(f"Cleaning up test: {self._testMethodName}")
        
        try:
            # Clean up test emails
            if self.outlook_checker:
                deleted_count = self.outlook_checker.delete_test_emails(
                    subject_contains=self.test_id
                )
                self.logger.info(f"Deleted {deleted_count} test emails")
            
            # Clean up temporary files
            if self.temp_manager:
                if self.temp_manager.cleanup_all():
                    self.logger.info("Temp cleanup successful")
                else:
                    self.logger.warning("Temp cleanup had issues")
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
        
        self.logger.info(f"Test cleanup completed: {self._testMethodName}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up class-level resources."""
        cls.logger.info("Class-level cleanup")
        
        # Final safety cleanup
        if hasattr(cls, 'outlook_checker') and cls.outlook_checker:
            try:
                # Delete any remaining test emails
                deleted_count = cls.outlook_checker.delete_test_emails(
                    subject_contains=cls.test_id,
                    older_than_minutes=0  # Delete all test emails regardless of age
                )
                cls.logger.info(f"Final cleanup: deleted {deleted_count} test emails")
            except Exception as e:
                cls.logger.error(f"Final email cleanup error: {e}")
    
    def get_unique_test_id(self) -> str:
        """Get unique test identifier."""
        return f"{self.test_id}_{self._testMethodName}"
    
    def create_test_email_subject(self, description: str = "") -> str:
        """Create a unique email subject for testing."""
        unique_id = self.get_unique_test_id()
        if description:
            return f"[TEST] {description} - {unique_id}"
        else:
            return f"[TEST] Integration Test - {unique_id}"
    
    def wait_for_processing(self, seconds: int = 5):
        """Wait for processing to complete."""
        self.logger.info(f"Waiting {seconds} seconds for processing...")
        time.sleep(seconds)
    
    def verify_file_exists(self, file_path: str, timeout_seconds: int = 30) -> bool:
        """
        Verify that a file exists, with timeout.
        
        Args:
            file_path: Path to file
            timeout_seconds: Maximum wait time
            
        Returns:
            bool: True if file exists within timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            if os.path.exists(file_path):
                self.logger.info(f"File found: {file_path}")
                return True
            time.sleep(1)
        
        self.logger.error(f"File not found within {timeout_seconds}s: {file_path}")
        return False
    
    def verify_file_count(self, directory: str, expected_count: int, timeout_seconds: int = 30) -> bool:
        """
        Verify file count in directory, with timeout.
        
        Args:
            directory: Directory path
            expected_count: Expected number of files
            timeout_seconds: Maximum wait time
            
        Returns:
            bool: True if count matches within timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            if os.path.exists(directory):
                file_count = len([f for f in os.listdir(directory) 
                                if os.path.isfile(os.path.join(directory, f))])
                if file_count == expected_count:
                    self.logger.info(f"File count verified: {directory} has {file_count} files")
                    return True
            time.sleep(1)
        
        actual_count = len([f for f in os.listdir(directory) 
                          if os.path.isfile(os.path.join(directory, f))]) if os.path.exists(directory) else 0
        self.logger.error(f"File count mismatch in {directory}: expected {expected_count}, got {actual_count}")
        return False
    
    def assert_email_sent_and_received(self, subject: str, timeout_seconds: int = 60) -> Dict[str, Any]:
        """
        Assert that an email was sent and received.
        
        Args:
            subject: Email subject to check
            timeout_seconds: Maximum wait time
            
        Returns:
            Dict[str, Any]: Email details if found
        """
        email_found = self.outlook_checker.wait_for_email(
            subject_contains=subject,
            timeout_seconds=timeout_seconds
        )
        
        self.assertTrue(email_found, f"Email with subject '{subject}' not received within {timeout_seconds}s")
        
        # Get email details
        email_details = self.outlook_checker.get_latest_email(subject_contains=subject)
        self.assertIsNotNone(email_details, "Could not retrieve email details")
        
        return email_details
    
    def get_config_value(self, key_path: str, default=None):
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Dot-separated key path (e.g., 'email.test_sender_address')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
