"""Business service: MigrationService.

Placeholder for database migration domain logic (planning, validation,
progress tracking) without direct infrastructure coupling.
"""

from __future__ import annotations

import logging
from typing import Any


class MigrationService:
    """Migration orchestration domain service (placeholder)."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.logger = logger or logging.getLogger(__name__)

    # TODO: Implement business methods
    def not_implemented(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover
        self.logger.debug(
            "MigrationService.not_implemented called", extra={"args": args, "kwargs": kwargs}
        )
        raise NotImplementedError("MigrationService method not yet implemented")
