"""Compatibility module: previous import path `shared.logging`.

Renamed to avoid shadowing the Python standard library `logging` module which broke
third-party packages expecting stdlib types.

Prefer importing from `shared.unified_logging` going forward.
"""
from shared.unified_logging import bind_request, setup_service_logging  # noqa: F401

__all__ = ["setup_service_logging", "bind_request"]
