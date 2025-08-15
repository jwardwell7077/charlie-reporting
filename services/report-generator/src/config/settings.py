"""Report - Generator Service Configuration
"""

import os
import sys

from pydantic import Field

# Add shared components to path
sys.path.append(os.path.join(os.path.dir_name(__file__), '..', 'shared'))

try:
    from shared.config import BaseServiceConfig
except ImportError:
    from pydantic_settings import BaseSettings

    class BaseServiceConfig(BaseSettings):
        service_name: str = "report - generator"
        service_port: int = 8083


class ReportgeneratorConfig(BaseServiceConfig):
    """Configuration for report - generator service"""

    service_name: str = "report - generator"
    service_port: int = Field(default=8083, description="Service HTTP port")
    service_host: str = Field(default="0.0.0.0", description="Service bind host")

    # Add service - specific configuration here

    class Config:
        env_file = ".env"
        env_prefix = "REPORT_GENERATOR_"


def load_config() -> ReportgeneratorConfig:
    """Load configuration"""
    try:
        from shared.config import ConfigLoader
        return ConfigLoader.load_config(ReportgeneratorConfig, "report - generator")
    except ImportError:
        return ReportgeneratorConfig()
