"""
Unit tests for database service configuration.
Following TDD - these tests are written BEFORE implementation.
"""

import pytest
import os
from unittest.mock import patch, mock_open
from pydantic import ValidationError

from src.config.database import DatabaseConfig
from src.config.settings import DatabaseServiceConfig


class TestDatabaseConfig:
    """Test database configuration management"""
    
    def test_default_sqlite_configuration(self):
        """Test default configuration uses SQLite"""
        config = DatabaseConfig()
        
        assert config.database_url == "sqlite+aiosqlite:///./data/charlie_reporting.db"
        assert config.database_pool_size == 5
        assert config.database_max_overflow == 10
        assert config.database_pool_timeout == 30
        assert config.database_echo is False
    
    def test_postgresql_configuration_from_env(self):
        """Test PostgreSQL configuration from environment variables"""
        env_vars = {
            'DATABASE_URL': 'postgresql+asyncpg://user:pass@localhost:5432/charlie_db',
            'DATABASE_POOL_SIZE': '20',
            'DATABASE_MAX_OVERFLOW': '30',
            'DATABASE_POOL_TIMEOUT': '60',
            'DATABASE_ECHO': 'true'
        }
        
        with patch.dict(os.environ, env_vars):
            config = DatabaseConfig()
            
            assert config.database_url == 'postgresql+asyncpg://user:pass@localhost:5432/charlie_db'
            assert config.database_pool_size == 20
            assert config.database_max_overflow == 30
            assert config.database_pool_timeout == 60
            assert config.database_echo is True
    
    def test_mysql_configuration_validation(self):
        """Test MySQL configuration is accepted"""
        config = DatabaseConfig(
            database_url="mysql+aiomysql://user:pass@localhost:3306/charlie_db"
        )
        
        assert "mysql+aiomysql" in config.database_url
    
    def test_invalid_database_url_validation(self):
        """Test invalid database URL raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            DatabaseConfig(database_url="invalid_url_format")
        
        assert "database_url" in str(exc_info.value)
    
    def test_negative_pool_size_validation(self):
        """Test negative pool size raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            DatabaseConfig(database_pool_size=-1)
        
        assert "database_pool_size" in str(exc_info.value)
    
    def test_zero_pool_size_validation(self):
        """Test zero pool size raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            DatabaseConfig(database_pool_size=0)
        
        assert "database_pool_size" in str(exc_info.value)
    
    def test_negative_max_overflow_validation(self):
        """Test negative max overflow raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            DatabaseConfig(database_max_overflow=-1)
        
        assert "database_max_overflow" in str(exc_info.value)
    
    def test_negative_timeout_validation(self):
        """Test negative timeout raises validation error"""
        with pytest.raises(ValidationError) as exc_info:
            DatabaseConfig(database_pool_timeout=-1)
        
        assert "database_pool_timeout" in str(exc_info.value)
    
    def test_config_to_connection_params(self):
        """Test conversion to SQLAlchemy connection parameters"""
        config = DatabaseConfig(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/testdb",
            database_pool_size=15,
            database_max_overflow=25,
            database_pool_timeout=45,
            database_echo=True
        )
        
        params = config.to_connection_params()
        
        expected = {
            'url': 'postgresql+asyncpg://user:pass@localhost:5432/testdb',
            'pool_size': 15,
            'max_overflow': 25,
            'pool_timeout': 45,
            'echo': True
        }
        
        assert params == expected
    
    def test_sqlite_memory_database_configuration(self):
        """Test SQLite in-memory database configuration"""
        config = DatabaseConfig(
            database_url="sqlite+aiosqlite:///:memory:"
        )
        
        assert config.database_url == "sqlite+aiosqlite:///:memory:"
        
        # In-memory SQLite should have different pool settings
        params = config.to_connection_params()
        assert params['url'] == "sqlite+aiosqlite:///:memory:"
    
    def test_development_vs_production_defaults(self):
        """Test different defaults for development vs production"""
        # Development config
        dev_config = DatabaseConfig(environment="development")
        assert dev_config.database_echo is True  # More verbose in dev
        assert dev_config.database_pool_size == 5  # Smaller pool in dev
        
        # Production config
        prod_config = DatabaseConfig(environment="production")
        assert prod_config.database_echo is False  # Less verbose in prod
        assert prod_config.database_pool_size == 20  # Larger pool in prod
    
    def test_database_config_integration_with_service_config(self):
        """Test database config integrates with main service config"""
        service_config = DatabaseServiceConfig(
            database_url="postgresql+asyncpg://user:pass@localhost:5432/integration_test",
            database_pool_size=12
        )
        
        db_config = DatabaseConfig.from_service_config(service_config)
        
        assert db_config.database_url == service_config.database_url
        assert db_config.database_pool_size == 12
    
    def test_config_repr_masks_password(self):
        """Test configuration repr masks database password"""
        config = DatabaseConfig(
            database_url="postgresql+asyncpg://user:secretpass@localhost:5432/testdb"
        )
        
        repr_str = repr(config)
        
        assert "secretpass" not in repr_str
        assert "***" in repr_str or "****" in repr_str  # Password should be masked
    
    def test_config_dict_masks_password(self):
        """Test configuration dict export masks password"""
        config = DatabaseConfig(
            database_url="postgresql+asyncpg://user:secretpass@localhost:5432/testdb"
        )
        
        config_dict = config.model_dump()
        
        # Should mask password in URL when exported
        assert "secretpass" not in str(config_dict)


class TestDatabaseConfigValidation:
    """Test advanced database configuration validation"""
    
    @pytest.mark.parametrize("url,expected_valid", [
        ("sqlite+aiosqlite:///./data/test.db", True),
        ("sqlite+aiosqlite:///:memory:", True),
        ("postgresql+asyncpg://user:pass@localhost:5432/db", True),
        ("mysql+aiomysql://user:pass@localhost:3306/db", True),
        ("oracle+cx_oracle://user:pass@localhost:1521/db", True),
        ("invalid_protocol://localhost/db", False),
        ("http://not-a-database-url", False),
        ("", False),
        ("postgresql://missing+async+driver@localhost/db", False),
    ])
    def test_database_url_validation(self, url, expected_valid):
        """Test various database URL formats"""
        if expected_valid:
            config = DatabaseConfig(database_url=url)
            assert config.database_url == url
        else:
            with pytest.raises(ValidationError):
                DatabaseConfig(database_url=url)
    
    @pytest.mark.parametrize("pool_size,max_overflow,expected_valid", [
        (5, 10, True),    # Normal case
        (1, 0, True),     # Minimum valid values
        (100, 200, True), # Large values
        (10, 5, False),   # max_overflow < pool_size
        (0, 10, False),   # Invalid pool_size
        (5, -1, False),   # Invalid max_overflow
    ])
    def test_pool_configuration_validation(self, pool_size, max_overflow, expected_valid):
        """Test pool size and overflow validation"""
        if expected_valid:
            config = DatabaseConfig(
                database_pool_size=pool_size,
                database_max_overflow=max_overflow
            )
            assert config.database_pool_size == pool_size
            assert config.database_max_overflow == max_overflow
        else:
            with pytest.raises(ValidationError):
                DatabaseConfig(
                    database_pool_size=pool_size,
                    database_max_overflow=max_overflow
                )
