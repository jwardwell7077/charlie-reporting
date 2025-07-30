"""
EmailRecord repository implementation.
Handles database operations for EmailRecord entities.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, func

from .base_repository import BaseRepository
from .email_repository_interface import EmailRepositoryInterface
from ..models.email_record import EmailRecord, EmailStatus
from ...infrastructure.persistence.database import DatabaseConnection
from ...infrastructure.persistence.models.email_models import EmailRecordORM
from ...infrastructure.persistence.mappers import EmailRecordMapper


class EmailRepository(EmailRepositoryInterface):
    """Repository for EmailRecord entities"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self._db_connection = db_connection
        self._mapper = EmailRecordMapper()
    
    async def save(self, email_record: EmailRecord) -> EmailRecord:
        """Save an email record"""
        async with self._db_connection.get_session() as session:
            # Check if record exists
            existing = await session.get(EmailRecordORM, email_record.id)
            
            if existing:
                # Update existing record
                orm_model = self._mapper.to_orm(email_record)
                for key, value in orm_model.__dict__.items():
                    if not key.startswith('_'):
                        setattr(existing, key, value)
                await session.flush()
                return self._mapper.to_domain(existing)
            else:
                # Create new record
                orm_model = self._mapper.to_orm(email_record)
                session.add(orm_model)
                await session.flush()
                return self._mapper.to_domain(orm_model)
    
    async def find_by_id(self, email_id: UUID) -> Optional[EmailRecord]:
        """Find email record by ID"""
        async with self._db_connection.get_session() as session:
            orm_model = await session.get(EmailRecordORM, email_id)
            if orm_model:
                return self._mapper.to_domain(orm_model)
            return None
    
    async def find_by_message_id(self, message_id: str) -> Optional[EmailRecord]:
        """Find email record by message ID"""
        async with self._db_connection.get_session() as session:
            stmt = select(EmailRecordORM).where(EmailRecordORM.message_id == message_id)
            result = await session.execute(stmt)
            orm_model = result.scalar_one_or_none()
            if orm_model:
                return self._mapper.to_domain(orm_model)
            return None
    
    async def find_all(self, limit: Optional[int] = None, 
                      offset: int = 0) -> List[EmailRecord]:
        """Find all email records with optional pagination"""
        async with self._db_connection.get_session() as session:
            stmt = select(EmailRecordORM).offset(offset)
            if limit:
                stmt = stmt.limit(limit)
            
            result = await session.execute(stmt)
            orm_models = result.scalars().all()
            return [self._mapper.to_domain(orm) for orm in orm_models]
    
    async def delete(self, email_id: UUID) -> bool:
        """Delete an email record"""
        async with self._db_connection.get_session() as session:
            orm_model = await session.get(EmailRecordORM, email_id)
            if orm_model:
                await session.delete(orm_model)
                return True
            return False
    
    async def list_all(self) -> List[EmailRecord]:
        """List all email records"""
        async with self._db_connection.get_session() as session:
            stmt = select(EmailRecord)
            result = await session.execute(stmt)
            return result.scalars().all()
    
    async def exists(self, email_id: UUID) -> bool:
        """Check if an email record exists"""
        async with self._db_connection.get_session() as session:
            email_record = await session.get(EmailRecord, email_id)
            return email_record is not None
    
    # Domain-specific query methods
    
    async def get_by_message_id(self, message_id: str) -> Optional[EmailRecord]:
        """Get an email record by its message ID"""
        async with self._db_connection.get_session() as session:
            stmt = select(EmailRecord).where(EmailRecord.message_id == message_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    async def get_by_status(self, status: EmailStatus) -> List[EmailRecord]:
        """Get email records by status"""
        async with self._db_connection.get_session() as session:
            stmt = select(EmailRecord).where(EmailRecord.status == status)
            result = await session.execute(stmt)
            return result.scalars().all()
    
    async def get_by_sender(self, sender: str) -> List[EmailRecord]:
        """Get email records by sender"""
        async with self._db_connection.get_session() as session:
            stmt = select(EmailRecord).where(EmailRecord.sender == sender)
            result = await session.execute(stmt)
            return result.scalars().all()
    
    async def get_by_date_range(self, start_date: datetime, 
                               end_date: datetime) -> List[EmailRecord]:
        """Get email records within a date range"""
        async with self._db_connection.get_session() as session:
            stmt = select(EmailRecord).where(
                EmailRecord.received_date >= start_date,
                EmailRecord.received_date <= end_date
            )
            result = await session.execute(stmt)
            return result.scalars().all()
    
    async def count_by_status(self, status: EmailStatus) -> int:
        """Count email records by status"""
        async with self._db_connection.get_session() as session:
            stmt = select(func.count(EmailRecord.id)).where(
                EmailRecord.status == status
            )
            result = await session.execute(stmt)
            return result.scalar()
