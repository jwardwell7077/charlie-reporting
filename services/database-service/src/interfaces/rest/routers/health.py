"""
Health check endpoints for the database service API.
Provides service status and readiness checks.
"""

from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from ....config.settings import DatabaseServiceConfig

from datetime import datetime, timezone
router = APIRouter()


async def get_service_config() -> DatabaseServiceConfig:
        """Dependency to get service configuration"""
    return DatabaseServiceConfig()


@router.get("/", status_code=status.HTTP_200_OK)

async def health_check() -> Dict[str, Any]:
        """
    Basic health check endpoint.
    Returns service status and timestamp.
    """
    return {
        "status": "healthy",
        "service": "database-service",
        "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
    }


@router.get("/ready", status_code=status.HTTP_200_OK)

async def readiness_check(
        config: DatabaseServiceConfig = Depends(get_service_config)
) -> Dict[str, Any]:
        """
    Readiness check endpoint.
    Verifies service is ready to accept requests.
    """
    try:
        # Basic configuration check
        checks = {
            "database_configured": bool(config.database_url),
                "environment": getattr(config, 'environment', 'development'),
                "service_name": config.service_name
        }

        all_ready = all(checks.values())

            return {
            "status": "ready" if all_ready else "not_ready",
            "service": "database-service",
            "timestamp": datetime.utcnow().isoformat(),
                "checks": checks
        }

    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "service": "database-service",
                "timestamp": datetime.utcnow().isoformat(),
                    "error": str(e)
                }
        )


@router.get("/live", status_code=status.HTTP_200_OK)

async def liveness_check() -> Dict[str, Any]:
        """
    Liveness check endpoint.
    Indicates the service is running and operational.
    """
    return {
        "status": "alive",
        "service": "database-service",
        "timestamp": datetime.utcnow().isoformat()
    }
