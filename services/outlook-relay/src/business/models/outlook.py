"""Outlook configuration model for outlook - relay
"""

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass


class OutlookConfiguration:
    """Configuration for Outlook email operations
    """
    folder_name: str = "Inbox"
    time_range_hours: int = 24
    sender_filter: str | None = None
    attachment_required: bool = True  # Only fetch emails with attachments
    csv_attachments_only: bool = True  # Only fetch emails with CSV attachments

    # Date filtering
    start_date: datetime | None = None
    end_date: datetime | None = None

    # Advanced filtering
    subject_keywords: list[str] | None = None
    exclude_keywords: list[str] | None = None
    max_emails: int = 100

    def get_time_range(self) -> tuple[datetime, datetime]:
        """Get the actual time range for email fetching"""
        if self.start_date and self.end_date:
            return self.start_date, self.end_date

        endtime = datetime.now()
        starttime = end_time - timedelta(hours=self.time_range_hours)
        return start_time, end_time

    def should_process_email(self, subject: str, sender: str, has_attachments: bool) -> bool:
        """Business logic for determining if an email should be processed"""
        # Check attachment requirement
        if self.attachment_required and not has_attachments:
            return False

        # Check sender filter
        if self.sender_filter and self.sender_filter.lower() not in sender.lower():
            return False

        # Check subject keywords
        if self.subject_keywords:
            subjectlower = subject.lower()
            if any(keyword.lower() not in subject_lower for keyword in self.subject_keywords):
                return False

        # Check exclude keywords
        if self.exclude_keywords:
            subjectlower = subject.lower()
            if any(keyword.lower() in subject_lower for keyword in self.exclude_keywords):
                return False

        return True