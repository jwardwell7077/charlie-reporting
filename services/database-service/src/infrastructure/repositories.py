"""
SQLAlchemy-based repository implementations.
These repositories handle the conversion between domain and persistence models.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import delete, func, select

from ..domain.models.email_record import EmailRecord, EmailStatus
from ..domain.repositories.email_repository_interface import EmailRepositoryInterface
from .persistence.database import DatabaseConnection
from .persistence.mappers import EmailRecordMapper
from .persistence.models.email_models import EmailRecordORM


class SQLAlchemyEmailRepository(EmailRepositoryInterface):
    """Async SQLAlchemy implementation of EmailRepositoryInterface."""

    def __init__(self, db_connection: DatabaseConnection):
        self._db = db_connection
        self._mapper = EmailRecordMapper()

    # Legacy + canonical upsert
    async def save(
        self, email_record: EmailRecord
    ) -> EmailRecord:  # type: ignore[override]
        async with self._db.get_session() as session:
            existing = await session.get(EmailRecordORM, email_record.id)
            if existing:
                orm_model = self._mapper.to_orm(email_record)
                for key, value in orm_model.__dict__.items():
                    if not key.startswith("_"):
                        setattr(existing, key, value)
                await session.flush()
                return self._mapper.to_domain(existing)
            orm_model = self._mapper.to_orm(email_record)
            session.add(orm_model)
            await session.flush()
            return self._mapper.to_domain(orm_model)

    # Canonical create delegates to save
    async def create(self, email_record: EmailRecord) -> EmailRecord:
        return await self.save(email_record)

    async def get_by_id(self, email_id: UUID) -> Optional[EmailRecord]:
        return await self.find_by_id(email_id)

    async def update(self, email_record: EmailRecord) -> EmailRecord:
        return await self.save(email_record)

    async def delete(self, email_id: UUID) -> bool:
        async with self._db.get_session() as session:
            stmt = delete(EmailRecordORM).where(EmailRecordORM.id == email_id)
            result = await session.execute(stmt)
            return result.rowcount > 0

    async def list_all(self) -> List[EmailRecord]:
        async with self._db.get_session() as session:
            stmt = select(EmailRecordORM)
            result = await session.execute(stmt)
            return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def exists(self, email_id: UUID) -> bool:
        return (await self.find_by_id(email_id)) is not None

    # Canonical queries
    async def get_by_message_id(
        self, message_id: str
    ) -> Optional[EmailRecord]:
        return await self.find_by_message_id(message_id)

    async def get_by_sender(self, sender: str) -> List[EmailRecord]:
        return await self.find_by_sender(sender)

    async def get_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[EmailRecord]:
        return await self.find_by_date_range(start_date, end_date)

    async def get_by_status(self, status: EmailStatus) -> List[EmailRecord]:
        return await self.find_by_status(status)

    async def count_by_status(self, status: EmailStatus) -> int:
        async with self._db.get_session() as session:
            stmt = select(func.count(EmailRecordORM.id)).where(
                EmailRecordORM.status == status.value
            )
            result = await session.execute(stmt)
            return int(result.scalar() or 0)

    # Legacy find_* implementations
    async def find_by_id(self, email_id: UUID) -> Optional[EmailRecord]:
        async with self._db.get_session() as session:
            orm = await session.get(EmailRecordORM, email_id)
            return self._mapper.to_domain(orm) if orm else None

    async def find_by_message_id(
        self, message_id: str
    ) -> Optional[EmailRecord]:
        async with self._db.get_session() as session:
            stmt = select(EmailRecordORM).where(
                EmailRecordORM.message_id == message_id
            )
            result = await session.execute(stmt)
            orm = result.scalar_one_or_none()
            return self._mapper.to_domain(orm) if orm else None

    async def find_all(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> List[EmailRecord]:
        async with self._db.get_session() as session:
            stmt = select(EmailRecordORM).offset(offset)
            if limit:
                stmt = stmt.limit(limit)
            result = await session.execute(stmt)
            return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def find_by_sender(self, sender: str) -> List[EmailRecord]:
        async with self._db.get_session() as session:
            stmt = select(EmailRecordORM).where(
                EmailRecordORM.sender == sender
            )
            result = await session.execute(stmt)
            return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def find_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[EmailRecord]:
        async with self._db.get_session() as session:
            stmt = select(EmailRecordORM).where(
                EmailRecordORM.received_date >= start_date,
                EmailRecordORM.received_date <= end_date,
            )
            result = await session.execute(stmt)
            return [self._mapper.to_domain(o) for o in result.scalars().all()]

    async def find_by_status(self, status: EmailStatus) -> List[EmailRecord]:
        async with self._db.get_session() as session:
            stmt = select(EmailRecordORM).where(
                EmailRecordORM.status == status.value
            )
            result = await session.execute(stmt)
            return [self._mapper.to_domain(o) for o in result.scalars().all()]
