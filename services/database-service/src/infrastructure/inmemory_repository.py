"""In-memory repository implementations for API tests / example usage.

These are NOT intended for production; they provide a lightweight
stand‑in until a real SQLAlchemy repository is fully wired to the
FastAPI layer. Only the subset of methods used by the current API
tests (create/save, find_by_id, find_by_message_id) are implemented.
"""
from __future__ import annotations

from typing import Dict, List
from uuid import UUID

from ..domain.models.email_record import EmailRecord
from ..domain.repositories.email_repository_interface import (
    EmailRepositoryInterface,
)


class InMemoryEmailRepository(EmailRepositoryInterface):
    """Simple in-memory email repository (test/demo only)."""
    def __init__(self) -> None:
        self._items: Dict[UUID, EmailRecord] = {}
        self._by_message_id: Dict[str, UUID] = {}

    async def save(
        self, email_record: EmailRecord
    ) -> EmailRecord:  # type: ignore[override]
        self._items[email_record.id] = email_record
        self._by_message_id[email_record.message_id] = email_record.id
        return email_record

    async def create(
        self, email_record: EmailRecord
    ) -> EmailRecord:  # type: ignore[override]
        return await self.save(email_record)

    async def find_by_id(self, email_id: UUID):  # type: ignore[override]
        return self._items.get(email_id)

    async def get_by_id(self, email_id: UUID):  # delegate
        return await self.find_by_id(email_id)

    async def find_by_message_id(
        self, message_id: str
    ):  # type: ignore[override]
        eid = self._by_message_id.get(message_id)
        return self._items.get(eid) if eid else None

    async def get_by_message_id(self, message_id: str):  # delegate
        return await self.find_by_message_id(message_id)

    async def update(
        self, email_record: EmailRecord
    ) -> EmailRecord:  # type: ignore[override]
        return await self.save(email_record)

    async def delete(self, email_id: UUID) -> bool:  # type: ignore[override]
        existed = email_id in self._items
        if existed:
            record = self._items.pop(email_id)
            self._by_message_id.pop(record.message_id, None)
        return existed

    async def list_all(self) -> List[EmailRecord]:  # type: ignore[override]
        return list(self._items.values())

    # Remaining interface methods not needed for tests are omitted.
    async def exists(self, email_id: UUID) -> bool:  # type: ignore[override]
        return email_id in self._items

    # Canonical getters not yet covered
    async def get_by_sender(self, sender: str):  # type: ignore[override]
        return [e for e in self._items.values() if e.sender == sender]

    async def get_by_date_range(
        self, start_date, end_date
    ):  # type: ignore[override]
        return [
            e for e in self._items.values()
            if start_date <= e.sent_date <= end_date
        ]

    async def get_by_status(self, status):  # type: ignore[override]
        return [e for e in self._items.values() if e.status == status]

    async def count_by_status(self, status):  # type: ignore[override]
        return len([e for e in self._items.values() if e.status == status])

    # Legacy find_* wrappers
    async def find_all(self, limit=None, offset=0):  # type: ignore[override]
        items = list(self._items.values())
        if limit is None:
            return items[offset:]
        return items[offset: offset + limit]

    async def find_by_sender(self, sender: str):  # type: ignore[override]
        return await self.get_by_sender(sender)

    async def find_by_date_range(
        self, start_date, end_date
    ):  # type: ignore[override]
        return await self.get_by_date_range(start_date, end_date)

    async def find_by_status(self, status):  # type: ignore[override]
        return await self.get_by_status(status)
