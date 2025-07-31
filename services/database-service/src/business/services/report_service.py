"""
Report Business Service.
Handles report generation workflows and business rules.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

from ...domain.models.email_record import EmailRecord, EmailStatus
from ...domain.models.user import User
from ...domain.models.report import Report, ReportType, ReportStatus
from ...domain.repositories.email_repository_interface import EmailRepositoryInterface
from ...infrastructure.persistence.database import DatabaseConnection


from typing import Optional
from datetime import datetime, timezone
from typing import List


class ReportService:
        """
    Report business service handling report generation workflows.
    Coordinates report creation, processing, and completion.
    """

    def __init__(self,
                 email_repository: EmailRepositoryInterface,
                 db_connection: DatabaseConnection,
                 logger: Optional[logging.Logger] = None):
            self._email_repository = email_repository
        self._db_connection = db_connection
        self._logger = logger or logging.getLogger(__name__)

        async def create_email_summary_report(self,
                                        created_by: User,
                                        title: str,
                                        description: str = "",
                                        email_criteria: Optional[Dict[str, Any]] = None) -> Report:
            """
        Create a new email summary report.

        Args:
            created_by: User creating the report
            title: Report title
            description: Report description
            email_criteria: Optional criteria for filtering emails

        Returns:
            Report: The created report
        """
        self._logger.info(f"Creating email summary report: {title}")

            # Get emails based on criteria
        emails = await self._get_emails_by_criteria(email_criteria or {})

            # Create report
        report = Report(
            title=title,
            description=description,
            report_type=ReportType.DAILY,  # Default type
            status=ReportStatus.PENDING,
            created_by=created_by,
            email_records=emails,
            file_path=None,
            completed_at=None,
            created_at=datetime.now()
            )

            self._logger.info(f"Created report with {len(emails)} emails")
            return report

    async def generate_report(self, report: Report) -> Report:
            """
        Generate the actual report content.

        Args:
            report: Report to generate

        Returns:
            Report: Updated report with generated content
        """
        self._logger.info(f"Generating report: {report.id}")

            if report.status != ReportStatus.PENDING:
            raise ValueError(f"Report {report.id} is not in PENDING status")

            # Mark as processing
        report.start_processing()

            try:
            # Generate report content based on type
            if report.report_type == ReportType.DAILY:
                content = await self._generate_daily_summary(report.email_records)
                elif report.report_type == ReportType.WEEKLY:
                content = await self._generate_weekly_summary(report.email_records)
                elif report.report_type == ReportType.MONTHLY:
                content = await self._generate_monthly_summary(report.email_records)
                else:
                content = await self._generate_custom_summary(report.email_records)

                # In a real system, we would write content to file
            # For now, we'll simulate file generation
            file_path = f"/reports/{report.id}_{report.report_type.value}_summary.html"

            # Mark as completed
            report.mark_as_completed(file_path)

                self._logger.info(f"Successfully generated report: {report.id}")

            except Exception:
            self._logger.error(f"Failed to generate report {report.id}: {e}")
                report.mark_as_failed()
                raise

        return report

    async def get_report_statistics(self, report: Report) -> Dict[str, Any]:
            """
        Generate statistics for a report.

        Args:
            report: Report to analyze

        Returns:
            Dictionary containing report statistics
        """
        stats = {
            "total_emails": len(report.email_records),
                "by_status": {},
            "by_priority": {},
            "by_sender": {},
            "date_range": {
                "earliest": None,
                "latest": None
            }
        }

        if not report.email_records:
            return stats

        # Count by status
        for email in report.email_records:
            status = email.status.value
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            # Count by priority
        for email in report.email_records:
            priority = email.priority.value
            stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1

            # Count by sender (top 10)
            sender_counts = {}
        for email in report.email_records:
            sender = email.sender
            sender_counts[sender] = sender_counts.get(sender, 0) + 1

            # Get top 10 senders
        top_senders = (
            sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            )
            stats["by_sender"] = dict(top_senders)

            # Date range
        dates = [email.received_date for email in report.email_records]
        stats["date_range"]["earliest"] = min(dates)
            stats["date_range"]["latest"] = max(dates)

            return stats

    async def _get_emails_by_criteria(self, criteria: Dict[str, Any]) -> List[EmailRecord]:
            """Get emails based on filtering criteria."""
        self._logger.debug(f"Filtering emails with criteria: {criteria}")

            # Default: get all emails
        if not criteria:
            return await self._email_repository.find_all(limit=1000)  # Reasonable limit

            emails = []

        # Filter by sender
        if "sender" in criteria:
            sender_emails = (
                await self._email_repository.find_by_sender(criteria["sender"])
                )
                emails.extend(sender_emails)

            # Filter by status
        elif "status" in criteria:
            status = EmailStatus(criteria["status"])
                status_emails = await self._email_repository.find_by_status(status)
                emails.extend(status_emails)

            # Filter by date range
        elif "start_date" in criteria and "end_date" in criteria:
            date_emails = await self._email_repository.find_by_date_range(
                criteria["start_date"], criteria["end_date"]
            )
                emails.extend(date_emails)

            else:
            # No specific criteria, get recent emails
            emails = await self._email_repository.find_all(limit=100)

            return emails

    async def _generate_daily_summary(self, emails: List[EmailRecord]) -> str:
            """Generate daily summary content."""
        self._logger.debug("Generating daily summary")

            # This would generate actual HTML/PDF content
        # For now, return a simple summary
        return f"Daily Summary: {len(emails)} emails processed"

        async def _generate_weekly_summary(self, emails: List[EmailRecord]) -> str:
            """Generate weekly summary content."""
        self._logger.debug("Generating weekly summary")
            return f"Weekly Summary: {len(emails)} emails processed"

        async def _generate_monthly_summary(self, emails: List[EmailRecord]) -> str:
            """Generate monthly summary content."""
        self._logger.debug("Generating monthly summary")
            return f"Monthly Summary: {len(emails)} emails processed"

        async def _generate_custom_summary(self, emails: List[EmailRecord]) -> str:
            """Generate custom summary content."""
        self._logger.debug("Generating custom summary")
            return f"Custom Summary: {len(emails)} emails processed"
