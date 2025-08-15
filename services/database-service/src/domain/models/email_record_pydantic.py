"""EmailRecord domain model.
Core domain entity representing an email message (legacy Pydantic style).
"""

from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .attachment import Attachment


class EmailStatus(Enum):
    """Email processing status."""

    RECEIVED = "received"
    PROCESSED = "processed"
    FAILED = "failed"
    ARCHIVED = "archived"


class EmailPriority(Enum):
    """Email priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class EmailRecord(BaseModel):
    """Domain model for email records (legacy Pydantic variant)."""

    message_id: str
    subject: str
    sender: str
    recipients: list[str]
    sent_date: datetime

    cc_recipients: list[str] = Field(default_factory=list)
    bcc_recipients: list[str] = Field(default_factory=list)
    body_text: str = ""
    body_html: str = ""
    priority: EmailPriority = EmailPriority.NORMAL
    status: EmailStatus = EmailStatus.RECEIVED
    attachments: list[Attachment] = Field(default_factory=list)
    received_date: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    id: UUID = Field(default_factory=uuid4)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        use_enum_values=True,
    )

    @field_validator("message_id")
    @classmethod
    def validate_message_id(cls, v: str) -> str:
        if not v:
            raise ValueError("Message ID cannot be empty")
        return v

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, v: str) -> str:
        if not v:
            raise ValueError("Subject cannot be empty")
        return v

    @field_validator("sender")
    @classmethod
    def validate_sender(cls, v: str) -> str:
        if not v:
            raise ValueError("Sender cannot be empty")
        return v

    @field_validator("recipients")
    @classmethod
    def validate_recipients(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("At least one recipient is required")
        return v

    @property
    def has_attachments(self) -> bool:
        return len(self.attachments) > 0

    @property
    def attachment_count(self) -> int:
        return len(self.attachments)

    @property
    def is_high_priority(self) -> bool:
        return self.priority in [EmailPriority.HIGH, EmailPriority.URGENT]

    def add_attachment(self, attachment: Attachment) -> None:
        if attachment not in self.attachments:
            self.attachments.append(attachment)

    def remove_attachment(self, attachment: Attachment) -> None:
        if attachment in self.attachments:
            self.attachments.remove(attachment)

    def mark_as_processed(self) -> None:
        self.status = EmailStatus.PROCESSED

    def mark_as_failed(self) -> None:
        self.status = EmailStatus.FAILED

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "message_id": self.message_id,
            "subject": self.subject,
            "sender": self.sender,
            "recipients": self.recipients,
            "cc_recipients": self.cc_recipients,
            "bcc_recipients": self.bcc_recipients,
            "body_text": self.body_text,
            "body_html": self.body_html,
            "sent_date": self.sent_date.isoformat(),
            "received_date": self.received_date.isoformat(),
            "priority": self.priority.value,
            "status": self.status.value,
            "attachments": [att.to_dict() for att in self.attachments],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EmailRecord":
        email_data = data.copy()
        email_data["id"] = UUID(email_data["id"])
        email_data["sent_date"] = datetime.fromisoformat(
            email_data["sent_date"]
        )
        email_data["received_date"] = datetime.fromisoformat(
            email_data["received_date"]
        )
        email_data["priority"] = EmailPriority(email_data["priority"])
        email_data["status"] = EmailStatus(email_data["status"])
        email_data["attachments"] = [
            Attachment.from_dict(att_data)
            for att_data in email_data.get("attachments", [])
        ]
        return cls(**email_data)

    def __eq__(self, other: object) -> bool:  # pragma: no cover
        return isinstance(other, EmailRecord) and self.id == other.id

    def __repr__(self) -> str:  # pragma: no cover
        return (
            "EmailRecord(id="
            f"{self.id}, message_id='{self.message_id}', "
            f"subject='{self.subject}')"
        )
