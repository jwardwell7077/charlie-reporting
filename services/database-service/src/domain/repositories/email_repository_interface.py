"""Abstract EmailRepository interface.
"""

from abc import abstractmethod
from datetime import datetime
from uuid import UUID

from ..models.email_record import EmailRecord, EmailStatus
from .base_repository import BaseRepository


class EmailRepositoryInterface(BaseRepository):
    """Abstract repository for EmailRecord entities.

    Provides both canonical get_/create/update/delete method names and
    legacy find_/save aliases used by existing tests and services.
    """

    # Canonical CRUD
    @abstractmethod
    async def create(
        self, email_record: EmailRecord
    ) -> EmailRecord:  # pragma: no cover - interface
        """Create a new email record."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(
        self, email_id: UUID
    ) -> EmailRecord | None:  # pragma: no cover - interface
        """Get email record by ID."""
        raise NotImplementedError

    @abstractmethod
    async def update(
        self, email_record: EmailRecord
    ) -> EmailRecord:  # pragma: no cover - interface
        """Update an existing email record."""
        raise NotImplementedError

    @abstractmethod
    async def delete(
        self, email_id: UUID
    ) -> bool:  # pragma: no cover - interface
        """Delete an email record by ID."""
        raise NotImplementedError

    @abstractmethod
    async def list_all(
        self,
    ) -> list[EmailRecord]:  # pragma: no cover - interface
        """List all email records."""
        raise NotImplementedError

    @abstractmethod
    async def exists(
        self, email_id: UUID
    ) -> bool:  # pragma: no cover - interface
        """Check if email record exists by ID."""
        raise NotImplementedError

    # Canonical email-specific queries
    @abstractmethod
    async def get_by_message_id(
        self, message_id: str
    ) -> EmailRecord | None:  # pragma: no cover - interface
        """Find email record by message ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_sender(
        self, sender: str
    ) -> list[EmailRecord]:  # pragma: no cover - interface
        """Find email records by sender."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> list[EmailRecord]:  # pragma: no cover - interface
        """Find email records within a date range."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_status(
        self, status: EmailStatus
    ) -> list[EmailRecord]:  # pragma: no cover - interface
        """Find email records by status."""
        raise NotImplementedError

    @abstractmethod
    async def count_by_status(
        self, status: EmailStatus
    ) -> int:  # pragma: no cover - interface
        """Count email records by status."""
        raise NotImplementedError

    # Legacy alias methods (tests & older code paths expect these)
    @abstractmethod
    async def save(
        self, email_record: EmailRecord
    ) -> EmailRecord:  # pragma: no cover - interface
        """Create or update (upsert) an EmailRecord."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(
        self, email_id: UUID
    ) -> EmailRecord | None:  # pragma: no cover - interface
        """Find email record by ID (legacy)."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_message_id(
        self, message_id: str
    ) -> EmailRecord | None:  # pragma: no cover - interface
        """Find email record by message ID (legacy)."""
        raise NotImplementedError

    @abstractmethod
    async def find_all(
        self, limit: int | None = None, offset: int = 0
    ) -> list[EmailRecord]:  # pragma: no cover - interface
        """Find all email records (legacy)."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_sender(
        self, sender: str
    ) -> list[EmailRecord]:  # pragma: no cover - interface
        """Find email records by sender (legacy)."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> list[EmailRecord]:  # pragma: no cover - interface
        """Find email records within a date range (legacy)."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_status(
        self, status: EmailStatus
    ) -> list[EmailRecord]:  # pragma: no cover - interface
        """Find email records by status (legacy)."""
        raise NotImplementedError
