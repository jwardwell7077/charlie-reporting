"""Filename utilities for simulator."""
from __future__ import annotations

from datetime import UTC, datetime


def truncate_5(dt: datetime) -> datetime:
    """Return datetime truncated down to nearest 5-minute boundary (UTC)."""
    dt = dt.astimezone(UTC)
    minute = (dt.minute // 5) * 5
    return dt.replace(minute=minute, second=0, microsecond=0)


def dataset_filename(dataset: str, dt: datetime) -> str:
    """Return canonical dataset filename for truncated timestamp."""
    t = truncate_5(dt)
    return f"{dataset}__{t.strftime('%Y-%m-%d_%H%M')}.csv"

__all__ = ["truncate_5", "dataset_filename"]
