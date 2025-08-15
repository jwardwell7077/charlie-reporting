"""Report Business Service.
Handles report generation workflows and business rules.
"""

import logging
from datetime import datetime
from typing import Any

from ...domain.models.email_record import EmailRecord, EmailStatus
from ...domain.models.report import Report, ReportStatus, ReportType
from ...domain.models.user import User
from ...domain.repositories.email_repository_interface import (
    EmailRepositoryInterface,
)
from ...infrastructure.persistence.database import DatabaseConnection


class ReportService:
    """Report business service handling report generation workflows.

    Coordinates report creation, processing, and completion.
    """

    def __init__(
        self,
        email_repository: EmailRepositoryInterface,
        db_connection: DatabaseConnection,
        logger: logging.Logger | None = None,
    ):
        self._email_repository = email_repository
        self._db_connection = db_connection
        self._logger = logger or logging.getLogger(__name__)

    async def create_email_summary_report(
        self,
        created_by: User,
        title: str,
        description: str = "",
        email_criteria: dict[str, Any] | None = None,
        report_type: ReportType = ReportType.DAILY,
    ) -> Report:
        """Create a new email summary report."""
        self._logger.info("Creating email summary report: %s", title)

        emails = await self._get_emails_by_criteria(email_criteria or {})

        report = Report(
            title=title,
            description=description,
            report_type=report_type,
            status=ReportStatus.PENDING,
            created_by=created_by,
            email_records=emails,
            file_path=None,
            completed_at=None,
            created_at=datetime.now(),
        )
        self._logger.info("Created report with %d emails", len(emails))
        return report

    async def generate_report(self, report: Report) -> Report:
        """Generate the actual report content."""
        self._logger.info("Generating report: %s", report.id)

        if report.status != ReportStatus.PENDING:
            raise ValueError(f"Report {report.id} is not in PENDING status")

        report.start_processing()

        try:
            if report.report_type == ReportType.DAILY:
                content = await self._generate_daily_summary(
                    report.email_records
                )
            elif report.report_type == ReportType.WEEKLY:
                content = await self._generate_weekly_summary(
                    report.email_records
                )
            elif report.report_type == ReportType.MONTHLY:
                content = await self._generate_monthly_summary(
                    report.email_records
                )
            else:
                content = await self._generate_custom_summary(
                    report.email_records
                )

            file_path = (
                f"/reports/{report.id}_{report.report_type.value}_summary.html"
            )
            report.mark_as_completed(file_path)
            self._logger.info(
                "Generated report %s (content size %d)",
                report.id,
                len(content),
            )
        except Exception as e:  # noqa: BLE001
            self._logger.error(
                "Failed to generate report %s: %s", report.id, e, exc_info=True
            )
            report.mark_as_failed()
            raise

        return report

    async def get_report_statistics(self, report: Report) -> dict[str, Any]:
        """Generate statistics for a report."""
        stats: dict[str, Any] = {
            "total_emails": len(report.email_records),
            "by_status": {},
            "by_priority": {},
            "by_sender": {},
            "date_range": {"earliest": None, "latest": None},
        }

        if not report.email_records:
            return stats

        for email in report.email_records:
            status = email.status.value
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

        for email in report.email_records:
            priority = email.priority.value
            stats["by_priority"][priority] = (
                stats["by_priority"].get(priority, 0) + 1
            )

        sender_counts: dict[str, int] = {}
        for email in report.email_records:
            sender = email.sender
            sender_counts[sender] = sender_counts.get(sender, 0) + 1
        top_senders = sorted(
            sender_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]
        stats["by_sender"] = dict(top_senders)

        dates = [email.received_date for email in report.email_records]
        stats["date_range"]["earliest"] = min(dates)
        stats["date_range"]["latest"] = max(dates)
        return stats

    async def _get_emails_by_criteria(
        self, criteria: dict[str, Any]
    ) -> list[EmailRecord]:
        """Get emails based on filtering criteria."""
        self._logger.debug("Filtering emails with criteria: %s", criteria)

        if not criteria:
            return await self._email_repository.list_all()

        emails: list[EmailRecord] = []

        if "sender" in criteria:
            emails.extend(
                await self._email_repository.get_by_sender(
                    criteria["sender"]
                )
            )

        if "status" in criteria:
            try:
                status = EmailStatus(
                    criteria["status"]
                )  # type: ignore[arg-type]
                emails.extend(
                    await self._email_repository.get_by_status(status)
                )
            except ValueError:
                self._logger.warning(
                    "Invalid status in criteria: %s",
                    criteria["status"],
                )

        if "start_date" in criteria and "end_date" in criteria:
            emails.extend(
                await self._email_repository.get_by_date_range(
                    criteria["start_date"],
                    criteria["end_date"],
                )
            )

        # Fallback if no emails matched criteria
        if not emails:
            emails = await self._email_repository.list_all()
        return emails

    async def _generate_daily_summary(self, emails: list[EmailRecord]) -> str:
        self._logger.debug("Generating daily summary")
        return f"Daily Summary: {len(emails)} emails processed"

    async def _generate_weekly_summary(self, emails: list[EmailRecord]) -> str:
        self._logger.debug("Generating weekly summary")
        return f"Weekly Summary: {len(emails)} emails processed"

    async def _generate_monthly_summary(
        self, emails: list[EmailRecord]
    ) -> str:
        self._logger.debug("Generating monthly summary")
        return f"Monthly Summary: {len(emails)} emails processed"

    async def _generate_custom_summary(self, emails: list[EmailRecord]) -> str:
        self._logger.debug("Generating custom summary")
        return f"Custom Summary: {len(emails)} emails processed"
