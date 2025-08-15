"""Email domain model for outlook - relay
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass


class Email:
    """Email domain model representing a fetched email
    """

    subject: str
    sender: str
    received_time: datetime
    body: str
    attachments: list[str]
    id: str | None = None
    folder: str | None = None
    has_csv_attachments: bool = False
    email_type: str | None = None  # ACQ, QCBS, etc.

    def __post_init__(self):
        """Post - initialization processing"""
        if self.attachments:
            self.hascsv_attachments = any(
                str(att).lower().endswith('.csv') for att in self.attachments
            )

    def get_csv_attachments(self) -> list[str]:
        """Get only CSV attachments"""
        return [att for att in self.attachments if str(att).lower().endswith('.csv')]

    def extractemail_type(self) -> str | None:
        """Extract email type from subject or filename patterns"""
        subjectupper = self.subject.upper()

        # Common patterns in email subjects
        if 'ACQ' in subject_upper:
            return 'ACQ'
        elif 'QCBS' in subject_upper:
            return 'QCBS'
        elif 'DIAL' in subject_upper:
            return 'DIALS'
        elif 'PRODUCTIVITY' in subject_upper:
            return 'PRODUCTIVITY'
        elif 'IB_CALL' in subject_upper or 'IBCALL' in subject_upper:
            return 'IB_CALLS'
        elif 'RESC' in subject_upper:
            return 'RESC'
        elif 'CAMPAIGN' in subject_upper:
            return 'CAMPAIGN_INTERACTIONS'

        # Try to extract from attachment names
        for attachment in self.attachments:
            attupper = str(attachment).upper()
            if 'ACQ' in att_upper:
                return 'ACQ'
            elif 'QCBS' in att_upper:
                return 'QCBS'
            # Add more patterns as needed

        return None