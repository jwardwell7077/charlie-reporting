"""
Database-Service Service Configuration
"""

from pydantic import Field
import sys
import os

# Add shared components to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

try:
        from shared.config import BaseServiceConfig
except ImportError:
    from pydantic_settings import BaseSettings

    class BaseServiceConfig(BaseSettings):
            service_name: str = "database-service"
        service_port: int = 8081


class DatabaseServiceConfig(BaseServiceConfig):
        """Configuration for database-service service"""

    service_name: str = "database-service"
    service_port: int = Field(default=8081, description="Service HTTP port")
        service_host: str = Field(
        default="0.0.0.0",
        description="Service bind host"
    )

        # Database configuration
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/charlie_reporting.db",
        description="Database connection URL"
    )
        database_pool_size: int = Field(
        default=5,
        description="Database connection pool size"
    )
        database_max_overflow: int = Field(
        default=10,
        description="Database max overflow connections"
    )
        database_pool_timeout: int = Field(
        default=30,
        description="Database pool timeout in seconds"
    )
        database_echo: bool = Field(
        default=False,
        description="Enable SQLAlchemy query logging"
    )

        class Config:
        env_file = ".env"
        env_prefix = "DATABASE_SERVICE_"


def load_config() -> DatabaseServiceConfig:
        """Load configuration"""
    try:
        from shared.config import ConfigLoader
        return ConfigLoader.load_config(
            DatabaseServiceConfig, "database-service"
        )
        except ImportError:
        return DatabaseServiceConfig()
