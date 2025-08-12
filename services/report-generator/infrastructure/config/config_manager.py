"""
Configuration Management Implementation
Production implementation of IConfigManager interface.
"""

import asyncio
from pathlib import Path
from typing import Dict, Any
import toml

from business.interfaces import IConfigManager
from business.models.csv_data import CSVRule


class ConfigManagerImpl(IConfigManager):
    """
    Production implementation of configuration management.

    Handles:
    - TOML configuration file loading
    - Environment - specific settings
    - CSV rule parsing and validation
    - Configuration caching and reload
    """

    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path or Path("config/config.toml")
        self.config_cache: Dict[str, Any] = {}
        self.csv_rules_cache: Dict[str, CSVRule] = {}

    async def get_csv_rules(self) -> Dict[str, CSVRule]:
        """
        Load and parse CSV processing rules from configuration.

        Returns:
            Dictionary mapping rule names to CSVRule objects

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If configuration is invalid
        """
        if not self.csv_rules_cache:
            await self.load_configuration()

        return self.csv_rules_cache.copy()

    async def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get configuration setting by key.

        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        if not self.config_cache:
            await self.load_configuration()

        # Support dot notation for nested keys
        keys = key.split('.')
        value = self.config_cache

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    async def reload_configuration(self) -> None:
        """
        Force reload of configuration from file.

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If configuration is invalid
        """
        self.config_cache.clear()
        self.csv_rules_cache.clear()
        await self.load_configuration()

    async def load_configuration(self) -> None:
        """Load configuration from TOML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        loop = asyncio.get_event_loop()
        config_data = await loop.run_in_executor(
            None,
            self.load_toml_file,
            self.config_path
        )

        self.config_cache = config_data
        self.csv_rules_cache = self.parse_csv_rules(config_data)

    def load_toml_file(self, file_path: Path) -> Dict[str, Any]:
        """Load TOML file synchronously."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return toml.load(f)
        except Exception as e:
            raise ValueError(f"Invalid TOML configuration: {e}") from e

    def parse_csv_rules(self, config_data: Dict[str, Any]) -> Dict[str, CSVRule]:
        """Parse CSV rules from configuration data."""
        csv_rules = {}

        # Look for csv_rules section in config
        rules_config = config_data.get('csv_rules', {})

        for rule_name, rule_data in rules_config.items():
            try:
                csv_rule = CSVRule(
                    file_pattern=rule_data.get('pattern', '*.csv'),
                    columns=rule_data.get('columns', []),
                    sheet_name=rule_data.get('sheet_name', rule_name),
                    required_columns=rule_data.get('required_columns', [])
                )
                csv_rules[rule_name] = csv_rule

            except Exception as e:
                raise ValueError(
                    f"Invalid CSV rule '{rule_name}': {e}"
                ) from e

        return csv_rules

    async def get_database_config(self) -> Dict[str, Any]:
        """
        Get database configuration settings.

        Returns:
            Database configuration dictionary
        """
        return await self.get_setting('database', {})

    async def get_excel_config(self) -> Dict[str, Any]:
        """
        Get Excel generation configuration settings.

        Returns:
            Excel configuration dictionary
        """
        return await self.get_setting('excel', {})

    async def get_logging_config(self) -> Dict[str, Any]:
        """
        Get logging configuration settings.

        Returns:
            Logging configuration dictionary
        """
        return await self.get_setting('logging', {})
