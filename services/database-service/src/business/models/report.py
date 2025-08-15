"""Backward compatibility shim for legacy import path.

Re-exports the domain ``Report`` model to satisfy old imports.
"""
from __future__ import annotations

from ...domain.models.report import Report  # noqa: F401

__all__ = ["Report"]
