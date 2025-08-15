"""Clean minimal health router used by API tests."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health_check() -> dict[str, Any]:
    return {
        "status": "healthy",
        "service": "database-service",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0.0",
    }

