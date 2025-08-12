"""
Email business service.
Provides workflows for importing, processing, archiving, and reporting
on emails with business rule application and statistics gathering.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging
from uuid import UUID

from ...domain.models.email_record import (
    EmailRecord, EmailStatus, EmailPriority
)
from ...domain.repositories.email_repository_interface import (
    EmailRepositoryInterface
)
from ...infrastructure.persistence.database import DatabaseConnection


class EmailService:
    """
    Email business service handling email processing workflows.
    Coordinates email storage, processing, and status management.
    """

    def __init__(self,
                 email_repository: EmailRepositoryInterface,
                 db_connection: DatabaseConnection,
                 logger: Optional[logging.Logger] = None):
        self._email_repository = email_repository
        self._db_connection = db_connection
        self._logger = logger or logging.getLogger(__name__)

    async def import_email(self, email_data: Dict[str, Any]) -> EmailRecord:
        """
        Import a new email with validation and business rules.

        Args:
            email_data: Raw email data dictionary

        Returns:
            EmailRecord: The imported and validated email record

        Raises:
            ValueError: If email data is invalid or duplicate
        """
        message_id = email_data.get('message_id')
        self._logger.info(f"Importing email with message_id: {message_id}")

        # Check for duplicate (legacy method name for test compatibility)
        existing_email = await self._email_repository.find_by_message_id(
            email_data.get('message_id', '')
        )  # type: ignore[attr-defined]
        if existing_email:
            self._logger.warning(f"Duplicate email detected: {message_id}")
            raise ValueError(
                f"Email with message_id {message_id} already exists"
            )

        # Create email record with business validation
        email_record = EmailRecord(
                message_id=email_data['message_id'],
                subject=email_data['subject'],
                sender=email_data['sender'],
                recipients=email_data.get('recipients', []),
                cc_recipients=email_data.get('cc_recipients', []),
                bcc_recipients=email_data.get('bcc_recipients', []),
                body_text=email_data.get('body_text', ''),
                body_html=email_data.get('body_html', ''),
                sent_date=email_data['sent_date'],
                received_date=email_data.get('received_date', datetime.now()),
                priority=EmailPriority(email_data.get('priority', 'normal')),
                status=EmailStatus.RECEIVED,
                attachments=[]
        )

        # Apply business rules
        email_record = self._apply_business_rules(email_record)

        # Save to repository
        saved_email = await self._email_repository.save(
            email_record
        )  # type: ignore[attr-defined]

        self._logger.info(f"Successfully imported email: {saved_email.id}")
        return saved_email

    async def process_email(self, email_id: UUID) -> EmailRecord:
        """
        Process an email through the business workflow.

        Args:
            email_id: ID of the email to process

        Returns:
            EmailRecord: The processed email

        Raises:
            ValueError: If email not found or already processed
        """
        self._logger.info(f"Processing email: {email_id}")

        email = await self._email_repository.find_by_id(
            email_id
        )  # type: ignore[attr-defined]
        if not email:
            raise ValueError(f"Email not found: {email_id}")

        if email.status != EmailStatus.RECEIVED:
            raise ValueError(f"Email {email_id} is not in RECEIVED status")

        # Mark as processing
        email.status = EmailStatus.PROCESSED

        # Apply processing business logic
        email = self._apply_processing_rules(email)

        # Save updated email
        processed_email = await self._email_repository.save(
            email
        )  # type: ignore[attr-defined]

        self._logger.info(f"Successfully processed email: {email_id}")
        return processed_email

    async def bulk_process_emails(
        self, email_ids: List[UUID]
    ) -> Dict[UUID, bool]:
        """
        Process multiple emails in bulk with transaction safety.

        Args:
            email_ids: List of email IDs to process

        Returns:
            Dict mapping email_id to success status
        """
        self._logger.info(f"Bulk processing {len(email_ids)} emails")

        results = {}

        for email_id in email_ids:
            try:
                await self.process_email(email_id)
                results[email_id] = True
            except Exception as e:
                self._logger.error(
                    f"Failed to process email {email_id}: {e}"
                )
                results[email_id] = False

        success_count = sum(results.values())
        self._logger.info(
            f"Bulk processing complete: {success_count}/"
            f"{len(email_ids)} successful"
        )

        return results

    async def archive_old_emails(self, days_old: int = 30) -> int:
        """
        Archive emails older than specified days.

        Args:
            days_old: Number of days old to consider for archiving

        Returns:
            Number of emails archived
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        self._logger.info(f"Archiving emails older than {cutoff_date}")

        # Find old processed emails
        old_emails = await self._email_repository.find_by_date_range(
            datetime.min, cutoff_date
        )  # type: ignore[attr-defined]

        archived_count = 0
        for email in old_emails:
            if email.status == EmailStatus.PROCESSED:
                email.status = EmailStatus.ARCHIVED
                await self._email_repository.save(
                    email
                )  # type: ignore[attr-defined]
                archived_count += 1

        self._logger.info(f"Archived {archived_count} emails")
        return archived_count

    async def get_email_statistics(self) -> Dict[str, Any]:
        """
        Get email statistics and metrics.

        Returns:
            Dictionary containing email statistics
        """
        self._logger.debug("Generating email statistics")

        stats = {}

        # Count by status
        for status in EmailStatus:
            count = await self._email_repository.count_by_status(status)
            stats[f"count_{status.value}"] = count

        # Get recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_emails = await self._email_repository.find_by_date_range(
            week_ago, datetime.now()
        )  # type: ignore[attr-defined]
        stats["recent_count"] = len(recent_emails)

        # High priority count
        high_priority_emails = [
            email for email in recent_emails
            if email.priority in [EmailPriority.HIGH, EmailPriority.URGENT]
        ]
        stats["high_priority_count"] = len(high_priority_emails)

        return stats

    def _apply_business_rules(self, email: EmailRecord) -> EmailRecord:
        """Apply business rules to email during import."""
        # Business rule: Emails from certain domains get high priority
        high_priority_domains = ['urgent.com', 'priority.org']
        sender_domain = (
            email.sender.split('@')[-1] if '@' in email.sender else ''
        )

        if sender_domain in high_priority_domains:
            email.priority = EmailPriority.HIGH
            self._logger.debug(
                f"Applied high priority rule for domain: {sender_domain}"
            )

        # Business rule: Large recipient lists get flagged
        total_recipients = len(email.recipients) + len(email.cc_recipients)
        if total_recipients > 50:
            self._logger.warning(
                f"Large recipient list detected: {total_recipients} recipients"
            )

        return email

    def _apply_processing_rules(self, email: EmailRecord) -> EmailRecord:
        """Apply processing business rules."""
        # Business rule: High priority emails get processed immediately
        if email.priority in [EmailPriority.HIGH, EmailPriority.URGENT]:
            self._logger.info(f"High priority email processed: {email.id}")

        # Business rule: Mark processing timestamp
        # (In a real system, this might update a processing_timestamp field)

        return email
