"""Simple project logging configuration.

Usage:
    from shared.service_logging import configure_logging, get_logger

    configure_logging()  # once at startup (idempotent)
    log = get_logger(__name__)
    log.info("Something happened")

Keep this intentionally tiny: stdlib only, no structlog, no custom classes.
Avoid name 'logging.py' to prevent shadowing stdlib logging.
"""
from __future__ import annotations

import logging
import os

_LOGGING_CONFIGURED = False


def configure_logging(level: str | int | None = None) -> None:
    """Configure root logger once.

    level: str|int - logging level (default INFO). Subsequent calls are no-ops.
    """
    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        return
    root = logging.getLogger()
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO")
    lvl = level
    if isinstance(lvl, str):
        lvl = getattr(logging, lvl.upper(), logging.INFO)
    elif lvl is None:
        lvl = logging.INFO
    root.setLevel(lvl)
    if not root.handlers:
        fmt = "%(asctime)s %(levelname)s %(name)s - %(message)s"
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(fmt))
        root.addHandler(handler)
    _LOGGING_CONFIGURED = True


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a module/service logger (configure if needed)."""
    if not _LOGGING_CONFIGURED:
        configure_logging()
    return logging.getLogger(name)


def set_level(level: str | int) -> None:
    """Dynamically adjust root log level."""
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    logging.getLogger().setLevel(level)


__all__ = ["configure_logging", "get_logger", "set_level"]
