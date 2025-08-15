from __future__ import annotations

import logging
import os
import sys
import time
from typing import Any

try:  # pragma: no cover
    import structlog  # type: ignore
except Exception:  # noqa: BLE001
    structlog = None  # type: ignore

DEFAULT_PROCESSORS: list[Any] = []
if structlog is not None:
    DEFAULT_PROCESSORS = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]


def _configure_once(force: bool = False) -> None:
    if getattr(_configure_once, "_configured", False) and not force:
        return
    if structlog is not None:
        rich_console = sys.stderr.isatty()
        processors = list(DEFAULT_PROCESSORS)
        if rich_console:
            processors.append(structlog.dev.ConsoleRenderer(colors=True))
        else:
            processors.append(structlog.processors.JSONRenderer())
        structlog.configure(
            processors=processors,
            wrapper_class=structlog.make_filtering_bound_logger(logging.getLogger().level),
            cache_logger_on_first_use=True,
        )
    _configure_once._configured = True  # type: ignore[attr-defined]


def setup_service_logging(service_name: str, level: str | int | None = None, **initial: Any):
    root = logging.getLogger()
    if level is not None:
        root.setLevel(level if isinstance(level, int) else str(level).upper())
    if not root.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        root.addHandler(handler)
    if structlog is not None:
        _configure_once()
        return structlog.get_logger(service=service_name, pid=os.getpid(), **initial)
    return logging.getLogger(service_name)


def bind_request(logger, request_id: str | None = None, **extra: Any):  # pragma: no cover
    if structlog is None:
        return logger
    if request_id is None:
        request_id = hex(int(time.time() * 1000))
    return logger.bind(request_id=request_id, **extra)


__all__ = ["setup_service_logging", "bind_request"]
