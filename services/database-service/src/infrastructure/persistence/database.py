"""
Database connection infrastructure for database-service
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
        AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)
import structlog

from ...config.settings import DatabaseServiceConfig
from ...config.database import DatabaseConfig


logger = structlog.get_logger(__name__)


class DatabaseConnection:
        """
    Database connection manager for async SQLAlchemy operations.

    Provides:
    - Async engine creation and management
    - Session factory with context manager support
    - Connection health checking
    - Proper cleanup and resource management
    """

    def __init__(self, config: DatabaseServiceConfig):
            self.config = config
        self.db_config = DatabaseConfig.from_service_config(config)
            self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None

    async def create_engine(self) -> AsyncEngine:
            """Create async SQLAlchemy engine"""
        try:
            connection_params = self.db_config.to_connection_params()

                # SQLite doesn't support pooling parameters
            if 'sqlite' in connection_params['url']:
                # Remove pooling parameters for SQLite
                sqlite_params = {
                    'url': connection_params['url'],
                    'echo': connection_params['echo']
                }
                engine = create_async_engine(**sqlite_params)
                else:
                # Use all parameters for other databases
                engine = create_async_engine(**connection_params)

                logger.info(
                "Database engine created",
                url=self.db_config._mask_password(connection_params['url']),
                    pool_size=connection_params.get('pool_size', 'N/A (SQLite)')
                )

                return engine

        except Exception:
            logger.error("Failed to create database engine", error=str(e))
                raise SQLAlchemyError(f"Database engine creation failed: {e}")

        async def initialize(self) -> None:
            """Initialize database connection and session factory"""
        try:
            self._engine = await self.create_engine()
                self._session_factory = async_sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

                logger.info("Database connection initialized successfully")

            except Exception:
            logger.error("Database initialization failed", error=str(e))
                raise

    @asynccontextmanager

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
            """
        Get database session with automatic transaction management.

        Usage:
            async with db_connection.get_session() as session:
                    # Use session for database operations
                result = await session.execute(query)
                    # Session will auto-commit on successful exit
                # Session will rollback on exception
        """
        if not self._session_factory:
            raise RuntimeError("Database not initialized. Call initialize() first.")

            session = self._session_factory()
            try:
            yield session
            await session.commit()
                logger.debug("Database session committed successfully")
            except Exception:
            await session.rollback()
                logger.error("Database session rolled back", error=str(e))
                raise
        finally:
            await session.close()

        async def health_check(self) -> bool:
            """
        Check database connection health.

        Returns:
            True if database is accessible, False otherwise
        """
        if not self._engine:
            return False

        try:
            async with self._engine.begin() as conn:
                    # Simple query to test connection
                from sqlalchemy import text
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError
                await conn.execute(text("SELECT 1"))
                return True
        except Exception:
            logger.warning("Database health check failed", error=str(e))
                return False

    async def close(self) -> None:
            """Close database connection and cleanup resources"""
        if self._engine:
            await self._engine.dispose()
                logger.info("Database engine disposed")

        self._engine = None
        self._session_factory = None
