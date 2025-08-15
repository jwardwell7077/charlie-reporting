"""Configuration for the database-service (clean post-merge)."""
from __future__ import annotations

import os
import sys

from pydantic import Field

_shared_path = os.path.join(os.path.dirname(__file__), "..", "shared")
if _shared_path not in sys.path:
    sys.path.append(_shared_path)

try:
    from shared.config import BaseServiceConfig  # type: ignore
except ImportError:
    from pydantic_settings import BaseSettings as BaseServiceConfig  # type: ignore


class _BaseServiceConfig(BaseServiceConfig):  # type: ignore[misc]
    service_name: str = "database-service"
    service_port: int = 8081


class DatabaseServiceConfig(_BaseServiceConfig):  # type: ignore[misc]
    """Service configuration including database connectivity."""

    service_name: str = "database-service"
    service_port: int = Field(default=8081, description="Service HTTP port")
    service_host: str = Field(default="0.0.0.0", description="Service bind host")

    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/charlie_reporting.db",
        description="Database connection URL",
    )
    database_pool_size: int = Field(default=5, description="DB pool size")
    database_max_overflow: int = Field(
        default=10, description="DB max overflow connections"
    )
    database_pool_timeout: int = Field(
        default=30, description="Database pool timeout (s)"
    )
    database_echo: bool = Field(
        default=False, description="Enable SQLAlchemy query logging"
    )

    class Config:  # type: ignore[override]
        env_file = ".env"
        env_prefix = "DATABASE_SERVICE_"


def load_config() -> DatabaseServiceConfig:
    """Load configuration using shared loader if available; else direct instantiation."""
    try:
        from shared.config import ConfigLoader  # type: ignore
        return ConfigLoader.load_config(DatabaseServiceConfig, "database-service")
    except Exception:  # pragma: no cover
        return DatabaseServiceConfig()
