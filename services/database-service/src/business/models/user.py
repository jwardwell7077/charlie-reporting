"""Backward compatibility shim for legacy import path.

Re-exports the domain ``User`` model.
"""
from __future__ import annotations

from ...domain.models.user import User  # noqa: F401

__all__ = ["User"]
