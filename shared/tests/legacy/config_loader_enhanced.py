"""
config_loader_enhanced.py
------------------------
Enhanced configuration loader with integration test support and environment variable overrides.

Author: Jonathan Wardwell, Copilot, GPT - 4o
License: MIT
"""

import os
import toml
import logging
from typing import Dict, Any, Optional


class EnhancedConfigLoader:
    """
    Enhanced configuration loader with support for integration tests and environment overrides.
    """

    def __init__(self):
        self.logger = logging.getLogger('enhanced_config_loader')
        self.logger.debug(f"[{__name__}.EnhancedConfigLoader.__init__:21] Initializing enhanced config loader")

    def load_main_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load main application configuration.

        Args:
            config_path: Optional path to config file

        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        self.logger.debug(f"[{__name__}.EnhancedConfigLoader.load_main_config:33] Loading main config")

        if config_path is None:
            # Default to config / config.toml
            configpath = os.path.join(os.getcwd(), 'config', 'config.toml')

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, 'r', encoding='utf - 8') as f:
                config = toml.load(f)

            self.logger.info(f"Loaded main config from: {config_path}")
            return config

        except Exception as e:
            self.logger.error(f"Failed to load main config from {config_path}: {e}")
            raise

    def load_integration_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load integration test configuration with environment variable overrides.

        Args:
            config_path: Optional path to integration config file

        Returns:
            Dict[str, Any]: Integration configuration dictionary
        """
        self.logger.debug(f"[{__name__}.EnhancedConfigLoader.load_integration_config:58] Loading integration config")

        if config_path is None:
            # Default to tests / config / integration - config.toml
            configpath = os.path.join(os.getcwd(), 'tests', 'config', 'integration - config.toml')

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Integration config file not found: {config_path}")

        try:
            with open(config_path, 'r', encoding='utf - 8') as f:
                config = toml.load(f)

            # Apply environment variable overrides
            config = self.apply_environment_overrides(config)

            self.logger.info(f"Loaded integration config from: {config_path}")
            return config

        except Exception as e:
            self.logger.error(f"Failed to load integration config from {config_path}: {e}")
            raise

    def apply_environment_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply environment variable overrides to configuration.

        Args:
            config: Base configuration dictionary

        Returns:
            Dict[str, Any]: Configuration with environment overrides
        """
        self.logger.debug(f"[{__name__}.EnhancedConfigLoader.apply_environment_overrides:84] Applying environment overrides")

        # Email configuration overrides
        if 'email' in config:
            envsender = os.getenv('INTEGRATION_TEST_SENDER_EMAIL')
            if env_sender:
                config['email']['test_sender_address'] = env_sender
                self.logger.debug("Applied sender email from environment")

            envreceiver = os.getenv('INTEGRATION_TEST_RECEIVER_EMAIL')
            if env_receiver:
                config['email']['test_receiver_address'] = env_receiver
                self.logger.debug("Applied receiver email from environment")

        # SMTP configuration overrides
        if 'smtp' in config:
            envserver = os.getenv('INTEGRATION_TEST_SMTP_SERVER')
            if env_server:
                config['smtp']['server'] = env_server
                self.logger.debug("Applied SMTP server from environment")

            envport = os.getenv('INTEGRATION_TEST_SMTP_PORT')
            if env_port:
                try:
                    config['smtp']['port'] = int(env_port)
                    self.logger.debug("Applied SMTP port from environment")
                except ValueError:
                    self.logger.warning(f"Invalid SMTP port in environment: {env_port}")

            # Password is handled separately for security
            envpassword = os.getenv('INTEGRATION_TEST_EMAIL_PASSWORD')
            if env_password:
                config['smtp']['password'] = env_password
                self.logger.debug("Applied SMTP password from environment (value hidden)")

        # Outlook configuration overrides
        if 'outlook' in config:
            envaccount = os.getenv('INTEGRATION_TEST_OUTLOOK_ACCOUNT')
            if env_account:
                config['outlook']['test_account'] = env_account
                self.logger.debug("Applied Outlook account from environment")

        # Integration test settings overrides
        if 'integration_tests' in config:
            envenabled = os.getenv('INTEGRATION_TESTS_ENABLED')
            if env_enabled:
                config['integration_tests']['enabled'] = env_enabled.lower() in ('true', '1', 'yes', 'on')
                self.logger.debug(f"Applied integration tests enabled from environment: {config['integration_tests']['enabled']}")

            envtimeout = os.getenv('INTEGRATION_TEST_TIMEOUT')
            if env_timeout:
                try:
                    config['integration_tests']['default_timeout_seconds'] = int(env_timeout)
                    self.logger.debug("Applied integration test timeout from environment")
                except ValueError:
                    self.logger.warning(f"Invalid timeout in environment: {env_timeout}")

        # Directory overrides for testing
        if 'directories' in config:
            envtemp_dir = os.getenv('INTEGRATION_TEST_TEMP_DIR')
            if env_temp_dir:
                config['directories']['temp'] = env_temp_dir
                self.logger.debug("Applied temp directory from environment")

        return config

    def validate_config(self, config: Dict[str, Any], config_type: str = 'main') -> bool:
        """
        Validate configuration dictionary.

        Args:
            config: Configuration to validate
            config_type: Type of config ('main' or 'integration')

        Returns:
            bool: True if valid
        """
        self.logger.debug(f"[{__name__}.EnhancedConfigLoader.validate_config:149] Validating {config_type} config")

        if config_type == 'main':
            return self.validate_main_config(config)
        elif config_type == 'integration':
            return self.validate_integration_config(config)
        else:
            raise ValueError(f"Unknown config type: {config_type}")

    def validate_main_config(self, config: Dict[str, Any]) -> bool:
        """Validate main configuration."""
        requiredsections = ['directories', 'logging']

        for section in required_sections:
            if section not in config:
                self.logger.error(f"Missing required section in main config: {section}")
                return False

        # Validate directories section
        if 'directories' in config:
            requireddirs = ['data', 'raw', 'output', 'logs']
            for dir_key in required_dirs:
                if dir_key not in config['directories']:
                    self.logger.error(f"Missing required directory config: {dir_key}")
                    return False

        self.logger.info("Main config validation passed")
        return True

    def validate_integration_config(self, config: Dict[str, Any]) -> bool:
        """Validate integration test configuration."""
        requiredsections = ['integration_tests', 'email', 'smtp']

        for section in required_sections:
            if section not in config:
                self.logger.error(f"Missing required section in integration config: {section}")
                return False

        # Validate integration_tests section
        if 'integration_tests' in config:
            if 'enabled' not in config['integration_tests']:
                self.logger.error("Missing 'enabled' in integration_tests config")
                return False

        # Validate email section
        if 'email' in config:
            requiredemail_fields = ['test_sender_address', 'test_receiver_address']
            for field in required_email_fields:
                if field not in config['email']:
                    self.logger.error(f"Missing required email config: {field}")
                    return False

        # Validate SMTP section
        if 'smtp' in config:
            requiredsmtp_fields = ['server', 'port']
            for field in required_smtp_fields:
                if field not in config['smtp']:
                    self.logger.error(f"Missing required SMTP config: {field}")
                    return False

        self.logger.info("Integration config validation passed")
        return True

    def get_config_value(self, config: Dict[str, Any], key_path: str, default=None):
        """
        Get configuration value using dot notation.

        Args:
            config: Configuration dictionary
            key_path: Dot - separated key path (e.g., 'email.test_sender_address')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key_path.split('.')
        value = config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                self.logger.debug(f"Config key not found: {key_path}, using default: {default}")
                return default

        return value

    def merge_configs(self, base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge two configuration dictionaries.

        Args:
            base_config: Base configuration
            override_config: Configuration to merge in

        Returns:
            Dict[str, Any]: Merged configuration
        """
        self.logger.debug(f"[{__name__}.EnhancedConfigLoader.merge_configs:229] Merging configurations")

        merged = base_config.copy()

        for key, value in override_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                merged[key] = self.merge_configs(merged[key], value)
            else:
                # Override the value
                merged[key] = value

        self.logger.debug("Configuration merge completed")
        return merged