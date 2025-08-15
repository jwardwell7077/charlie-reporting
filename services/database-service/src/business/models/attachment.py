"""Backward compatibility shim for legacy import path.

The domain models were migrated to ``src/domain/models``. Older code (or
in‑flight branches) may still import from
``business.models.attachment``. This module re-exports the new
Pydantic model so those imports continue to function while the codebase
is refactored.
"""
from __future__ import annotations

from ...domain.models.attachment import Attachment  # noqa: F401

__all__ = ["Attachment"]
