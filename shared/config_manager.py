
"""
config_loader.py
----------------
Loads and provides access to TOML-based configuration for the reporting pipeline.

Author: Jonathan Wardwell, Copilot, GPT-4o
License: MIT
"""

import tomllib
import os
from .logging_utils import LoggerFactory

class ConfigLoader:
    """
    Loads and provides access to TOML configuration for the reporting pipeline.
    Exposes sections as properties and provides compatibility with legacy config access patterns.
    """
    def __init__(self, config_path=None):
        self.logger = LoggerFactory.get_logger('config_loader', 'main.log')
        self.logger.debug("ConfigLoader.__init__: Starting initialization")
        
        if config_path is None:
            config_path = os.path.join(os.getcwd(), 'config', 'config.toml')
        self.config_path = config_path
        self.logger.debug(f"ConfigLoader.__init__: config_path={config_path}")
        
        with open(self.config_path, 'rb') as f:
            self._config = tomllib.load(f)
        self.logger.debug("ConfigLoader.__init__: Configuration loaded successfully")
        self.logger.debug("ConfigLoader.__init__: Initialization complete")

    @property
    def general(self):
        """General settings from the config (dict)."""
        return self._config.get('general', {})

    @property
    def email(self):
        """Email-related settings from the config (dict)."""
        return self._config.get('email', {})

    @property
    def output(self):
        """Output-related settings from the config (dict)."""
        return self._config.get('output', {})

    @property
    def attachments(self):
        """Attachment rules from the config (dict)."""
        return self._config.get('attachments', {})

    @property
    def directory_scan(self):
        """Directory scanning settings from the config (dict)."""
        return self._config.get('directory_scan', {})

    @property
    def global_filter(self):
        """Legacy compatibility: returns sender and subject_contains as a dict."""
        return {
            'sender': self.email.get('sender', []),
            'subject_contains': self.email.get('subject_contains', [])
        }

    @property
    def attachment_rules(self):
        """Legacy compatibility: returns dict of {filename: {'columns': [...]}}."""
        return {k: {'columns': v} for k, v in self.attachments.items()}
