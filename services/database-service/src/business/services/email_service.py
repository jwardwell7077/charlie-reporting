"""Email business service.

Clean minimal implementation providing only the behaviour required by
current API tests (import, get, list, basic processing hooks) while
preserving placeholders for future expansion.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging
from uuid import UUID

from ...domain.models.email_record import (
    EmailRecord,
    EmailStatus,
    EmailPriority,
)
from ...domain.repositories.email_repository_interface import (
    EmailRepositoryInterface,
)
from ...infrastructure.persistence.database import DatabaseConnection


class EmailService:
    """Email business service handling workflows and rules."""

    def __init__(
        self,
        email_repository: EmailRepositoryInterface,
        db_connection: DatabaseConnection | None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._email_repository = email_repository
        self._db_connection = db_connection
        self._logger = logger or logging.getLogger(__name__)

    # ------------------------------------------------------------------
    # Import / create
    # ------------------------------------------------------------------
    async def import_email(self, email_data: Dict[str, Any]) -> EmailRecord:
        """Import a new email (idempotent on message_id).

        Raises ValueError if message_id already exists.
        """
        message_id = email_data.get("message_id")
        existing = await self._email_repository.find_by_message_id(
            message_id or ""
        )
        if existing:
            raise ValueError(
                f"Email with message_id {message_id} already exists"
            )

        email_record = EmailRecord(
            message_id=email_data["message_id"],
            subject=email_data["subject"],
            sender=email_data["sender"],
            recipients=email_data.get("recipients", []),
            cc_recipients=email_data.get("cc_recipients", []),
            bcc_recipients=email_data.get("bcc_recipients", []),
            body_text=email_data.get("body_text", ""),
            body_html=email_data.get("body_html", ""),
            sent_date=email_data["sent_date"],
            received_date=email_data.get("received_date", datetime.now()),
            priority=EmailPriority(email_data.get("priority", "normal")),
            status=EmailStatus.RECEIVED,
            attachments=[],
        )
        email_record = self._apply_business_rules(email_record)
        return await self._email_repository.save(email_record)

    # ------------------------------------------------------------------
    # Simple retrieval helpers
    # ------------------------------------------------------------------
    async def get_email_by_id(self, email_id: UUID) -> Optional[EmailRecord]:
        return await self._email_repository.find_by_id(email_id)

    async def list_emails(self) -> List[EmailRecord]:
        return await self._email_repository.list_all()

    # ------------------------------------------------------------------
    # Processing / batch (minimal)
    # ------------------------------------------------------------------
    async def process_email(self, email_id: UUID) -> EmailRecord:
        email = await self._email_repository.find_by_id(email_id)
        if not email:
            raise ValueError(f"Email not found: {email_id}")
        if email.status != EmailStatus.RECEIVED:
            raise ValueError(
                f"Email {email_id} is not in RECEIVED status"
            )
        email.status = EmailStatus.PROCESSED
        email = self._apply_processing_rules(email)
        return await self._email_repository.save(email)

    async def archive_old_emails(self, days_old: int = 30) -> int:
        cutoff = datetime.now() - timedelta(days=days_old)
        old = await self._email_repository.find_by_date_range(
            datetime.min, cutoff
        )
        archived = 0
        for email in old:
            if email.status == EmailStatus.PROCESSED:
                email.status = EmailStatus.ARCHIVED
                await self._email_repository.save(email)
                archived += 1
        return archived

    async def get_email_statistics(self) -> Dict[str, Any]:
        stats: Dict[str, Any] = {}
        for status in EmailStatus:
            stats[f"count_{status.value}"] = await self._email_repository.\
                count_by_status(status)
        return stats

    # ------------------------------------------------------------------
    # Internal business rules
    # ------------------------------------------------------------------
    def _apply_business_rules(self, email: EmailRecord) -> EmailRecord:
        high_priority_domains = ["urgent.com", "priority.org"]
        domain = email.sender.split("@")[-1] if "@" in email.sender else ""
        if domain in high_priority_domains:
            email.priority = EmailPriority.HIGH
        return email

    def _apply_processing_rules(self, email: EmailRecord) -> EmailRecord:
        return email
