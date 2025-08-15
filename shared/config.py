"""Unified configuration system (pydantic v2 compatible)."""

from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from typing import Any

import toml
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    service_name: str
    service_version: str = "1.0.0"
    environment: Environment = Environment.DEVELOPMENT

    host: str = "0.0.0.0"
    # Provide defaults to avoid strict static complaints; services override.
    port: int = 0
    api_key: str | None = None
    allowed_origins: list[str] = Field(default_factory=lambda: ["*"])
    enable_cors: bool = True
    service_registry: dict[str, str] = Field(default_factory=dict)

    log_level: LogLevel = LogLevel.INFO
    metrics_enabled: bool = True
    health_check_interval: int = 30

    database_url: str | None = None
    database_pool_size: int = 5
    database_timeout: int = 30

    messaging_enabled: bool = False
    kafka_bootstrap_servers: list[str] | None = None
    kafka_group_id: str | None = None

    storage_path: str = "./data"
    max_file_size_mb: int = 100
    retention_days: int = 30

    max_concurrent_requests: int = 100
    request_timeout: int = 30
    retry_attempts: int = 3

    windows_service_name: str | None = None
    windows_service_display_name: str | None = None
    windows_service_description: str | None = None

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    @field_validator("storage_path")
    @classmethod
    def _ensure_storage(cls, v: str) -> str:
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return str(path.absolute())

    @field_validator("service_registry")
    @classmethod
    def _validate_registry(cls, v: dict[str, str]) -> dict[str, str]:
        for name, url in v.items():
            if not url.startswith(("http://", "https://")):
                raise ValueError(f"Invalid URL for service {name}: {url}")
        return v

    def get_service_url(self, name: str) -> str | None:
        return self.service_registry.get(name)

    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION

    def is_development(self) -> bool:
        return self.environment == Environment.DEVELOPMENT


class ConfigLoader:
    """Load and scaffold service configuration from layered sources."""

    @staticmethod
    def load_config(
        config_class: type[BaseServiceConfig],
        service_name: str,
        config_dir: str = "config",
        environment: str | None = None,
    ) -> BaseServiceConfig:
        env = environment or os.getenv("ENVIRONMENT", "development")
        cfg_dir = Path(config_dir)
        # Use Any for values because TOML loader returns heterogeneous types (str, int, bool, list, dict)
        data: dict[str, Any] = {}
        sf = cfg_dir / "service.toml"
        if sf.exists():
            data.update(toml.load(sf))
        ef = cfg_dir / f"{env}.toml"
        if ef.exists():
            data.update(toml.load(ef))
        data.setdefault("service_name", service_name)
        data.setdefault("environment", env)
        return config_class(**data)

    @staticmethod
    def create_sample_configs(service_name: str, config_dir: str = "config") -> None:
        cfg_dir = Path(config_dir)
        cfg_dir.mkdir(parents=True, exist_ok=True)
        base = {
            "service_name": service_name,
            "service_version": "1.0.0",
            "port": 8080,
            "log_level": "INFO",
            "metrics_enabled": True,
            "storage_path": "./data",
            "service_registry": {
                "outlook-relay": "http://localhost:8080",
                "data-service": "http://localhost:8081",
                "scheduler": "http://localhost:8082",
                "report-generator": "http://localhost:8083",
                "email-service": "http://localhost:8084",
            },
        }
        with (cfg_dir / "service.toml").open("w") as f:
            toml.dump(base, f)
        dev = {
            "environment": "development",
            "host": "localhost",
            "log_level": "DEBUG",
            "database_url": "sqlite:///./data/charlie_dev.db",
            "api_key": "dev-api-key-12345",
            "allowed_origins": ["*"],
            "messaging_enabled": False,
        }
        with (cfg_dir / "development.toml").open("w") as f:
            toml.dump(dev, f)
        prod = {
            "environment": "production",
            "host": "0.0.0.0",
            "log_level": "INFO",
            "database_url": "postgresql://user:pass@db-server:5432/charlie",
            "api_key": "${API_KEY}",
            "allowed_origins": ["https://company.com"],
            "messaging_enabled": True,
            "kafka_bootstrap_servers": ["kafka1:9092", "kafka2:9092"],
            "metrics_enabled": True,
        }
        with (cfg_dir / "production.toml").open("w") as f:
            toml.dump(prod, f)


# Service - specific config classes


class OutlookRelayConfig(BaseServiceConfig):
    service_name: str = "outlook-relay"
    port: int = 8082
    api_key: str | None = "dev-outlook-relay-key"
    outlook_profile: str = "EmailService"
    outlook_timeout: int = 30
    max_attachment_size_mb: int = 100
    batch_size: int = 50
    archiveprocessed_emails: bool = True


class DataServiceConfig(BaseServiceConfig):
    service_name: str = "data-service"
    port: int = 8081
    api_key: str | None = "dev-data-key"
    database_url: str | None = None
    max_batch_size: int = 1000
    dedup_strategy: str = "strict"
    enable_data_validation: bool = True


class SchedulerConfig(BaseServiceConfig):
    service_name: str = "scheduler"
    port: int = 8083
    api_key: str | None = "dev-scheduler-key"
    job_store_url: str | None = None
    max_concurrent_jobs: int = 10
    job_timeout: int = 3600
    enable_web_dashboard: bool = True
    dashboard_auth_required: bool = True


class ReportGeneratorConfig(BaseServiceConfig):
    service_name: str = "report-generator"
    port: int = 8084
    api_key: str | None = "dev-report-key"
    template_path: str = "./templates"
    output_path: str = "./reports"
    max_report_size_mb: int = 50
    enable_cloud_storage: bool = False
    cloud_storage_bucket: str | None = None


class EmailServiceConfig(BaseServiceConfig):
    service_name: str = "email-service"
    port: int = 8085
    api_key: str | None = "dev-email-key"
    template_path: str = "./email_templates"
    max_recipients: int = 100
    retry_failed_emails: bool = True
    delivery_timeout: int = 60
    track_delivery: bool = True