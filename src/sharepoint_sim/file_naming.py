"""Filename utilities for simulator."""
from __future__ import annotations

from datetime import datetime, timezone


def truncate_5(dt: datetime) -> datetime:
    dt = dt.astimezone(timezone.utc)
    minute = (dt.minute // 5) * 5
    return dt.replace(minute=minute, second=0, microsecond=0)


def dataset_filename(dataset: str, dt: datetime) -> str:
    t = truncate_5(dt)
    return f"{dataset}__{t.strftime('%Y-%m-%d_%H%M')}.csv"

__all__ = ["truncate_5", "dataset_filename"]
