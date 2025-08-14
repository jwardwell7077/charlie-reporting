"""Clean minimal health router used by API tests."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "database-service",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
    }

