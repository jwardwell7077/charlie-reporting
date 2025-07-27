import tomllib
import os

class ConfigLoader:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(os.getcwd(), 'config', 'config.toml')
        self.config_path = config_path
        with open(self.config_path, 'rb') as f:
            self._config = tomllib.load(f)

    @property
    def general(self):
        return self._config.get('general', {})

    @property
    def email(self):
        return self._config.get('email', {})

    @property
    def output(self):
        return self._config.get('output', {})

    @property
    def attachments(self):
        return self._config.get('attachments', {})

    @property
    def global_filter(self):
        # For compatibility with old code
        return {
            'sender': self.email.get('sender', []),
            'subject_contains': self.email.get('subject_contains', [])
        }

    @property
    def attachment_rules(self):
        # For compatibility with old code
        # Returns dict of {filename: {'columns': [...]}}
        return {k: {'columns': v} for k, v in self.attachments.items()}
