"""Application logging utilities (alias for legacy shared.logging).

Provides setup_service_logging and bind_request while avoiding the risk of
shadowing the stdlib 'logging' module when imported indirectly during
package installation.
"""
from .unified_logging import bind_request, setup_service_logging  # noqa: F401

__all__ = ["setup_service_logging", "bind_request"]
