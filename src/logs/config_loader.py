import yaml


class ConfigLoader:
    """
    ConfigLoader loads and provides access to global email filters and attachment rules from a YAML file.
    """
    def __init__(self, path: str):
        """Initialize the loader and parse the YAML config."""
        with open(path, 'r') as f:
            self._cfg = yaml.safe_load(f)

    @property
    def global_filter(self) -> dict:
        """Return the global email filtering settings."""
        return self._cfg.get('global_email_filter', {}) or {}

    @property
    def attachment_rules(self) -> dict:
        """Return the per-attachment matching rules."""
        return self._cfg.get('attachments', {}) or {}
