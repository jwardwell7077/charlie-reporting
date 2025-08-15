"""
Unit tests for database connection infrastructure.
Following TDD - these tests are written BEFORE implementation.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy.exc import SQLAlchemyError

from src.infrastructure.persistence.database import DatabaseConnection
from src.config.settings import DatabaseServiceConfig


class TestDatabaseConnection:
    """Test database connection management"""
    
    @pytest.fixture
    def config(self):
        """Test configuration"""
        return DatabaseServiceConfig(
            database_url="sqlite+aiosqlite:///:memory:",
            database_pool_size=5,
            database_max_overflow=10,
            database_pool_timeout=30
        )
    
    @pytest.fixture
    def db_connection(self, config):
        """Database connection instance"""
        return DatabaseConnection(config)
    
    @pytest.mark.asyncio
    async def test_create_engine_with_sqlite(self, db_connection):
        """Test engine creation with SQLite URL"""
        engine = await db_connection.create_engine()
        
        assert engine is not None
        assert isinstance(engine, AsyncEngine)
        assert "sqlite+aiosqlite" in str(engine.url)
        
        await engine.dispose()
    
    @pytest.mark.asyncio
    async def test_create_engine_with_postgresql(self, config):
        """Test engine creation with PostgreSQL URL"""
        config.database_url = "postgresql+asyncpg://user:pass@localhost/testdb"
        db_connection = DatabaseConnection(config)
        
        # Mock asyncpg connection since we don't have real DB
        with patch('src.infrastructure.persistence.database.create_async_engine') as mock_create:
            mock_engine = AsyncMock()
            mock_create.return_value = mock_engine
            
            engine = await db_connection.create_engine()
            
            assert engine is not None
            mock_create.assert_called_once()
            # Verify PostgreSQL gets full connection params (not SQLite-stripped)
            call_kwargs = mock_create.call_args[1]
            assert 'pool_size' in call_kwargs
            assert 'max_overflow' in call_kwargs
    
    @pytest.mark.asyncio
    async def test_get_session_returns_async_session(self, db_connection):
        """Test session creation returns AsyncSession"""
        await db_connection.initialize()
        
        async with db_connection.get_session() as session:
            assert isinstance(session, AsyncSession)
            assert session.bind is not None
    
    @pytest.mark.asyncio
    async def test_session_context_manager_auto_commits(self, db_connection):
        """Test session auto-commits on successful exit"""
        await db_connection.initialize()
        
        # Mock session to verify commit is called
        with patch.object(db_connection, '_session_factory') as mock_factory:
            mock_session = AsyncMock()
            mock_factory.return_value = mock_session
            
            async with db_connection.get_session() as session:
                pass  # Normal exit should trigger commit
            
            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_session_context_manager_rollback_on_exception(self, db_connection):
        """Test session rolls back on exception"""
        await db_connection.initialize()
        
        with patch.object(db_connection, '_session_factory') as mock_factory:
            mock_session = AsyncMock()
            mock_factory.return_value = mock_session
            
            with pytest.raises(ValueError):
                async with db_connection.get_session() as session:
                    raise ValueError("Test exception")
            
            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check_with_healthy_connection(self, db_connection):
        """Test health check returns True for healthy connection"""
        await db_connection.initialize()
        
        is_healthy = await db_connection.health_check()
        
        assert is_healthy is True
    
    @pytest.mark.asyncio
    async def test_health_check_with_failed_connection(self, db_connection):
        """Test health check returns False for failed connection"""
        # Don't initialize connection to simulate failure
        
        is_healthy = await db_connection.health_check()
        
        assert is_healthy is False
    
    @pytest.mark.asyncio
    async def test_initialize_creates_engine_and_session_factory(self, db_connection):
        """Test initialization creates required components"""
        await db_connection.initialize()
        
        assert db_connection._engine is not None
        assert db_connection._session_factory is not None
    
    @pytest.mark.asyncio
    async def test_close_disposes_engine(self, db_connection):
        """Test close properly disposes of engine"""
        await db_connection.initialize()
        engine = db_connection._engine
        
        await db_connection.close()
        
        # Verify engine was disposed (can't test directly, but ensure it's called)
        assert db_connection._engine is None
        assert db_connection._session_factory is None
    
    @pytest.mark.asyncio
    async def test_connection_pool_configuration(self, config):
        """Test connection pool is configured correctly"""
        config.database_pool_size = 15
        config.database_max_overflow = 20
        # Use PostgreSQL URL to test pooling (SQLite doesn't use pool params)
        config.database_url = "postgresql+asyncpg://user:pass@localhost/testdb"
        
        db_connection = DatabaseConnection(config)
        
        with patch('src.infrastructure.persistence.database.create_async_engine') as mock_create:
            mock_engine = AsyncMock()
            mock_create.return_value = mock_engine
            
            await db_connection.create_engine()
            
            # Verify pool configuration was passed
            call_kwargs = mock_create.call_args[1]
            assert call_kwargs['pool_size'] == 15
            assert call_kwargs['max_overflow'] == 20
    
    @pytest.mark.asyncio
    async def test_connection_timeout_configuration(self, config):
        """Test connection timeout is configured"""
        config.database_pool_timeout = 45
        # Use PostgreSQL URL to test pooling (SQLite doesn't use pool params)
        config.database_url = "postgresql+asyncpg://user:pass@localhost/testdb"
        
        db_connection = DatabaseConnection(config)
        
        with patch('src.infrastructure.persistence.database.create_async_engine') as mock_create:
            mock_engine = AsyncMock()
            mock_create.return_value = mock_engine
            
            await db_connection.create_engine()
            
            call_kwargs = mock_create.call_args[1]
            assert call_kwargs['pool_timeout'] == 45
    
    @pytest.mark.asyncio
    async def test_concurrent_session_usage(self, db_connection):
        """Test multiple concurrent sessions work correctly"""
        await db_connection.initialize()
        
        async def use_session(session_id: int):
            async with db_connection.get_session() as session:
                # Simulate some work
                await asyncio.sleep(0.01)
                return session_id
        
        # Run multiple sessions concurrently
        tasks = [use_session(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        assert results == [0, 1, 2, 3, 4]
    
    @pytest.mark.asyncio
    async def test_invalid_database_url_raises_error(self):
        """Test invalid database URL raises appropriate error"""
        config = DatabaseServiceConfig(database_url="invalid://url")
        db_connection = DatabaseConnection(config)
        
        with pytest.raises(SQLAlchemyError):
            await db_connection.initialize()
