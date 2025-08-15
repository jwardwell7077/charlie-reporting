"""Configuration for the database-service (packaged)."""
from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings

try:
    from shared.config import BaseServiceConfig, ConfigLoader  # type: ignore
except Exception:  # pragma: no cover
    class BaseServiceConfig(BaseSettings):  # type: ignore
        service_name: str = "database-service"
        service_port: int = 8081

    class ConfigLoader:  # type: ignore
        @staticmethod
        def load_config(config_class, service_name: str, **_: object):
            return config_class()


class DatabaseServiceConfig(BaseServiceConfig):  # type: ignore[misc]
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

    model_config = {"env_file": ".env", "extra": "ignore"}


def load_config() -> DatabaseServiceConfig:
    return ConfigLoader.load_config(DatabaseServiceConfig, "database-service")
