"""
Base Configuration System
Standardized configuration management for all services
"""

from pydantic import BaseSettings, Field, validator
from typing import Dict, List, Optional, Any, Union
import os
import toml
from pathlib import Path
from enum import Enum


class Environment(str, Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class BaseServiceConfig(BaseSettings):
    """
    Base configuration class for all Charlie Reporting services.

    Provides standardized configuration structure with:
    - Environment - specific settings
    - Service discovery
    - Security configuration
    - Infrastructure settings
    """

    # === Service Identity ==
    service_name: str
    service_version: str = "1.0.0"
    environment: Environment = Field(default=Environment.DEVELOPMENT, env="ENVIRONMENT")

    # === Network Configuration ==
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(..., env="PORT")

    # === Security ==
    api_key: str = Field(..., env="API_KEY")
    allowed_origins: List[str] = ["*"]
    enable_cors: bool = True

    # === Service Discovery ==
    service_registry: Dict[str, str] = {}

    # === Infrastructure ==
    log_level: LogLevel = Field(default=LogLevel.INFO, env="LOG_LEVEL")
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")

    # === Database (Optional) ==
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    database_pool_size: int = Field(default=5, env="DATABASE_POOL_SIZE")
    database_timeout: int = Field(default=30, env="DATABASE_TIMEOUT")

    # === Messaging (Future Kafka) ==
    messaging_enabled: bool = Field(default=False, env="MESSAGING_ENABLED")
    kafka_bootstrap_servers: Optional[List[str]] = Field(default=None, env="KAFKA_BOOTSTRAP_SERVERS")
    kafka_group_id: Optional[str] = Field(default=None, env="KAFKA_GROUP_ID")

    # === File Storage ==
    storage_path: str = Field(default="./data", env="STORAGE_PATH")
    max_file_size_mb: int = Field(default=100, env="MAX_FILE_SIZE_MB")
    retention_days: int = Field(default=30, env="RETENTION_DAYS")

    # === Performance ==
    max_concurrent_requests: int = Field(default=100, env="MAX_CONCURRENT_REQUESTS")
    request_timeout: int = Field(default=30, env="REQUEST_TIMEOUT")
    retry_attempts: int = Field(default=3, env="RETRY_ATTEMPTS")

    # === Windows Specific ==
    windows_service_name: Optional[str] = None
    windows_service_display_name: Optional[str] = None
    windows_service_description: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False
        use_enum_values = True

    @validator('storage_path')
    def validate_storage_path(cls, v):
        """Ensure storage path exists"""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return str(path.absolute())

    @validator('service_registry')
    def validate_service_registry(cls, v):
        """Validate service registry URLs"""
        for service_name, url in v.items():
            if not url.startswith(('http://', 'https://')):
                raise ValueError(f"Invalid URL for service {service_name}: {url}")
        return v

    def get_service_url(self, service_name: str) -> Optional[str]:
        """Get URL for a specific service"""
        return self.service_registry.get(service_name)

    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == Environment.PRODUCTION

    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == Environment.DEVELOPMENT


class ConfigLoader:
    """
    Configuration loader that supports multiple sources:
    - TOML files (environment - specific)
    - Environment variables
    - Command line arguments (future)
    """

    @staticmethod
    def load_config(
        config_class: type,
        service_name: str,
        config_dir: str = "config",
        environment: Optional[str] = None
    ) -> BaseServiceConfig:
        """
        Load configuration from multiple sources with precedence:
        1. Environment variables (highest priority)
        2. Environment - specific TOML file
        3. Service - specific TOML file
        4. Default values (lowest priority)
        """

        # Determine environment
        env = environment or os.getenv("ENVIRONMENT", "development")

        configpath = Path(config_dir)
        configdata = {}

        # 1. Load service - specific config
        serviceconfig_file = config_path / "service.toml"
        if service_config_file.exists():
            serviceconfig = toml.load(service_config_file)
            config_data.update(service_config)

        # 2. Load environment - specific config
        envconfig_file = config_path / f"{env}.toml"
        if env_config_file.exists():
            envconfig = toml.load(env_config_file)
            config_data.update(env_config)

        # 3. Set service name and environment
        config_data.setdefault("service_name", service_name)
        config_data.setdefault("environment", env)

        # 4. Create config instance (environment variables will override)
        return config_class(**config_data)

    @staticmethod
    def create_sample_configs(service_name: str, config_dir: str = "config"):
        """Create sample configuration files for a service"""
        configpath = Path(config_dir)
        config_path.mkdir(exist_ok=True)

        # Service - specific config
        serviceconfig = {
            "service_name": service_name,
            "service_version": "1.0.0",
            "port": 8080,
            "log_level": "INFO",
            "metrics_enabled": True,
            "storage_path": "./data",
            "service_registry": {
                "outlook - relay": "http://localhost:8080",
                "data - service": "http://localhost:8081",
                "scheduler": "http://localhost:8082",
                "report - generator": "http://localhost:8083",
                "email - service": "http://localhost:8084"
            }
        }

        with open(config_path / "service.toml", "w") as f:
            toml.dump(service_config, f)

        # Development config
        devconfig = {
            "environment": "development",
            "host": "localhost",
            "log_level": "DEBUG",
            "database_url": "sqlite:///./data / charlie_dev.db",
            "api_key": "dev - api - key - 12345",
            "allowed_origins": ["*"],
            "messaging_enabled": False
        }

        with open(config_path / "development.toml", "w") as f:
            toml.dump(dev_config, f)

        # Production config template
        prodconfig = {
            "environment": "production",
            "host": "0.0.0.0",
            "log_level": "INFO",
            "database_url": "postgresql://user:pass@db - server:5432 / charlie",
            "api_key": "${API_KEY}",  # To be replaced with actual key
            "allowed_origins": ["https://company.com"],
            "messaging_enabled": True,
            "kafka_bootstrap_servers": ["kafka1:9092", "kafka2:9092"],
            "metrics_enabled": True
        }

        with open(config_path / "production.toml", "w") as f:
            toml.dump(prod_config, f)


# Service - specific config classes


class OutlookRelayConfig(BaseServiceConfig):
    """Configuration for Outlook Relay Service"""
    service_name: str = "outlook - relay"
    port: int = 8080

    # Outlook - specific settings
    outlook_profile: str = Field(default="EmailService", env="OUTLOOK_PROFILE")
    outlook_timeout: int = Field(default=30, env="OUTLOOK_TIMEOUT")
    max_attachment_size_mb: int = Field(default=100, env="MAX_ATTACHMENT_SIZE_MB")

    # Email processing
    batch_size: int = Field(default=50, env="EMAIL_BATCH_SIZE")
    archiveprocessed_emails: bool = Field(default=True, env="ARCHIVE_PROCESSED_EMAILS")


class DataServiceConfig(BaseServiceConfig):
    """Configuration for Data Service"""
    service_name: str = "data - service"
    port: int = 8081

    # Database is required for data service
    database_url: str = Field(..., env="DATABASE_URL")

    # Data processing settings
    max_batch_size: int = Field(default=1000, env="MAX_BATCH_SIZE")
    dedup_strategy: str = Field(default="strict", env="DEDUP_STRATEGY")
    enable_data_validation: bool = Field(default=True, env="ENABLE_DATA_VALIDATION")


class SchedulerConfig(BaseServiceConfig):
    """Configuration for Scheduler Service"""
    service_name: str = "scheduler"
    port: int = 8082

    # Scheduling settings
    job_store_url: Optional[str] = Field(default=None, env="JOB_STORE_URL")
    max_concurrent_jobs: int = Field(default=10, env="MAX_CONCURRENT_JOBS")
    job_timeout: int = Field(default=3600, env="JOB_TIMEOUT")  # 1 hour

    # Web dashboard
    enable_web_dashboard: bool = Field(default=True, env="ENABLE_WEB_DASHBOARD")
    dashboard_auth_required: bool = Field(default=True, env="DASHBOARD_AUTH_REQUIRED")


class ReportGeneratorConfig(BaseServiceConfig):
    """Configuration for Report Generator Service"""
    service_name: str = "report - generator"
    port: int = 8083

    # Report generation
    template_path: str = Field(default="./templates", env="TEMPLATE_PATH")
    output_path: str = Field(default="./reports", env="OUTPUT_PATH")
    max_report_size_mb: int = Field(default=50, env="MAX_REPORT_SIZE_MB")

    # File storage
    enable_cloud_storage: bool = Field(default=False, env="ENABLE_CLOUD_STORAGE")
    cloud_storage_bucket: Optional[str] = Field(default=None, env="CLOUD_STORAGE_BUCKET")


class EmailServiceConfig(BaseServiceConfig):
    """Configuration for Email Service"""
    service_name: str = "email - service"
    port: int = 8084

    # Email settings
    template_path: str = Field(default="./email_templates", env="EMAIL_TEMPLATE_PATH")
    max_recipients: int = Field(default=100, env="MAX_RECIPIENTS")
    retry_failed_emails: bool = Field(default=True, env="RETRY_FAILED_EMAILS")

    # Email delivery
    delivery_timeout: int = Field(default=60, env="DELIVERY_TIMEOUT")
    track_delivery: bool = Field(default=True, env="TRACK_DELIVERY")