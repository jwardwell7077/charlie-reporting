"""Database connection infrastructure for database-service.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ...config.database import DatabaseConfig
from ...config.settings import DatabaseServiceConfig

logger = structlog.get_logger(__name__)


class DatabaseConnection:
    """Manage async SQLAlchemy engine and sessions."""

    def __init__(self, config: DatabaseServiceConfig):
        self.config = config
        try:
            self.db_config = DatabaseConfig.from_service_config(config)
        except ValidationError as e:
            # Defer raising until initialize()
            self._init_error = e
            self.db_config = None  # type: ignore[assignment]
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    async def create_engine(self) -> AsyncEngine:
        """Create and return an async SQLAlchemy engine.

        For SQLite URLs remove pooling parameters.
        """
        try:
            connection_params = (
                self.db_config.to_connection_params()  # type: ignore[union-attr]
            )
            url = connection_params["url"]
            if "sqlite" in url:
                engine = create_async_engine(
                    url, echo=connection_params.get("echo", False)
                )
            else:
                engine = create_async_engine(
                    url,
                    echo=connection_params.get("echo", False),
                    pool_size=connection_params.get("pool_size"),
                    max_overflow=connection_params.get("max_overflow"),
                    pool_timeout=connection_params.get("pool_timeout"),
                )
            logger.info(
                "Database engine created",
                url=self.db_config._mask_password(  # type: ignore[union-attr]
                    url
                ),
            )
            return engine
        except Exception as e:  # noqa: BLE001
            logger.error("Failed to create database engine", error=str(e))
            raise SQLAlchemyError(f"Database engine creation failed: {e}")

    async def initialize(self) -> None:
        if getattr(self, "_init_error", None):
            raise SQLAlchemyError(str(self._init_error))
        if self._engine is None:
            self._engine = await self.create_engine()
            self._session_factory = async_sessionmaker(
                bind=self._engine, class_=AsyncSession, expire_on_commit=False
            )
            logger.info("Database connection initialized successfully")

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Yield an AsyncSession with automatic commit/rollback."""
        if not self._session_factory:
            raise RuntimeError(
                "Database not initialized. Call initialize() first."
            )
        session: AsyncSession = self._session_factory()
        try:
            yield session
            await session.commit()
            logger.debug("Database session committed successfully")
        except Exception as e:  # noqa: BLE001
            await session.rollback()
            logger.error("Database session rolled back", error=str(e))
            raise
        finally:
            await session.close()

    async def health_check(self) -> bool:
        """Return True if a simple SELECT 1 succeeds."""
        if not self._engine:
            return False
        try:
            async with self._engine.begin() as conn:  # type: ignore[arg-type]
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as e:  # noqa: BLE001
            logger.warning("Database health check failed", error=str(e))
            return False

    async def close(self) -> None:
        """Dispose engine and reset session factory."""
        if self._engine:
            await self._engine.dispose()
            logger.info("Database engine disposed")
        self._engine = None
        self._session_factory = None
