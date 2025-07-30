"""
EmailRecord domain model.
Core domain entity representing an email message.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, validator

from .attachment import Attachment


class EmailStatus(Enum):
    """Email processing status"""
    RECEIVED = "received"
    PROCESSED = "processed"
    FAILED = "failed"
    ARCHIVED = "archived"


class EmailPriority(Enum):
    """Email priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class EmailRecord(BaseModel):
    """Domain model for email records"""
    
    # Required fields
    message_id: str
    subject: str
    sender: str
    recipients: List[str]
    sent_date: datetime
    
    # Optional fields with defaults
    cc_recipients: List[str] = Field(default_factory=list)
    bcc_recipients: List[str] = Field(default_factory=list)
    body_text: str = ""
    body_html: str = ""
    priority: EmailPriority = EmailPriority.NORMAL
    status: EmailStatus = EmailStatus.RECEIVED
    attachments: List[Attachment] = Field(default_factory=list)
    received_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    id: UUID = Field(default_factory=uuid4)
    
    class Config:
        # Allow arbitrary types for UUID
        arbitrary_types_allowed = True
        # Use enum values for serialization
        use_enum_values = True
    
    @validator('message_id')
    def validate_message_id(cls, v):
        if not v:
            raise ValueError("Message ID cannot be empty")
        return v
    
    @validator('subject')
    def validate_subject(cls, v):
        if not v:
            raise ValueError("Subject cannot be empty")
        return v
    
    @validator('sender')
    def validate_sender(cls, v):
        if not v:
            raise ValueError("Sender cannot be empty")
        return v
    
    @validator('recipients')
    def validate_recipients(cls, v):
        if not v:
            raise ValueError("At least one recipient is required")
        return v
    
    @property
    def has_attachments(self) -> bool:
        """Check if email has attachments"""
        return len(self.attachments) > 0
    
    @property
    def attachment_count(self) -> int:
        """Get number of attachments"""
        return len(self.attachments)
    
    @property
    def is_high_priority(self) -> bool:
        """Check if email is high priority"""
        return self.priority in [EmailPriority.HIGH, EmailPriority.URGENT]
    
    def add_attachment(self, attachment: Attachment) -> None:
        """Add an attachment to the email"""
        if attachment not in self.attachments:
            self.attachments.append(attachment)
    
    def remove_attachment(self, attachment: Attachment) -> None:
        """Remove an attachment from the email"""
        if attachment in self.attachments:
            self.attachments.remove(attachment)
    
    def mark_as_processed(self) -> None:
        """Mark email as processed"""
        self.status = EmailStatus.PROCESSED
    
    def mark_as_failed(self) -> None:
        """Mark email as failed"""
        self.status = EmailStatus.FAILED
    
    def to_dict(self) -> dict:
        """Convert email record to dictionary"""
        return {
            'id': str(self.id),
            'message_id': self.message_id,
            'subject': self.subject,
            'sender': self.sender,
            'recipients': self.recipients,
            'cc_recipients': self.cc_recipients,
            'bcc_recipients': self.bcc_recipients,
            'body_text': self.body_text,
            'body_html': self.body_html,
            'sent_date': self.sent_date.isoformat(),
            'received_date': self.received_date.isoformat(),
            'priority': self.priority.value,
            'status': self.status.value,
            'attachments': [att.to_dict() for att in self.attachments]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'EmailRecord':
        """Create email record from dictionary"""
        email_data = data.copy()
        email_data['id'] = UUID(email_data['id'])
        email_data['sent_date'] = datetime.fromisoformat(
            email_data['sent_date']
        )
        email_data['received_date'] = datetime.fromisoformat(
            email_data['received_date']
        )
        email_data['priority'] = EmailPriority(email_data['priority'])
        email_data['status'] = EmailStatus(email_data['status'])
        email_data['attachments'] = [
            Attachment.from_dict(att_data)
            for att_data in email_data.get('attachments', [])
        ]
        return cls(**email_data)
    
    def __eq__(self, other) -> bool:
        """Check equality based on ID"""
        if not isinstance(other, EmailRecord):
            return False
        return self.id == other.id
    
    def __repr__(self) -> str:
        return (f"EmailRecord(id={self.id}, message_id='{self.message_id}', "
                f"subject='{self.subject}')")
