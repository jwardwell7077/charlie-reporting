"""Backward compatibility shim for legacy import path.

Re-exports the new domain-level ``EmailRecord`` model.
"""
from __future__ import annotations

from ...domain.models.email_record import EmailRecord  # noqa: F401

__all__ = ["EmailRecord"]
