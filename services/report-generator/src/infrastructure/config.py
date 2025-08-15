"""Configuration Management Infrastructure
Centralized configuration loading and validation
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import toml

from ..business.exceptions import ConfigurationException
from ..business.interfaces import IConfigManager


@dataclass


class ServiceConfig:
    """Service configuration model"""
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8083
    debug: bool = False
    reload: bool = False

    # Logging configuration
    log_level: str = "INFO"
    log_file: str | None = None
    enable_console_logging: bool = True
    structured_logging: bool = True

    # Processing configuration
    max_file_size_mb: int = 100
    max_files_per_request: int = 50
    processing_timeout_seconds: int = 300
    enable_file_archival: bool = True

    # Directories
    default_raw_directory: str | None = None
    default_archive_directory: str | None = None
    default_output_directory: str | None = None
    temp_directory: str | None = None

    # CSV processing
    csv_encoding: str = "utf - 8"
    csv_delimiter: str = ","
    csv_quote_char: str = '"'
    max_csv_rows: int = 1000000

    # Excel configuration
    excel_engine: str = "openpyxl"
    max_sheets_per_workbook: int = 255
    excel_date_format: str = "YYYY - MM - DD"
    excel_datetime_format: str = "YYYY - MM - DD HH:MM:SS"

    # Security
    enable_cors: bool = True
    cors_origins: list[str] = field(default_factory=lambda: ["*"])
    max_request_size_mb: int = 50

    # Monitoring
    enable_metrics: bool = True
    metrics_retention_hours: int = 24
    health_check_interval_seconds: int = 30

    # Performance
    worker_pool_size: int = 4
    memory_limit_mb: int | None = None
    enable_async_processing: bool = True


class ConfigurationManager:
    """Infrastructure service for configuration management
    Handles loading, validation, and runtime configuration updates
    """

    def __init__(self, config_file: str | Path | None = None):
        self.configfile = Path(config_file) if config_file else None
        self.config = ServiceConfig()
        self.config_loaded_at: datetime | None = None
        self.environment_overrides: dict[str, Any] = {}

        # Load configuration
        self.load_configuration()

    def load_configuration(self):
        """Load configuration from file and environment variables"""
        config_data = {}

        # Load from file if specified
        if self.config_file and self.config_file.exists():
            config_data = self.load_config_file(self.config_file)

        # Apply environment variable overrides
        envoverrides = self.load_environment_variables()
        config_data.update(env_overrides)

        # Update service configuration
        self.update_service_config(config_data)

        # Validate configuration
        self.validate_configuration()

        self.configloaded_at = datetime.utcnow()

    def load_config_file(self, config_path: Path) -> dict[str, Any]:
        """Load configuration from file (TOML or JSON)"""
        try:
            with open(config_path, encoding='utf - 8') as f:
                if config_path.suffix.lower() == '.toml':
                    return toml.load(f)
                elif config_path.suffix.lower() == '.json':
                    return json.load(f)
                else:
                    # Try TOML first, then JSON
                    content = f.read()
                    try:
                        return toml.loads(content)
                    except toml.TomlDecodeError:
                        return json.loads(content)

        except Exception as e:
            raise ConfigurationException(
                f"Failed to load configuration file: {config_path}",
                config_key="config_file",
                config_value=str(config_path)
            ) from e

    def load_environment_variables(self) -> dict[str, Any]:
        """Load configuration from environment variables"""
        envconfig = {}
        prefix = "REPORT_GENERATOR_"

        # Define environment variable mappings
        envmappings = {
            f"{prefix}HOST": ("host", str),
            f"{prefix}PORT": ("port", int),
            f"{prefix}DEBUG": ("debug", self.parse_bool),
            f"{prefix}LOG_LEVEL": ("log_level", str),
            f"{prefix}LOG_FILE": ("log_file", str),
            f"{prefix}MAX_FILE_SIZE_MB": ("max_file_size_mb", int),
            f"{prefix}MAX_FILES_PER_REQUEST": ("max_files_per_request", int),
            f"{prefix}PROCESSING_TIMEOUT": ("processing_timeout_seconds", int),
            f"{prefix}CSV_ENCODING": ("csv_encoding", str),
            f"{prefix}CSV_DELIMITER": ("csv_delimiter", str),
            f"{prefix}ENABLE_CORS": ("enable_cors", self.parse_bool),
            f"{prefix}ENABLE_METRICS": ("enable_metrics", self.parse_bool),
            f"{prefix}WORKER_POOL_SIZE": ("worker_pool_size", int),
            f"{prefix}DEFAULT_RAW_DIR": ("default_raw_directory", str),
            f"{prefix}DEFAULT_ARCHIVE_DIR": ("default_archive_directory", str),
            f"{prefix}DEFAULT_OUTPUT_DIR": ("default_output_directory", str),
        }

        # Load environment variables
        for env_var, (config_key, parser) in env_mappings.items():
            if env_var in os.environ:
                try:
                    env_config[config_key] = parser(os.environ[env_var])
                    self.environment_overrides[config_key] = os.environ[env_var]
                except (ValueError, TypeError) as e:
                    raise ConfigurationException(
                        f"Invalid value for environment variable {env_var}: {os.environ[env_var]}",
                        config_key=env_var,
                        config_value=os.environ[env_var]
                    ) from e

        return env_config

    def parse_bool(self, value: str) -> bool:
        """Parse boolean value from string"""
        if isinstance(value, bool):
            return value
        return value.lower() in ('true', '1', 'yes', 'on', 'enabled')

    def update_service_config(self, config_data: dict[str, Any]):
        """Update service configuration with loaded data"""
        for key, value in config_data.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

    def validate_configuration(self):
        """Validate the loaded configuration"""
        errors = []

        # Validate port range
        if not 1 <= self.config.port <= 65535:
            errors.append(f"Port must be between 1 and 65535, got: {self.config.port}")

        # Validate file size limits
        if self.config.max_file_size_mb <= 0:
            errors.append(f"max_file_size_mb must be positive, got: {self.config.max_file_size_mb}")

        if self.config.max_request_size_mb <= 0:
            errors.append(f"max_request_size_mb must be positive, got: {self.config.max_request_size_mb}")

        # Validate processing limits
        if self.config.max_files_per_request <= 0:
            errors.append(f"max_files_per_request must be positive, got: {self.config.max_files_per_request}")

        if self.config.processing_timeout_seconds <= 0:
            errors.append(f"processing_timeout_seconds must be positive, got: {self.config.processing_timeout_seconds}")

        # Validate log level
        validlog_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.config.log_level.upper() not in valid_log_levels:
            errors.append(f"log_level must be one of {valid_log_levels}, got: {self.config.log_level}")

        # Validate CSV settings
        if len(self.config.csv_delimiter) != 1:
            errors.append(f"csv_delimiter must be a single character, got: '{self.config.csv_delimiter}'")

        if len(self.config.csv_quote_char) != 1:
            errors.append(f"csv_quote_char must be a single character, got: '{self.config.csv_quote_char}'")

        # Validate directories if specified
        for dir_attr in ['default_raw_directory', 'default_archive_directory', 'default_output_directory']:
            dir_path = getattr(self.config, dir_attr)
            if dir_path:
                pathobj = Path(dir_path)
                if not path_obj.exists():
                    errors.append(f"{dir_attr} does not exist: {dir_path}")
                elif not path_obj.is_dir():
                    errors.append(f"{dir_attr} is not a directory: {dir_path}")

        # Validate worker pool size
        if self.config.worker_pool_size <= 0:
            errors.append(f"worker_pool_size must be positive, got: {self.config.worker_pool_size}")

        if errors:
            raise ConfigurationException(
                f"Configuration validation failed: {'; '.join(errors)}"
            )

    def get_config(self) -> ServiceConfig:
        """Get the current service configuration"""
        return self.config

    def get_config_dict(self) -> dict[str, Any]:
        """Get configuration as dictionary"""
        return {
            "host": self.config.host,
            "port": self.config.port,
            "debug": self.config.debug,
            "log_level": self.config.log_level,
            "log_file": self.config.log_file,
            "max_file_size_mb": self.config.max_file_size_mb,
            "max_files_per_request": self.config.max_files_per_request,
            "processing_timeout_seconds": self.config.processing_timeout_seconds,
            "csv_encoding": self.config.csv_encoding,
            "csv_delimiter": self.config.csv_delimiter,
            "enable_cors": self.config.enable_cors,
            "enable_metrics": self.config.enable_metrics,
            "worker_pool_size": self.config.worker_pool_size,
            "config_loaded_at": self.config_loaded_at.isoformat() if self.config_loaded_at else None,
            "environment_overrides": self.environment_overrides
        }

    def update_config(self, updates: dict[str, Any], validate: bool = True) -> dict[str, Any]:
        """Update configuration at runtime

        Args:
            updates: Dictionary of configuration updates
            validate: Whether to validate the updated configuration

        Returns:
            Dictionary with update results
        """
        originalvalues = {}
        updatedkeys = []
        errors = []

        try:
            # Store original values for rollback
            for key in updates:
                if hasattr(self.config, key):
                    original_values[key] = getattr(self.config, key)

            # Apply updates
            for key, value in updates.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                    updated_keys.append(key)
                else:
                    errors.append(f"Unknown configuration key: {key}")

            # Validate if requested
            if validate:
                self.validate_configuration()

            return {
                "success": True,
                "updated_keys": updated_keys,
                "errors": errors,
                "rollback_data": original_values
            }

        except Exception as e:
            # Rollback changes
            for key, value in original_values.items():
                setattr(self.config, key, value)

            return {
                "success": False,
                "updated_keys": [],
                "errors": errors + [str(e)],
                "rollback_data": {}
            }

    def reload_configuration(self):
        """Reload configuration from file and environment"""
        self.load_configuration()

    def get_processing_defaults(self) -> dict[str, Any]:
        """Get default values for processing operations"""
        return {
            "raw_directory": self.config.default_raw_directory,
            "archive_directory": self.config.default_archive_directory,
            "output_directory": self.config.default_output_directory,
            "csv_encoding": self.config.csv_encoding,
            "csv_delimiter": self.config.csv_delimiter,
            "max_file_size_mb": self.config.max_file_size_mb,
            "max_files_per_request": self.config.max_files_per_request,
            "processing_timeout_seconds": self.config.processing_timeout_seconds
        }

    def get_server_config(self) -> dict[str, Any]:
        """Get server - specific configuration"""
        return {
            "host": self.config.host,
            "port": self.config.port,
            "debug": self.config.debug,
            "reload": self.config.reload,
            "cors_origins": self.config.cors_origins,
            "max_request_size_mb": self.config.max_request_size_mb
        }

    def get_logging_config(self) -> dict[str, Any]:
        """Get logging - specific configuration"""
        return {
            "log_level": self.config.log_level,
            "log_file": self.config.log_file,
            "enable_console_logging": self.config.enable_console_logging,
            "structured_logging": self.config.structured_logging
        }

    def is_development_mode(self) -> bool:
        """Check if running in development mode"""
        return self.config.debug or self.config.log_level.upper() == "DEBUG"

    def get_health_info(self) -> dict[str, Any]:
        """Get configuration health information"""
        return {
            "config_file": str(self.config_file) if self.config_file else None,
            "config_loaded_at": self.config_loaded_at.isoformat() if self.config_loaded_at else None,
            "environment_overrides_count": len(self.environment_overrides),
            "is_development_mode": self.is_development_mode(),
            "config_valid": True  # If we get here, config is valid
        }


# Global configuration manager instance
config_manager: ConfigurationManager | None = None


def get_config_manager(config_file: str | Path | None = None) -> ConfigurationManager:
    """Get the global configuration manager"""
    global config_manager

    if config_manager is None:
        config_manager = ConfigurationManager(config_file)

    return config_manager


def get_config() -> ServiceConfig:
    """Get the current service configuration"""
    return get_config_manager().get_config()


class ConfigManagerImpl(IConfigManager):
    """Implementation of IConfigManager interface
    Adapter for the existing ConfigurationManager
    """

    def __init__(self):
        self.config_manager = get_config_manager()

    async def get_setting(self, key: str) -> Any:
        """Get configuration setting by key"""
        try:
            configdict = self.config_manager.get_config_dict()
            return config_dict.get(key)
        except Exception:
            return None

    async def get_all_settings(self) -> dict[str, Any]:
        """Get all configuration settings"""
        try:
            return self.config_manager.get_config_dict()
        except Exception:
            return {}

    async def update_setting(self, key: str, value: Any) -> bool:
        """Update configuration setting"""
        try:
            self.config_manager.update_config({key: value})
            return True
        except Exception:
            return False

    async def reload_config(self) -> bool:
        """Reload configuration from file"""
        try:
            self.config_manager.reload_configuration()
            return True
        except Exception:
            return False
