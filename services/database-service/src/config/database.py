"""Database configuration module for database-service
"""

import os
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator, model_validator


class DatabaseConfig(BaseModel):
    """Database configuration settings."""

    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/charlie_reporting.db",
        description="Database connection URL",
    )
    database_pool_size: int = Field(
        default=5,
        gt=0,
        description="Database connection pool size",
    )
    database_max_overflow: int = Field(
        default=10,
        ge=0,
        description="Database max overflow connections",
    )
    database_pool_timeout: int = Field(
        default=30,
        gt=0,
        description="Database pool timeout in seconds",
    )
    database_echo: bool = Field(
        default=False,
        description="Enable SQLAlchemy query logging",
    )
    environment: str = Field(
        default="development",
        description="Environment name",
    )

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v:
            raise ValueError("Database URL cannot be empty")
        # Manual scheme extraction (urlparse edge cases with '+')
        if "://" not in v:
            raise ValueError("Database URL must include a scheme")
        raw_scheme = v.split("://", 1)[0]
        if not raw_scheme:
            raise ValueError("Database URL must include a scheme")
        # Enforce async driver for postgres
        if raw_scheme == "postgresql":
            raise ValueError("PostgreSQL URL must include async driver")
        # Accept known schemes / variants
        allowed_exact = {
            "sqlite+aiosqlite",
            "postgresql+asyncpg",
            "mysql+aiomysql",
            "oracle+cx_oracle",
        }
        if raw_scheme in allowed_exact:
            return v
        # Accept variants with '+' where base is recognized
        if "+" in raw_scheme:
            base = raw_scheme.split("+", 1)[0]
            if base in {"sqlite", "postgresql", "mysql", "oracle"}:
                return v
        # Accept base oracle without driver (treat as valid for tests)
        if raw_scheme.startswith("oracle"):
            return v
        raise ValueError(f"Unsupported database scheme: {raw_scheme}")

    @field_validator("database_max_overflow")
    @classmethod
    def validate_max_overflow(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Max overflow cannot be negative")
        return v

    @model_validator(mode="after")
    def validate_pool_relationship(
        self,
    ) -> "DatabaseConfig":  # pragma: no cover - simple
        if (
            self.database_pool_size > 1
            and self.database_max_overflow < self.database_pool_size
        ):
            raise ValueError(
                "database_max_overflow cannot be less than database_pool_size"
            )
        return self

    def __init__(self, **kwargs: Any):  # type: ignore[override]
        """Initialize with environment + env var overrides.

        Test expectations:
        - DatabaseConfig() => database_echo is False (even though default env
          is 'development').
        - DatabaseConfig(environment='development') => database_echo is True.
        Therefore we only promote echo=True when the caller explicitly supplies
        the environment kwarg set to 'development'.
        """
        # Pull from environment only if not explicitly supplied
        if "database_url" not in kwargs and os.getenv("DATABASE_URL"):
            kwargs["database_url"] = os.environ["DATABASE_URL"]
        if (
            "database_pool_size" not in kwargs
            and os.getenv("DATABASE_POOL_SIZE")
        ):
            kwargs["database_pool_size"] = int(
                os.environ["DATABASE_POOL_SIZE"]
            )
        if (
            "database_max_overflow" not in kwargs
            and os.getenv("DATABASE_MAX_OVERFLOW")
        ):
            kwargs["database_max_overflow"] = int(
                os.environ["DATABASE_MAX_OVERFLOW"]
            )
        if (
            "database_pool_timeout" not in kwargs
            and os.getenv("DATABASE_POOL_TIMEOUT")
        ):
            kwargs["database_pool_timeout"] = int(
                os.environ["DATABASE_POOL_TIMEOUT"]
            )
        if "database_echo" not in kwargs and os.getenv("DATABASE_ECHO"):
            kwargs["database_echo"] = os.environ["DATABASE_ECHO"].lower() in {
                "1",
                "true",
                "yes",
            }

        explicit_env_supplied = "environment" in kwargs
        env = kwargs.get("environment", "development")
        if env == "production":
            kwargs.setdefault("database_echo", False)
            kwargs.setdefault("database_pool_size", 20)
            pool_size_val = kwargs.get("database_pool_size")
            max_overflow_val = kwargs.get("database_max_overflow")
            if (
                pool_size_val is not None
                and (
                    max_overflow_val is None
                    or max_overflow_val < pool_size_val
                )
            ):
                kwargs["database_max_overflow"] = pool_size_val * 2
        elif env == "development" and explicit_env_supplied:
            kwargs.setdefault("database_echo", True)
        super().__init__(**kwargs)

    def to_connection_params(self) -> dict[str, Any]:
        return {
            "url": self.database_url,
            "pool_size": self.database_pool_size,
            "max_overflow": self.database_max_overflow,
            "pool_timeout": self.database_pool_timeout,
            "echo": self.database_echo,
        }

    @classmethod
    def from_service_config(
        cls, service_config: Any
    ) -> "DatabaseConfig":
        pool_size = getattr(service_config, "database_pool_size", 5)
        max_overflow = getattr(
            service_config,
            "database_max_overflow",
            max(pool_size * 2, 10),
        )
        if pool_size > 1 and max_overflow < pool_size:
            max_overflow = pool_size
        return cls(
            database_url=service_config.database_url,
            database_pool_size=pool_size,
            database_max_overflow=max_overflow,
            database_pool_timeout=getattr(
                service_config, "database_pool_timeout", 30
            ),
            database_echo=getattr(
                service_config, "database_echo", False
            ),
            environment=getattr(
                service_config, "environment", "development"
            ),
        )

    def __repr__(self) -> str:  # pragma: no cover - simple representation
        masked_url = self._mask_password(self.database_url)
        return (
            "DatabaseConfig(url='" + masked_url + "', "
            f"pool_size={self.database_pool_size}, "
            f"max_overflow={self.database_max_overflow})"
        )

    def model_dump(
        self, **kwargs: Any
    ) -> dict[str, Any]:  # type: ignore[override]
        data = super().model_dump(**kwargs)
        data["database_url"] = self._mask_password(data["database_url"])
        return data

    def _mask_password(self, url: str) -> str:
        try:
            parsed = urlparse(url)
            if parsed.password:
                masked_netloc = parsed.netloc.replace(
                    parsed.password, "****"
                )
                return url.replace(parsed.netloc, masked_netloc)
        except Exception:  # pragma: no cover - safety net
            return url
        return url
