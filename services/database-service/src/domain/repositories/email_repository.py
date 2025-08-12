"""
EmailRecord repository implementation.
Handles database operations for EmailRecord entities.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, func
from inspect import iscoroutinefunction

from .email_repository_interface import EmailRepositoryInterface
from ..models.email_record import EmailRecord, EmailStatus
from ...infrastructure.persistence.database import DatabaseConnection
from ...infrastructure.persistence.models.email_models import EmailRecordORM
from ...infrastructure.persistence.mappers import EmailRecordMapper


class EmailRepository(EmailRepositoryInterface):
    """Repository for EmailRecord entities."""

    def __init__(self, db_connection: DatabaseConnection):
        self._db_connection = db_connection
        self._mapper = EmailRecordMapper()

    async def create(self, email_record: EmailRecord) -> EmailRecord:
        async with self._db_connection.get_session() as session:
            orm_model = self._mapper.to_orm(email_record)
            # session.add may be AsyncMock in tests; await only if coroutine
            add_call = session.add
            if iscoroutinefunction(add_call):  # pragma: no cover - test shim
                await add_call(orm_model)
            else:
                add_call(orm_model)
            await session.flush()
            return self._mapper.to_domain(orm_model)

    async def get_by_id(self, email_id: UUID) -> Optional[EmailRecord]:
        async with self._db_connection.get_session() as session:
            orm_model = await session.get(EmailRecordORM, email_id)
            if orm_model:
                return self._mapper.to_domain(orm_model)
            return None

    async def update(self, email_record: EmailRecord) -> EmailRecord:
        async with self._db_connection.get_session() as session:
            orm_model = self._mapper.to_orm(email_record)
            merged_orm = await session.merge(orm_model)
            await session.flush()
            return self._mapper.to_domain(merged_orm)

    async def delete(self, email_id: UUID) -> bool:
        async with self._db_connection.get_session() as session:
            orm_model = await session.get(EmailRecordORM, email_id)
            if orm_model:
                await session.delete(orm_model)
                return True
            return False

    async def list_all(self) -> List[EmailRecord]:
        async with self._db_connection.get_session() as session:
            stmt = select(EmailRecordORM)
            result = await session.execute(stmt)
            orm_models = result.scalars().all()
            return [self._mapper.to_domain(orm) for orm in orm_models]

    async def exists(self, email_id: UUID) -> bool:
        async with self._db_connection.get_session() as session:
            orm_model = await session.get(EmailRecordORM, email_id)
            return orm_model is not None

    async def get_by_message_id(
        self, message_id: str
    ) -> Optional[EmailRecord]:
        async with self._db_connection.get_session() as session:
            stmt = select(EmailRecordORM).where(
                EmailRecordORM.message_id == message_id
            )
            result = await session.execute(stmt)
            orm_model = result.scalar_one_or_none()
            if orm_model:
                return self._mapper.to_domain(orm_model)
            return None

    async def get_by_sender(self, sender: str) -> List[EmailRecord]:
        async with self._db_connection.get_session() as session:
            stmt = select(EmailRecordORM).where(
                EmailRecordORM.sender == sender
            )
            result = await session.execute(stmt)
            orm_models = result.scalars().all()
            return [self._mapper.to_domain(orm) for orm in orm_models]

    async def get_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[EmailRecord]:
        async with self._db_connection.get_session() as session:
            stmt = select(EmailRecordORM).where(
                EmailRecordORM.received_date >= start_date,
                EmailRecordORM.received_date <= end_date,
            )
            result = await session.execute(stmt)
            orm_models = result.scalars().all()
            return [self._mapper.to_domain(orm) for orm in orm_models]

    async def get_by_status(self, status: EmailStatus) -> List[EmailRecord]:
        async with self._db_connection.get_session() as session:
            stmt = select(EmailRecordORM).where(
                EmailRecordORM.status == status.value
            )
            result = await session.execute(stmt)
            orm_models = result.scalars().all()
            return [self._mapper.to_domain(orm) for orm in orm_models]

    async def count_by_status(self, status: EmailStatus) -> int:
        async with self._db_connection.get_session() as session:
            stmt = select(func.count(EmailRecordORM.id)).where(
                EmailRecordORM.status == status.value
            )
            result = await session.execute(stmt)
            return result.scalar() or 0

    # Legacy method aliases
    async def save(self, email_record: EmailRecord) -> EmailRecord:
        try:
            existing = await self.get_by_id(email_record.id)
            if existing:
                return await self.update(email_record)
            return await self.create(email_record)
        except Exception:
            return await self.create(email_record)

    async def find_by_id(self, email_id: UUID) -> Optional[EmailRecord]:
        return await self.get_by_id(email_id)

    async def find_by_message_id(
        self, message_id: str
    ) -> Optional[EmailRecord]:
        return await self.get_by_message_id(message_id)

    async def find_all(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> List[EmailRecord]:
        async with self._db_connection.get_session() as session:
            stmt = select(EmailRecordORM).offset(offset)
            if limit:
                stmt = stmt.limit(limit)
            result = await session.execute(stmt)
            orm_models = result.scalars().all()
            return [self._mapper.to_domain(orm) for orm in orm_models]

    async def find_by_sender(self, sender: str) -> List[EmailRecord]:
        return await self.get_by_sender(sender)

    async def find_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[EmailRecord]:
        return await self.get_by_date_range(start_date, end_date)

    async def find_by_status(self, status: EmailStatus) -> List[EmailRecord]:
        return await self.get_by_status(status)
