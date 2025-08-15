"""Legacy reports router (simplified).

NOTE: This module has been minimized to remove previous syntax and typing issues.
If richer functionality is required, reintroduce endpoints incrementally with tests.
"""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, Any]:
    """Return basic service health information."""
    return {"status": "ok", "service": "report-generator", "timestamp": datetime.now(UTC).isoformat()}


@router.get("/")
async def info() -> dict[str, Any]:
    """Return basic service metadata."""
    return {"service": "report-generator", "version": "2.0.0", "endpoints": ["/health"]}

