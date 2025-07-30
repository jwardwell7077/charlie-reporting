"""
Database migration system for database-service
"""

import hashlib
import re
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any
import structlog

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from .database import DatabaseConnection
from ...config.settings import DatabaseServiceConfig


logger = structlog.get_logger(__name__)


@dataclass
class Migration:
    """Represents a database migration"""
    
    version: str
    name: str
    up_sql: str
    down_sql: str
    description: str = ""
    applied_at: Optional[datetime] = None
    
    def __lt__(self, other):
        """Compare migrations by version for sorting"""
        return self.version < other.version
    
    def __eq__(self, other):
        """Compare migrations by version for equality"""
        return self.version == other.version
    
    def __repr__(self):
        """String representation of migration"""
        return f"Migration(version='{self.version}', name='{self.name}')"


@dataclass
class MigrationState:
    """Represents the state of an applied migration"""
    
    version: str
    name: str
    applied_at: str
    checksum: str


@dataclass
class MigrationResult:
    """Result of a migration operation"""
    
    migration: Migration
    success: bool
    error: Optional[Exception] = None
    execution_time: Optional[float] = None


class MigrationError(Exception):
    """Custom exception for migration errors"""
    
    def __init__(self, message: str, migration: Migration, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.migration = migration
        self.original_error = original_error


class MigrationManager:
    """
    Manages database migrations for the database service.
    
    Provides:
    - Migration discovery and loading
    - Migration state tracking
    - Forward and backward migration execution
    - Migration validation and checksums
    """
    
    def __init__(self, config: DatabaseServiceConfig):
        self.config = config
        self._db_connection = DatabaseConnection(config)
        self._migration_table = "migration_history"
    
    async def initialize(self) -> None:
        """Initialize migration system and create tracking table"""
        await self._db_connection.initialize()
        await self._create_migration_table()
        
        logger.info("Migration system initialized")
    
    async def _create_migration_table(self) -> None:
        """Create migration history tracking table if it doesn't exist"""
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self._migration_table} (
            version TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            checksum TEXT NOT NULL,
            execution_time_ms INTEGER
        )
        """
        
        async with self._db_connection.get_session() as session:
            await session.execute(text(create_table_sql))
            logger.debug("Migration tracking table ensured")
    
    async def load_migrations_from_directory(self, migrations_dir: str) -> List[Migration]:
        """
        Load migrations from filesystem directory.
        
        Expected format: {version}_{name}.sql
        Example: 001_create_users_table.sql
        """
        migrations_path = Path(migrations_dir)
        migration_files = list(migrations_path.glob("*.sql"))
        
        migrations = []
        for file_path in sorted(migration_files):
            try:
                content = file_path.read_text(encoding='utf-8')
                migration = self.parse_migration_file(file_path.name, content)
                migrations.append(migration)
                
                logger.debug(
                    "Loaded migration from file",
                    version=migration.version,
                    name=migration.name,
                    file=file_path.name
                )
                
            except Exception as e:
                logger.error(
                    "Failed to load migration file",
                    file=file_path.name,
                    error=str(e)
                )
                raise MigrationError(f"Failed to load migration {file_path.name}: {e}", None, e)
        
        return sorted(migrations)
    
    def parse_migration_file(self, filename: str, content: str) -> Migration:
        """
        Parse migration file content into Migration object.
        
        Expected format:
        -- Description: Migration description
        -- Up
        CREATE TABLE ...;
        -- Down
        DROP TABLE ...;
        """
        # Extract version and name from filename
        match = re.match(r'^(\d+)_(.+)\.sql$', filename)
        if not match:
            raise ValueError(f"Invalid migration filename format: {filename}")
        
        version, name = match.groups()
        
        # Parse content sections
        description_match = re.search(r'-- Description:\s*(.+)', content)
        description = description_match.group(1).strip() if description_match else ""
        
        # Split on -- Up and -- Down markers
        up_match = re.search(r'-- Up\s*\n(.*?)(?=-- Down|\Z)', content, re.DOTALL)
        down_match = re.search(r'-- Down\s*\n(.*)', content, re.DOTALL)
        
        if not up_match:
            raise ValueError(f"No '-- Up' section found in {filename}")
        if not down_match:
            raise ValueError(f"No '-- Down' section found in {filename}")
        
        up_sql = up_match.group(1).strip()
        down_sql = down_match.group(1).strip()
        
        return Migration(
            version=version,
            name=name,
            description=description,
            up_sql=up_sql,
            down_sql=down_sql
        )
    
    async def get_applied_migrations(self) -> List[MigrationState]:
        """Get list of migrations that have been applied to the database"""
        query = f"""
        SELECT version, name, applied_at, checksum
        FROM {self._migration_table}
        ORDER BY version
        """
        
        async with self._db_connection.get_session() as session:
            result = await session.execute(text(query))
            rows = result.fetchall()
            
            return [
                MigrationState(
                    version=row.version,
                    name=row.name,
                    applied_at=str(row.applied_at),
                    checksum=row.checksum
                )
                for row in rows
            ]
    
    async def get_pending_migrations(self, available_migrations: List[Migration]) -> List[Migration]:
        """Get list of migrations that need to be applied"""
        applied_migrations = await self.get_applied_migrations()
        applied_versions = {state.version for state in applied_migrations}
        
        pending = [
            migration for migration in available_migrations
            if migration.version not in applied_versions
        ]
        
        return sorted(pending)
    
    async def apply_migration(self, migration: Migration) -> MigrationResult:
        """Apply a single migration"""
        start_time = datetime.now()
        
        try:
            async with self._db_connection.get_session() as session:
                # Execute migration SQL
                await session.execute(text(migration.up_sql))
                
                # Record migration in history
                checksum = self.calculate_checksum(migration)
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                insert_history = f"""
                INSERT INTO {self._migration_table} 
                (version, name, description, checksum, execution_time_ms)
                VALUES (:version, :name, :description, :checksum, :execution_time)
                """
                
                await session.execute(text(insert_history), {
                    "version": migration.version,
                    "name": migration.name,
                    "description": migration.description,
                    "checksum": checksum,
                    "execution_time": int(execution_time)
                })
                
                logger.info(
                    "Migration applied successfully",
                    version=migration.version,
                    name=migration.name,
                    execution_time_ms=int(execution_time)
                )
                
                return MigrationResult(
                    migration=migration,
                    success=True,
                    execution_time=execution_time
                )
                
        except Exception as e:
            logger.error(
                "Migration failed",
                version=migration.version,
                name=migration.name,
                error=str(e)
            )
            
            return MigrationResult(
                migration=migration,
                success=False,
                error=e
            )
    
    async def rollback_migration(self, migration: Migration) -> MigrationResult:
        """Rollback a single migration"""
        start_time = datetime.now()
        
        try:
            async with self._db_connection.get_session() as session:
                # Execute rollback SQL
                await session.execute(text(migration.down_sql))
                
                # Remove from migration history
                delete_history = f"""
                DELETE FROM {self._migration_table}
                WHERE version = :version
                """
                
                await session.execute(text(delete_history), {"version": migration.version})
                
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                logger.info(
                    "Migration rolled back successfully",
                    version=migration.version,
                    name=migration.name,
                    execution_time_ms=int(execution_time)
                )
                
                return MigrationResult(
                    migration=migration,
                    success=True,
                    execution_time=execution_time
                )
                
        except Exception as e:
            logger.error(
                "Migration rollback failed",
                version=migration.version,
                name=migration.name,
                error=str(e)
            )
            
            return MigrationResult(
                migration=migration,
                success=False,
                error=e
            )
    
    async def migrate_up(self, migrations: List[Migration], target_version: Optional[str] = None) -> List[MigrationResult]:
        """Apply pending migrations up to target version (or all if no target)"""
        pending = await self.get_pending_migrations(migrations)
        
        if target_version:
            # Filter to only migrations up to target
            pending = [m for m in pending if m.version <= target_version]
        
        results = []
        for migration in pending:
            result = await self.apply_migration(migration)
            results.append(result)
            
            if not result.success:
                logger.error(
                    "Migration failed, stopping execution",
                    version=migration.version,
                    error=str(result.error)
                )
                break
        
        return results
    
    async def migrate_down(self, migrations: List[Migration], target_version: str) -> List[MigrationResult]:
        """Rollback migrations down to target version"""
        applied = await self.get_applied_migrations()
        
        # Find migrations to rollback (in reverse order)
        to_rollback = []
        for state in reversed(applied):
            if state.version > target_version:
                # Find the migration object
                migration = next((m for m in migrations if m.version == state.version), None)
                if migration:
                    to_rollback.append(migration)
        
        results = []
        for migration in to_rollback:
            result = await self.rollback_migration(migration)
            results.append(result)
            
            if not result.success:
                logger.error(
                    "Migration rollback failed, stopping execution",
                    version=migration.version,
                    error=str(result.error)
                )
                break
        
        return results
    
    def calculate_checksum(self, migration: Migration) -> str:
        """Calculate checksum for migration validation"""
        content = f"{migration.version}|{migration.name}|{migration.up_sql}|{migration.down_sql}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
    
    def validate_migration(self, applied_state: MigrationState, current_migration: Migration) -> bool:
        """Validate that applied migration matches current migration"""
        current_checksum = self.calculate_checksum(current_migration)
        return applied_state.checksum == current_checksum
    
    async def close(self) -> None:
        """Close migration manager and cleanup resources"""
        await self._db_connection.close()
        logger.info("Migration manager closed")
