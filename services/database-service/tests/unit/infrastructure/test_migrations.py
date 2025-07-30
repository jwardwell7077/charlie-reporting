"""
Unit tests for database migration system.
Following TDD - these tests are written BEFORE implementation.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from pathlib import Path
from typing import List, Dict, Any

from src.infrastructure.persistence.migrations import (
    MigrationManager,
    Migration,
    MigrationState,
    MigrationError
)
from src.config.settings import DatabaseServiceConfig


class TestMigration:
    """Test individual migration behavior"""
    
    def test_migration_creation(self):
        """Test migration object creation"""
        migration = Migration(
            version="001",
            name="create_users_table",
            description="Create users table with basic fields",
            up_sql="CREATE TABLE users (id INTEGER PRIMARY KEY);",
            down_sql="DROP TABLE users;"
        )
        
        assert migration.version == "001"
        assert migration.name == "create_users_table"
        assert migration.description == "Create users table with basic fields"
        assert migration.up_sql == "CREATE TABLE users (id INTEGER PRIMARY KEY);"
        assert migration.down_sql == "DROP TABLE users;"
        assert migration.applied_at is None
    
    def test_migration_comparison(self):
        """Test migration version comparison"""
        migration1 = Migration(version="001", name="first", up_sql="", down_sql="")
        migration2 = Migration(version="002", name="second", up_sql="", down_sql="")
        migration3 = Migration(version="001", name="duplicate", up_sql="", down_sql="")
        
        assert migration1 < migration2
        assert migration2 > migration1
        assert migration1 == migration3  # Same version
    
    def test_migration_repr(self):
        """Test migration string representation"""
        migration = Migration(
            version="001",
            name="test_migration",
            up_sql="SELECT 1;",
            down_sql="SELECT 0;"
        )
        
        repr_str = repr(migration)
        assert "001" in repr_str
        assert "test_migration" in repr_str


class TestMigrationState:
    """Test migration state tracking"""
    
    def test_migration_state_creation(self):
        """Test migration state object creation"""
        state = MigrationState(
            version="001",
            name="test_migration",
            applied_at="2025-07-29T10:00:00",
            checksum="abc123"
        )
        
        assert state.version == "001"
        assert state.name == "test_migration"
        assert state.applied_at == "2025-07-29T10:00:00"
        assert state.checksum == "abc123"


class TestMigrationManager:
    """Test migration manager functionality"""
    
    @pytest.fixture
    def config(self):
        """Test configuration"""
        return DatabaseServiceConfig(
            database_url="sqlite+aiosqlite:///:memory:",
            database_pool_size=5
        )
    
    @pytest.fixture
    def migration_manager(self, config):
        """Migration manager instance"""
        return MigrationManager(config)
    
    @pytest.fixture
    def sample_migrations(self):
        """Sample migrations for testing"""
        return [
            Migration(
                version="001",
                name="create_users_table",
                description="Create users table",
                up_sql="""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """,
                down_sql="DROP TABLE users;"
            ),
            Migration(
                version="002",
                name="create_emails_table",
                description="Create emails table",
                up_sql="""
                CREATE TABLE emails (
                    id INTEGER PRIMARY KEY,
                    subject TEXT NOT NULL,
                    body TEXT,
                    user_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
                """,
                down_sql="DROP TABLE emails;"
            ),
            Migration(
                version="003",
                name="add_email_index",
                description="Add index on email subject",
                up_sql="CREATE INDEX idx_email_subject ON emails(subject);",
                down_sql="DROP INDEX idx_email_subject;"
            )
        ]
    
    @pytest.mark.asyncio
    async def test_initialize_creates_migration_table(self, migration_manager):
        """Test initialization creates migration tracking table"""
        with patch.object(migration_manager, '_db_connection') as mock_db:
            # Mock the async methods properly
            mock_db.initialize = AsyncMock()
            mock_session = AsyncMock()
            mock_db.get_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_db.get_session.return_value.__aexit__ = AsyncMock(return_value=None)
            
            await migration_manager.initialize()
            
            # Verify initialization was called
            mock_db.initialize.assert_called_once()
            
            # Verify migration table creation SQL was executed
            mock_session.execute.assert_called()
            executed_sql = str(mock_session.execute.call_args[0][0])
            assert "migration_history" in executed_sql.lower()
    
    @pytest.mark.asyncio
    async def test_load_migrations_from_directory(self, migration_manager):
        """Test loading migrations from filesystem"""
        mock_migration_files = {
            "001_create_users.sql": """
-- Description: Create users table
-- Up
CREATE TABLE users (id INTEGER PRIMARY KEY);
-- Down
DROP TABLE users;
            """,
            "002_create_emails.sql": """
-- Description: Create emails table
-- Up
CREATE TABLE emails (id INTEGER PRIMARY KEY);
-- Down
DROP TABLE emails;
            """
        }
        
        with patch('pathlib.Path.glob') as mock_glob, \
             patch('pathlib.Path.read_text') as mock_read:
            
            # Mock file discovery
            mock_files = [
                Path(f"migrations/{name}") 
                for name in mock_migration_files.keys()
            ]
            mock_glob.return_value = mock_files
            
            # Mock file reading - fix the encoding parameter issue
            def mock_read_side_effect(*args, **kwargs):
                call_count = getattr(mock_read_side_effect, 'call_count', 0)
                mock_read_side_effect.call_count = call_count + 1
                filename = mock_files[call_count - 1].name
                return mock_migration_files[filename]
            
            mock_read.side_effect = mock_read_side_effect
            
            migrations = await migration_manager.load_migrations_from_directory(
                "migrations/"
            )
            
            assert len(migrations) == 2
            assert migrations[0].version == "001"
            assert migrations[0].name == "create_users"
            assert migrations[1].version == "002"
            assert migrations[1].name == "create_emails"
    
    @pytest.mark.asyncio
    async def test_get_applied_migrations(self, migration_manager):
        """Test retrieving applied migrations from database"""
        mock_applied = [
            {"version": "001", "name": "create_users", 
             "applied_at": "2025-07-29T10:00:00", "checksum": "abc123"},
            {"version": "002", "name": "create_emails", 
             "applied_at": "2025-07-29T11:00:00", "checksum": "def456"}
        ]
        
        with patch.object(migration_manager, '_db_connection') as mock_db:
            mock_session = AsyncMock()
            mock_result = MagicMock()  # Regular MagicMock for result
            
            # Create mock row objects with attribute access
            mock_rows = []
            for item in mock_applied:
                mock_row = MagicMock()
                mock_row.version = item["version"]
                mock_row.name = item["name"]
                mock_row.applied_at = item["applied_at"]
                mock_row.checksum = item["checksum"]
                mock_rows.append(mock_row)
            
            mock_result.fetchall.return_value = mock_rows
            # session.execute should be awaitable and return a result
            mock_session.execute = AsyncMock(return_value=mock_result)
            
            # Setup context manager
            mock_db.get_session.return_value.__aenter__ = AsyncMock(
                return_value=mock_session
            )
            mock_db.get_session.return_value.__aexit__ = AsyncMock(
                return_value=None
            )
            
            applied = await migration_manager.get_applied_migrations()
            
            assert len(applied) == 2
            assert applied[0].version == "001"
            assert applied[1].version == "002"
    
    @pytest.mark.asyncio
    async def test_get_pending_migrations(self, migration_manager, sample_migrations):
        """Test identifying pending migrations"""
        # Mock applied migrations (only first two)
        applied = [
            MigrationState("001", "create_users_table", "2025-07-29T10:00:00", "abc123"),
            MigrationState("002", "create_emails_table", "2025-07-29T11:00:00", "def456")
        ]
        
        with patch.object(migration_manager, 'get_applied_migrations', return_value=applied):
            pending = await migration_manager.get_pending_migrations(sample_migrations)
            
            assert len(pending) == 1
            assert pending[0].version == "003"
            assert pending[0].name == "add_email_index"
    
    @pytest.mark.asyncio
    async def test_apply_migration_success(self, migration_manager, sample_migrations):
        """Test successful migration application"""
        migration = sample_migrations[0]  # create_users_table
        
        with patch.object(migration_manager, '_db_connection') as mock_db:
            mock_session = AsyncMock()
            mock_db.get_session.return_value.__aenter__.return_value = mock_session
            
            result = await migration_manager.apply_migration(migration)
            
            assert result.success is True
            assert result.migration == migration
            assert result.error is None
            
            # Verify migration SQL was executed
            assert mock_session.execute.call_count >= 1
            
            # Verify migration was recorded in history
            calls = mock_session.execute.call_args_list
            history_call = any("migration_history" in str(call[0][0]) for call in calls)
            assert history_call
    
    @pytest.mark.asyncio
    async def test_apply_migration_failure(self, migration_manager):
        """Test migration application failure handling"""
        bad_migration = Migration(
            version="999",
            name="bad_migration",
            up_sql="INVALID SQL SYNTAX HERE",
            down_sql="DROP TABLE nonexistent;"
        )
        
        with patch.object(migration_manager, '_db_connection') as mock_db:
            mock_session = AsyncMock()
            mock_session.execute.side_effect = Exception("SQL syntax error")
            mock_db.get_session.return_value.__aenter__.return_value = mock_session
            
            result = await migration_manager.apply_migration(bad_migration)
            
            assert result.success is False
            assert result.migration == bad_migration
            assert result.error is not None
            assert "SQL syntax error" in str(result.error)
    
    @pytest.mark.asyncio
    async def test_rollback_migration_success(self, migration_manager, sample_migrations):
        """Test successful migration rollback"""
        migration = sample_migrations[0]  # create_users_table
        
        with patch.object(migration_manager, '_db_connection') as mock_db:
            mock_session = AsyncMock()
            mock_db.get_session.return_value.__aenter__.return_value = mock_session
            
            result = await migration_manager.rollback_migration(migration)
            
            assert result.success is True
            assert result.migration == migration
            assert result.error is None
            
            # Verify rollback SQL was executed
            assert mock_session.execute.call_count >= 1
    
    @pytest.mark.asyncio
    async def test_migrate_up_applies_pending_migrations(self, migration_manager, sample_migrations):
        """Test migrate up applies all pending migrations in order"""
        # Mock no applied migrations
        with patch.object(migration_manager, 'get_applied_migrations', return_value=[]), \
             patch.object(migration_manager, 'apply_migration') as mock_apply:
            
            # Mock successful application
            mock_apply.return_value = MagicMock(success=True, error=None)
            
            results = await migration_manager.migrate_up(sample_migrations)
            
            assert len(results) == 3
            assert mock_apply.call_count == 3
            
            # Verify migrations were applied in order
            applied_versions = [call[0][0].version for call in mock_apply.call_args_list]
            assert applied_versions == ["001", "002", "003"]
    
    @pytest.mark.asyncio
    async def test_migrate_up_stops_on_failure(self, migration_manager, sample_migrations):
        """Test migrate up stops on first failure"""
        with patch.object(migration_manager, 'get_applied_migrations', return_value=[]), \
             patch.object(migration_manager, 'apply_migration') as mock_apply:
            
            # Mock failure on second migration
            def apply_side_effect(migration):
                if migration.version == "002":
                    return MagicMock(success=False, error="Database error")
                return MagicMock(success=True, error=None)
            
            mock_apply.side_effect = apply_side_effect
            
            results = await migration_manager.migrate_up(sample_migrations)
            
            # Should stop after failure
            assert len(results) == 2
            assert results[0].success is True
            assert results[1].success is False
    
    @pytest.mark.asyncio
    async def test_migrate_down_rolls_back_to_target(self, migration_manager, sample_migrations):
        """Test migrate down rolls back to target version"""
        # Mock all migrations applied
        applied = [
            MigrationState("001", "create_users_table", "2025-07-29T10:00:00", "abc123"),
            MigrationState("002", "create_emails_table", "2025-07-29T11:00:00", "def456"),
            MigrationState("003", "add_email_index", "2025-07-29T12:00:00", "ghi789")
        ]
        
        with patch.object(migration_manager, 'get_applied_migrations', return_value=applied), \
             patch.object(migration_manager, 'rollback_migration') as mock_rollback:
            
            mock_rollback.return_value = MagicMock(success=True, error=None)
            
            # Rollback to version 001 (should rollback 003 and 002)
            results = await migration_manager.migrate_down(sample_migrations, target_version="001")
            
            assert len(results) == 2
            assert mock_rollback.call_count == 2
            
            # Verify rollbacks were in reverse order
            rolled_back_versions = [call[0][0].version for call in mock_rollback.call_args_list]
            assert rolled_back_versions == ["003", "002"]
    
    @pytest.mark.asyncio
    async def test_migration_checksum_validation(self, migration_manager):
        """Test migration checksum validation"""
        migration = Migration(
            version="001",
            name="test",
            up_sql="CREATE TABLE test (id INTEGER);",
            down_sql="DROP TABLE test;"
        )
        
        checksum1 = migration_manager.calculate_checksum(migration)
        
        # Same migration should have same checksum
        migration2 = Migration(
            version="001",
            name="test",
            up_sql="CREATE TABLE test (id INTEGER);",
            down_sql="DROP TABLE test;"
        )
        checksum2 = migration_manager.calculate_checksum(migration2)
        
        assert checksum1 == checksum2
        
        # Different SQL should have different checksum
        migration3 = Migration(
            version="001",
            name="test",
            up_sql="CREATE TABLE test (id TEXT);",  # Different type
            down_sql="DROP TABLE test;"
        )
        checksum3 = migration_manager.calculate_checksum(migration3)
        
        assert checksum1 != checksum3
    
    @pytest.mark.asyncio
    async def test_migration_validation_detects_changes(self, migration_manager):
        """Test migration validation detects unauthorized changes"""
        # Original migration
        applied_state = MigrationState(
            version="001",
            name="test_migration",
            applied_at="2025-07-29T10:00:00",
            checksum="original_checksum"
        )
        
        # Modified migration (same version, different content)
        current_migration = Migration(
            version="001",
            name="test_migration",
            up_sql="MODIFIED SQL",  # Changed!
            down_sql="DROP TABLE test;"
        )
        
        with patch.object(migration_manager, 'calculate_checksum', return_value="different_checksum"):
            is_valid = migration_manager.validate_migration(applied_state, current_migration)
            
            assert is_valid is False
    
    def test_parse_migration_file_format(self, migration_manager):
        """Test parsing migration file format"""
        migration_content = """
-- Description: Create users table with authentication
-- Up
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- Down
DROP INDEX idx_users_email;
DROP TABLE users;
        """
        
        migration = migration_manager.parse_migration_file("001_create_users.sql", migration_content)
        
        assert migration.version == "001"
        assert migration.name == "create_users"
        assert migration.description == "Create users table with authentication"
        assert "CREATE TABLE users" in migration.up_sql
        assert "CREATE INDEX idx_users_email" in migration.up_sql
        assert "DROP TABLE users" in migration.down_sql
        assert "DROP INDEX idx_users_email" in migration.down_sql


class TestMigrationError:
    """Test migration error handling"""
    
    def test_migration_error_creation(self):
        """Test migration error object creation"""
        migration = Migration(version="001", name="test", up_sql="", down_sql="")
        error = MigrationError("Database connection failed", migration)
        
        assert str(error) == "Database connection failed"
        assert error.migration == migration
    
    def test_migration_error_with_nested_exception(self):
        """Test migration error with nested exception"""
        migration = Migration(version="001", name="test", up_sql="", down_sql="")
        original_error = ValueError("Invalid SQL")
        error = MigrationError("Migration failed", migration, original_error)
        
        assert "Migration failed" in str(error)
        assert error.migration == migration
        assert error.original_error == original_error
