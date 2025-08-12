"""
Database-Service Service Configuration
"""

from typing import Optional
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



class DatabaseserviceConfig(BaseServiceConfig):
    """Configuration for database-service service"""

    service_name: str = "database-service"
    service_port: int = Field(default=8081, description="Service HTTP port")
    service_host: str = Field(default="0.0.0.0", description="Service bind host")

    # Add service-specific configuration here

    class Config:
        env_file = ".env"
        env_prefix = "DATABASE_SERVICE_"



def load_config() -> DatabaseserviceConfig:
    """Load configuration"""
    try:
        from shared.config import ConfigLoader
        return ConfigLoader.load_config(DatabaseserviceConfig, "database-service")
    except ImportError:
        return DatabaseserviceConfig()