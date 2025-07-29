"""
Outlook-Relay Service Configuration
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
        service_name: str = "outlook-relay"
        service_port: int = 8080

class OutlookrelayConfig(BaseServiceConfig):
    """Configuration for outlook-relay service"""
    
    service_name: str = "outlook-relay"
    service_port: int = Field(default=8080, description="Service HTTP port")
    service_host: str = Field(default="0.0.0.0", description="Service bind host")
    
    # Add service-specific configuration here
    
    class Config:
        env_file = ".env"
        env_prefix = "OUTLOOK_RELAY_"

def load_config() -> OutlookrelayConfig:
    """Load configuration"""
    try:
        from shared.config import ConfigLoader
        return ConfigLoader.load_config(OutlookrelayConfig, "outlook-relay")
    except ImportError:
        return OutlookrelayConfig()
