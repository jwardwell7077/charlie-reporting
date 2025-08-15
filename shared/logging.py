"""Deprecated shim for backward compatibility.

Use `shared.unified_logging` (or preferably `shared.app_logging`) instead.
This file will be removed after the migration window.
"""
from .unified_logging import bind_request, setup_service_logging  # noqa: F401

__all__ = ["setup_service_logging", "bind_request"]
